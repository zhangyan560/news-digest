"""主流程：采集 → 时间过滤 → 去重 → 打标签 → 排序 → 抓正文 → 摘要 → 渲染。"""
from __future__ import annotations

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from . import http
from .dedupe import dedupe
from .fetchers import get_fetcher
from .models import Item
from .render import TZ, to_html, to_markdown
from .sources import fetch_feed, get_search_provider
from .summarize import get_summarizer
from .tagging import Tagger

log = logging.getLogger(__name__)


def load_config(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def score(it: Item, now: datetime) -> float:
    age_h = (now - it.published).total_seconds() / 3600 if it.published else 24
    recency = math.exp(-max(age_h, 0) / 36)
    heat = 1 + math.log1p(it.points) / 3
    return it.weight * heat * (0.4 + recency) * (1 + 0.25 * len(it.also_in))


def collect(cfg: dict, hours: int) -> tuple[list[Item], str]:
    items: list[Item] = []
    with ThreadPoolExecutor(6) as ex:
        for res in ex.map(fetch_feed, cfg.get("feeds", [])):
            items += res
    sc = cfg.get("search", {})
    provider = get_search_provider(sc.get("hn_min_points", 30))
    for t in cfg["topics"]:
        qs = t.get("queries") or [t["name"]]
        per = max(3, sc.get("max_results_per_topic", 8) // len(qs) + 1)
        for q in qs:
            try:
                items += provider.search(q, hours, per)
            except Exception as e:
                log.warning("搜索失败 %s：%s", q, e)
    return items, provider.name


def run(cfg: dict, hours: int | None = None, topics: list[str] | None = None, progress=None) -> dict:
    note = progress or (lambda msg: log.info(msg))
    hours = hours or cfg.get("hours", 48)
    if topics:
        cfg = {**cfg, "topics": [t for t in cfg["topics"] if t["name"] in topics]}
    http.robots_blocked.clear()
    now = datetime.now(timezone.utc)

    note("采集 RSS 与搜索结果…")
    raw, search_name = collect(cfg, hours)
    cutoff = now - timedelta(hours=hours)
    fresh = [it for it in raw if it.published is None or it.published >= cutoff]
    uniq = dedupe(fresh)
    note(f"采集 {len(raw)} 条，时间窗口内 {len(fresh)} 条，去重后 {len(uniq)} 条")

    tagger = Tagger(cfg["topics"])
    for it in uniq:
        it.topics = [n for n, _ in tagger.tag(it)]
        it.score = score(it, now)
    if not cfg.get("drop_unmatched", True):
        for it in uniq:
            it.topics = it.topics or ["其他"]

    # 每条只放在其最相关的主题下，避免重复；其余主题作为标签展示
    cap = cfg.get("max_items_per_topic", 6)
    names = [t["name"] for t in cfg["topics"]] + ([] if cfg.get("drop_unmatched", True) else ["其他"])
    sections: dict[str, list[Item]] = {n: [] for n in names}
    for it in sorted(uniq, key=lambda x: -x.score):
        if it.topics and len(sections[it.topics[0]]) < cap:
            sections[it.topics[0]].append(it)
    selected = [it for v in sections.values() for it in v]

    fetcher = get_fetcher()
    if cfg.get("fetch_full_text", True):
        todo = [it for it in selected if it.fetch and not it.content]
        note(f"抓取正文 {len(todo)} 篇（{fetcher.name}，遵守 robots.txt 与限速）…")

        def _f(it: Item):
            try:
                it.content = fetcher.fetch(it.url)
            except Exception as e:
                log.warning("抓取失败 %s：%s", it.url, e)

        with ThreadPoolExecutor(6) as ex:
            list(ex.map(_f, todo))

    summarizer = get_summarizer()
    note(f"生成摘要（{summarizer.name}）…")
    for topic, its in sections.items():
        if its:
            summarizer.summarize(topic, its)
    now_local = now.astimezone(TZ)
    return {
        "title": cfg.get("title", "资讯日报"), "date": now_local.strftime("%Y-%m-%d"),
        "generated": now_local.strftime("%Y-%m-%d %H:%M"), "hours": hours,
        "stats": {"collected": len(raw), "unique": len(uniq), "selected": len(selected),
                  "robots_blocked": len(http.robots_blocked)},
        "modes": {"search": search_name, "fetcher": fetcher.name, "summarizer": summarizer.name,
                  "lang_note": summarizer.lang_note},
        "overview": summarizer.overview(sections), "sections": sections,
    }


def write(d: dict, out_dir: str | Path, stem: str | None = None) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = stem or f"digest-{d['date']}"
    md, html = out / f"{stem}.md", out / f"{stem}.html"
    md.write_text(to_markdown(d), encoding="utf-8")
    html.write_text(to_html(d), encoding="utf-8")
    return md, html
