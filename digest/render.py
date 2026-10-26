"""输出：Markdown 与独立的 HTML 页面（内联样式，无外部依赖）。"""
from __future__ import annotations

import html
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def fmt_time(dt: datetime | None) -> str:
    return dt.astimezone(TZ).strftime("%m-%d %H:%M") if dt else "时间未知"


def to_markdown(d: dict) -> str:
    L = [f"# {d['title']} · {d['date']}", "",
         f"> 生成于 {d['generated']}（北京时间）· 时间窗口：最近 {d['hours']} 小时 · "
         f"采集 {d['stats']['collected']} 条 → 去重后 {d['stats']['unique']} 条 → 入选 {d['stats']['selected']} 条",
         f"> 搜索：{d['modes']['search']} · 抓取：{d['modes']['fetcher']} · 摘要：{d['modes']['summarizer']}（{d['modes']['lang_note']}）",
         "", "## 今日概览", ""]
    L += [f"- {x}" for x in d["overview"]] + [""]
    for topic, items in d["sections"].items():
        if not items:
            continue
        L += [f"## {topic}（{len(items)}）", ""]
        for n, it in enumerate(items, 1):
            meta = [it.source, fmt_time(it.published)]
            if it.points:
                meta.append(f"HN {it.points} 分")
            if it.also_in:
                meta.append("同见：" + "、".join(it.also_in))
            L.append(f"### {n}. [{it.title}]({it.url})")
            L.append(f"<sub>{' · '.join(meta)}</sub>")
            L.append("")
            L.append(it.summary)
            tags = [t for t in it.topics[1:]] + it.keywords
            if tags:
                L.append("")
                L.append(" ".join(f"`{t}`" for t in tags[:6]))
            L.append("")
    L += ["---", f"本日报由 [news-digest](https://github.com/zhangyan560/news-digest) 自动生成；"
          "版权归原作者所有，摘要仅供索引，请点击原文阅读全文。"]
    return "\n".join(L)


CSS = """
body{font-family:-apple-system,"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:860px;margin:32px auto;padding:0 20px;color:#1f2937;background:#f8fafc;line-height:1.65}
h1{font-size:28px;margin-bottom:4px}.meta{color:#64748b;font-size:13px}
.overview{background:#eef2ff;border-radius:10px;padding:12px 20px;margin:18px 0}
h2{border-left:4px solid #6366f1;padding-left:10px;margin-top:34px;font-size:20px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px 18px;margin:12px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card a{color:#1d4ed8;text-decoration:none;font-weight:600;font-size:16px}.card a:hover{text-decoration:underline}
.card .src{color:#64748b;font-size:12px;margin:4px 0 8px}.card p{margin:0;font-size:14px}
.tag{display:inline-block;background:#f1f5f9;color:#475569;border-radius:999px;padding:1px 10px;font-size:12px;margin:8px 6px 0 0}
footer{color:#94a3b8;font-size:12px;margin:40px 0}
"""


def to_html(d: dict) -> str:
    e = html.escape
    s = d["stats"]
    parts = [f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
             f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(d['title'])} {d['date']}</title>"
             f"<style>{CSS}</style></head><body>",
             f"<h1>📰 {e(d['title'])} · {d['date']}</h1>",
             f"<div class='meta'>生成于 {d['generated']}（北京时间）· 最近 {d['hours']} 小时 · 采集 {s['collected']} → 去重 {s['unique']} → 入选 {s['selected']}<br>"
             f"搜索：{e(d['modes']['search'])} · 抓取：{e(d['modes']['fetcher'])} · 摘要：{e(d['modes']['summarizer'])}</div>",
             "<div class='overview'><b>今日概览</b><ul>" +
             "".join(f"<li>{e(x).replace('**', '')}</li>" for x in d["overview"]) + "</ul></div>"]
    for topic, items in d["sections"].items():
        if not items:
            continue
        parts.append(f"<h2>{e(topic)} <span class='meta'>{len(items)} 条</span></h2>")
        for it in items:
            meta = [it.source, fmt_time(it.published)] + ([f"HN {it.points} 分"] if it.points else []) + \
                   (["同见：" + "、".join(it.also_in)] if it.also_in else [])
            tags = "".join(f"<span class='tag'>{e(t)}</span>" for t in (it.topics[1:] + it.keywords)[:6])
            parts.append(f"<div class='card'><a href='{e(it.url)}' target='_blank' rel='noopener'>{e(it.title)}</a>"
                         f"<div class='src'>{e(' · '.join(meta))}</div><p>{e(it.summary)}</p>{tags}</div>")
    parts.append("<footer>由 news-digest 自动生成 · 版权归原作者所有，摘要仅供索引，请点击原文阅读全文。</footer></body></html>")
    return "\n".join(parts)
