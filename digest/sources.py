"""数据来源：RSS/Atom 订阅（免密钥）+ 可插拔搜索服务（Tavily / Brave / 免密钥的 HN Algolia）。

选择规则（SEARCH_PROVIDER 环境变量可强制指定）：
  TAVILY_API_KEY 存在 -> Tavily；否则 BRAVE_API_KEY 存在 -> Brave；否则 -> HN Algolia（免密钥）。
"""
from __future__ import annotations

import html
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Protocol

import feedparser

from . import http
from .models import Item

TAG_RE = re.compile(r"<[^>]+>")


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", s or ""))).strip()


def _ts(entry) -> datetime | None:
    for k in ("published_parsed", "updated_parsed"):
        if entry.get(k):
            return datetime(*entry[k][:6], tzinfo=timezone.utc)
    return None


def fetch_feed(cfg: dict) -> list[Item]:
    r = http.get(cfg["url"], check_robots=True, cache=False, timeout=20)
    if r is None:
        return []
    feed = feedparser.parse(r.content)
    items = []
    for e in feed.entries[: cfg.get("max_items", 30)]:
        snippet = strip_html(e.get("summary") or (e.get("content") or [{}])[0].get("value", ""))
        m = re.search(r"Points:\s*(\d+)", snippet)       # hnrss 在摘要中附带分数
        snippet = re.sub(r"Article URL:.*$", "", snippet).strip() if "hnrss" in cfg["url"] else snippet
        snippet = re.sub(r"^arXiv:\S+\s+Announce Type:\s*\w+\s*Abstract:\s*", "", snippet)  # arXiv 摘要前缀
        snippet = re.sub(r"点击查看原文\s*>?", "", snippet).strip()                           # InfoQ 占位文字
        pub = _ts(e)
        if pub and pub > datetime.now(timezone.utc):  # 个别源时区标注有误，未来时间按当前时间处理
            pub = datetime.now(timezone.utc)
        title = strip_html(e.get("title", ""))
        repo = cfg.get("repo") or (cfg["name"].split(":", 1)[1].strip() if cfg["name"].startswith("GitHub Releases:") else "")
        if repo and repo.lower() not in title.lower():  # GitHub Release 标题常只有版本号，补上项目名
            title = f"{repo} {title}"
        items.append(Item(title=title, url=e.get("link", ""), source=cfg["name"],
                          published=pub, snippet=snippet[:2000], lang=cfg.get("lang", "en"),
                          weight=cfg.get("weight", 1.0), fetch=cfg.get("fetch", True),
                          points=int(m.group(1)) if m else 0))
    return items


class SearchProvider(Protocol):
    name: str

    def search(self, query: str, hours: int, limit: int) -> list[Item]: ...


class TavilySearch:
    name = "Tavily"

    def __init__(self, key: str):
        self.key = key

    def search(self, query, hours, limit):
        data = http.post_json("https://api.tavily.com/search",
                              {"query": query, "topic": "news", "days": max(1, hours // 24),
                               "max_results": limit, "search_depth": "basic"},
                              headers={"Authorization": f"Bearer {self.key}"})
        out = []
        for r in data.get("results", []):
            pub = None
            if r.get("published_date"):
                try:
                    from email.utils import parsedate_to_datetime
                    pub = parsedate_to_datetime(r["published_date"])
                except Exception:
                    pub = None
            out.append(Item(title=r.get("title", ""), url=r["url"], source="Tavily 搜索", published=pub,
                            snippet=r.get("content", ""), content=r.get("raw_content") or ""))
        return out


class BraveSearch:
    name = "Brave Search"

    def __init__(self, key: str):
        self.key = key

    def search(self, query, hours, limit):
        fresh = "pd" if hours <= 24 else ("pw" if hours <= 24 * 7 else "pm")
        r = http._session.get("https://api.search.brave.com/res/v1/news/search",
                              params={"q": query, "count": limit, "freshness": fresh},
                              headers={"X-Subscription-Token": self.key, "Accept": "application/json"},
                              timeout=20)
        r.raise_for_status()
        out = []
        for x in r.json().get("results", []):
            pub = None
            if x.get("page_age"):
                try:
                    pub = datetime.fromisoformat(x["page_age"].replace("Z", "+00:00"))
                    pub = pub if pub.tzinfo else pub.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            out.append(Item(title=strip_html(x.get("title", "")), url=x["url"], source="Brave 搜索",
                            published=pub, snippet=strip_html(x.get("description", ""))))
        return out


class HNAlgoliaSearch:
    """免密钥搜索：Hacker News 官方合作的 Algolia 公共 API，按关键词搜索近期高分讨论。"""
    name = "HN Algolia（免密钥）"

    def __init__(self, min_points: int = 30):
        self.min_points = min_points

    def search(self, query, hours, limit):
        since = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
        # Algolia 是 API 而非网页，不适用 robots.txt；仍走统一限速
        r = http.get("https://hn.algolia.com/api/v1/search", check_robots=False, cache=False,
                     params={"query": query, "tags": "story", "hitsPerPage": limit,
                             "numericFilters": f"created_at_i>{since},points>{self.min_points}"})
        if r is None:
            return []
        out = []
        for h in r.json().get("hits", []):
            url = h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}"
            out.append(Item(title=h.get("title", ""), url=url, source="HN 搜索",
                            published=datetime.fromtimestamp(h["created_at_i"], timezone.utc),
                            points=h.get("points") or 0, snippet=strip_html(h.get("story_text") or "")))
        return out


def get_search_provider(min_points=30) -> SearchProvider:
    forced = os.getenv("SEARCH_PROVIDER", "").lower()
    if forced in ("", "tavily") and os.getenv("TAVILY_API_KEY"):
        return TavilySearch(os.environ["TAVILY_API_KEY"])
    if forced in ("", "brave") and os.getenv("BRAVE_API_KEY"):
        return BraveSearch(os.environ["BRAVE_API_KEY"])
    return HNAlgoliaSearch(min_points)
