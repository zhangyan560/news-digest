"""摘要：LLM（OpenAI 兼容接口，生成中文摘要）或免密钥的抽取式 TextRank 摘要。

LLM 模式需同时设置 LLM_BASE_URL / LLM_API_KEY / LLM_MODEL。
"""
from __future__ import annotations

import json
import logging
import os
import re

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from . import http
from .models import Item

log = logging.getLogger(__name__)
ZH = re.compile(r"[\u4e00-\u9fff]")


def is_zh(text: str) -> bool:
    return len(ZH.findall(text[:500])) > 20


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[。！？!?])\s*|(?<=[.;])\s+(?=[A-Z\"“(])", text)
    return [p.strip() for p in parts if 15 <= len(p.strip()) <= 400 and not looks_like_code(p)]


CODE_HINT = re.compile(r"(&&|\$ |git clone|pip install|npm |cargo |https?://|[{}<>=]{2,}|\w+\(\))")


def looks_like_code(s: str) -> bool:
    """过滤命令行、代码、链接等不适合作为摘要的句子。"""
    if CODE_HINT.search(s):
        return True
    letters = len(re.findall(r"[A-Za-z\u4e00-\u9fff\s,，。.;；:：'’\"“”!?！？()（）\-]", s))
    return letters / max(len(s), 1) < 0.85


def textrank(sentences: list[str], k: int = 2, lead_bias: float = 0.15) -> list[str]:
    """TextRank：句子相似度图上做 PageRank，叠加新闻"导语优先"的位置先验，按原顺序输出。"""
    if len(sentences) <= k:
        return sentences
    X = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3)).fit_transform(sentences)
    S = (X @ X.T).toarray()
    np.fill_diagonal(S, 0)
    row = S.sum(1, keepdims=True)
    M = np.divide(S, row, out=np.zeros_like(S), where=row > 0)
    n = len(sentences)
    prior = np.array([1 / (i + 1) for i in range(n)])
    prior /= prior.sum()
    r = np.full(n, 1 / n)
    for _ in range(50):
        r = (1 - 0.85) * ((1 - lead_bias) / n + lead_bias * prior) + 0.85 * M.T @ r
    top = sorted(np.argsort(-r)[:k])
    return [sentences[i] for i in top]


def keywords(text: str, k: int = 4) -> list[str]:
    if is_zh(text):
        import jieba.analyse
        return jieba.analyse.extract_tags(text, topK=k)
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-\+\.]{2,}", text)
    freq: dict[str, int] = {}
    for w in words:
        lw = w.lower().strip(".")
        if lw in ENGLISH_STOP_WORDS or len(lw) < 3:
            continue
        freq[w.strip(".")] = freq.get(w.strip("."), 0) + (3 if w[0].isupper() else 1)
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]


class ExtractiveSummarizer:
    name = "抽取式 TextRank（免密钥）"
    lang_note = "摘要为原文摘录，英文来源保留英文"

    def summarize(self, topic: str, items: list[Item]) -> None:
        for it in items:
            text = it.content or it.snippet or it.title
            sents = split_sentences(text)
            limit = 160 if is_zh(text) else 320
            picked = textrank(sents, k=2) if sents else [text[:limit]]
            s = " ".join(picked)
            it.summary = s if len(s) <= limit else s[:limit].rsplit(" ", 1)[0] + "…"
            it.keywords = keywords(it.title + "。" + text[:3000])

    def overview(self, sections: dict[str, list[Item]]) -> list[str]:
        out = []
        for topic, items in sections.items():
            if items:
                out.append(f"**{topic}**：{items[0].title}")
        return out


class LLMSummarizer:
    name = "LLM（OpenAI 兼容接口）"
    lang_note = "摘要由大模型生成中文"

    def __init__(self):
        self.base = os.environ["LLM_BASE_URL"].rstrip("/")
        self.key, self.model = os.environ["LLM_API_KEY"], os.environ["LLM_MODEL"]
        self.fallback = ExtractiveSummarizer()

    def _chat(self, system: str, user: str) -> str:
        data = http.post_json(f"{self.base}/chat/completions",
                              {"model": self.model, "temperature": 0.2,
                               "messages": [{"role": "system", "content": system},
                                            {"role": "user", "content": user}]},
                              headers={"Authorization": f"Bearer {self.key}"}, timeout=90)
        return data["choices"][0]["message"]["content"]

    def summarize(self, topic: str, items: list[Item]) -> None:
        payload = [{"id": i, "title": it.title, "source": it.source,
                    "text": (it.content or it.snippet)[:2500]} for i, it in enumerate(items)]
        system = ("你是科技资讯编辑。为每条资讯写中文摘要：两句话、不超过八十字，客观陈述事实，不加评论，不编造原文没有的信息；"
                  "再给出三个中文或英文关键词。只输出 JSON 数组：[{\"id\":0,\"summary\":\"...\",\"keywords\":[\"...\"]}]")
        try:
            raw = self._chat(system, f"主题：{topic}\n资讯：{json.dumps(payload, ensure_ascii=False)}")
            raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.M)
            for r in json.loads(raw):
                it = items[int(r["id"])]
                it.summary, it.keywords = r["summary"], r.get("keywords", [])[:4]
        except Exception as e:  # 失败时逐条降级，保证日报照常生成
            log.warning("LLM 摘要失败，降级为抽取式：%s", e)
        self.fallback.summarize(topic, [it for it in items if not it.summary])

    def overview(self, sections: dict[str, list[Item]]) -> list[str]:
        lines = [f"[{t}] {it.title}：{it.summary}" for t, its in sections.items() for it in its[:3]]
        try:
            raw = self._chat("你是科技资讯主编。根据给定资讯写三到五条中文「今日要点」，每条一句话，只输出列表，每行以 - 开头。",
                             "\n".join(lines))
            return [l.lstrip("-• ").strip() for l in raw.splitlines() if l.strip()][:5]
        except Exception as e:
            log.warning("LLM 要点生成失败：%s", e)
            return self.fallback.overview(sections)


def get_summarizer():
    if all(os.getenv(k) for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")):
        return LLMSummarizer()
    return ExtractiveSummarizer()
