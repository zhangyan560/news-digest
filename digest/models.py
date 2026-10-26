from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    title: str
    url: str
    source: str
    published: datetime | None = None
    snippet: str = ""          # feed/搜索结果自带的摘要
    content: str = ""          # 抓取到的正文
    lang: str = "en"
    weight: float = 1.0
    points: int = 0            # 热度（如 HN 分数）
    fetch: bool = True
    topics: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    summary: str = ""
    also_in: list[str] = field(default_factory=list)  # 去重合并后的其他来源
    score: float = 0.0
