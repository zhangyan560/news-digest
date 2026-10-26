"""主题打标签：关键词规则（标题权重更高）+ 来源加分，支持一条资讯属于多个主题。"""
from __future__ import annotations

import re

from .models import Item


def _pattern(kw: str) -> re.Pattern:
    kw = kw.strip().lower()
    prefix = kw.endswith("*")
    kw = kw.rstrip("*")
    if re.search(r"[\u4e00-\u9fff]", kw):
        return re.compile(re.escape(kw))
    tail = "" if prefix else r"(?![a-z0-9])"
    return re.compile(r"(?<![a-z0-9])" + re.escape(kw) + tail)


class Tagger:
    def __init__(self, topics: list[dict]):
        self.topics = [(t["name"], [_pattern(k) for k in t.get("keywords", [])], t.get("sources", []))
                       for t in topics]

    def tag(self, it: Item) -> list[tuple[str, float]]:
        title, body = it.title.lower(), (it.snippet + " " + it.content[:1500]).lower()
        res = []
        for name, pats, srcs in self.topics:
            s = sum(2.0 for p in pats if p.search(title)) + sum(0.5 for p in pats if p.search(body))
            if any(x.lower() in it.source.lower() for x in srcs):
                s += 3.0
            if s >= 1.0:
                res.append((name, s))
        return sorted(res, key=lambda x: -x[1])
