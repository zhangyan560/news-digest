"""正文抓取：Firecrawl（需 FIRECRAWL_API_KEY）或本地 requests + trafilatura（免密钥，遵守 robots.txt）。"""
from __future__ import annotations

import os
from typing import Protocol

import trafilatura

from . import http


class Fetcher(Protocol):
    name: str

    def fetch(self, url: str) -> str: ...


class FirecrawlFetcher:
    name = "Firecrawl"

    def __init__(self, key: str, base: str | None = None):
        # FIRECRAWL_API_URL 可指向自托管实例，默认官方云服务
        self.key = key
        self.base = (base or os.getenv("FIRECRAWL_API_URL") or "https://api.firecrawl.dev").rstrip("/")

    def fetch(self, url):
        data = http.post_json(f"{self.base}/v2/scrape",
                              {"url": url, "formats": ["markdown"], "onlyMainContent": True, "timeout": 30000},
                              headers={"Authorization": f"Bearer {self.key}"}, timeout=45)
        return (data.get("data") or {}).get("markdown", "")[:20000]


class LocalFetcher:
    """requests 获取 + trafilatura 正文抽取；robots.txt 不允许时直接跳过。"""
    name = "本地抓取（requests + trafilatura）"

    def fetch(self, url):
        if url.lower().endswith(".pdf"):
            return ""
        r = http.get(url, check_robots=True)
        if r is None or "html" not in r.headers.get("Content-Type", "text/html"):
            return ""
        text = trafilatura.extract(r.text, include_comments=False, include_tables=False,
                                   favor_precision=True, url=url) or ""
        return text[:20000]


def get_fetcher() -> Fetcher:
    if os.getenv("FIRECRAWL_API_KEY"):
        return FirecrawlFetcher(os.environ["FIRECRAWL_API_KEY"])
    return LocalFetcher()
