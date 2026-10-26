"""去重：URL 规范化 + 标题相似度（字符 n-gram TF-IDF 余弦）。"""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .models import Item

TRACKING = re.compile(r"^(utm_|ref$|ref_src$|fbclid$|gclid$|spm$|from$|source$)")


def normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    host = p.netloc.lower().removeprefix("www.").removeprefix("m.")
    q = urlencode(sorted((k, v) for k, v in parse_qsl(p.query) if not TRACKING.match(k.lower())))
    path = re.sub(r"/+$", "", p.path) or "/"
    if host == "arxiv.org":  # arxiv abs/pdf/版本号 统一
        path = re.sub(r"^/(pdf|abs)/([\d.]+)(v\d+)?(\.pdf)?$", r"/abs/\2", path)
    return urlunparse(("https", host, path, "", q, ""))


def _rank_key(it: Item):
    return (it.weight, it.points, len(it.content) + len(it.snippet))


def dedupe(items: list[Item], title_threshold: float = 0.8) -> list[Item]:
    by_url: dict[str, Item] = {}
    for it in items:
        if not it.title or not it.url:
            continue
        k = normalize_url(it.url)
        if k in by_url:
            keep, drop = sorted([by_url[k], it], key=_rank_key, reverse=True)
            keep.also_in = sorted(set(keep.also_in + drop.also_in + [drop.source]) - {keep.source})
            keep.points = max(keep.points, drop.points)
            by_url[k] = keep
        else:
            by_url[k] = it
    uniq = list(by_url.values())
    if len(uniq) < 2:
        return uniq
    titles = [re.sub(r"\s+", " ", u.title.lower()) for u in uniq]
    X = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)).fit_transform(titles)
    sim = (X @ X.T).toarray()
    np.fill_diagonal(sim, 0)
    removed = set()
    order = sorted(range(len(uniq)), key=lambda i: _rank_key(uniq[i]), reverse=True)
    for i in order:
        if i in removed:
            continue
        for j in np.where(sim[i] >= title_threshold)[0]:
            if j not in removed and j != i:
                removed.add(j)
                uniq[i].also_in = sorted(set(uniq[i].also_in + [uniq[j].source]) - {uniq[i].source})
    return [u for k, u in enumerate(uniq) if k not in removed]
