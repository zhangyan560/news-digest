"""Streamlit 界面：选择/新增主题、设置时间窗口，一键生成并查看日报。

运行：streamlit run app.py
"""
from __future__ import annotations

import copy
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from digest.fetchers import get_fetcher
from digest.pipeline import load_config, run
from digest.render import to_html, to_markdown
from digest.sources import get_search_provider
from digest.summarize import get_summarizer

ROOT = Path(__file__).parent
st.set_page_config(page_title="AI 与开源技术日报", page_icon="📰", layout="wide")
base_cfg = load_config(ROOT / "config" / "topics.yaml")

with st.sidebar:
    st.header("⚙️ 配置")
    names = [t["name"] for t in base_cfg["topics"]]
    chosen = st.multiselect("主题", names, default=names)
    with st.expander("➕ 自定义主题"):
        c_name = st.text_input("主题名称", placeholder="例如：数据库")
        c_kw = st.text_input("关键词（逗号分隔，用于打标签）", placeholder="postgres, mysql, 数据库")
        c_q = st.text_input("搜索词（逗号分隔，可选）", placeholder="postgres, database")
    hours = st.slider("时间窗口（小时）", 12, 168, int(base_cfg.get("hours", 48)), step=12)
    per = st.slider("每个主题最多条数", 3, 10, int(base_cfg.get("max_items_per_topic", 6)))
    full = st.checkbox("抓取正文用于摘要（更慢，遵守 robots.txt）", value=True)
    st.divider()
    st.caption("当前运行模式（由环境变量自动选择）")
    st.markdown(f"- 搜索：**{get_search_provider().name}**\n- 抓取：**{get_fetcher().name}**\n"
                f"- 摘要：**{get_summarizer().name}**")
    if not any(os.getenv(k) for k in ("TAVILY_API_KEY", "BRAVE_API_KEY", "FIRECRAWL_API_KEY", "LLM_API_KEY")):
        st.info("未配置任何 API Key，正在使用免密钥模式。配置方法见 README。", icon="🔑")
    go = st.button("🚀 生成日报", type="primary", use_container_width=True)

st.title("📰 AI 与开源技术日报")
st.caption("RSS / 搜索采集 → 去重 → 主题归类 → 正文抓取 → 摘要 → Markdown / HTML 输出")

if go:
    cfg = copy.deepcopy(base_cfg)
    cfg.update(max_items_per_topic=per, fetch_full_text=full)
    cfg["topics"] = [t for t in cfg["topics"] if t["name"] in chosen]
    if c_name and c_kw:
        split = lambda s: [x.strip() for x in s.replace("，", ",").split(",") if x.strip()]
        cfg["topics"].append({"name": c_name, "keywords": split(c_kw), "queries": split(c_q) or split(c_kw)[:2]})
    if not cfg["topics"]:
        st.warning("请至少选择一个主题")
        st.stop()
    with st.status("正在生成…", expanded=True) as status:
        d = run(cfg, hours=hours, progress=st.write)
        status.update(label="生成完成", state="complete", expanded=False)
    st.session_state["digest"] = d

d = st.session_state.get("digest")
if not d:
    sample = ROOT / "docs" / "sample_digest.md"
    st.info("在左侧选择主题后点击「生成日报」。下方为仓库内的示例日报。")
    if sample.exists():
        st.markdown(sample.read_text(encoding="utf-8"), unsafe_allow_html=True)
    st.stop()

s = d["stats"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("采集条数", s["collected"])
c2.metric("去重后", s["unique"])
c3.metric("入选", s["selected"])
c4.metric("robots 跳过", s["robots_blocked"])
md, html = to_markdown(d), to_html(d)
b1, b2, _ = st.columns([1, 1, 4])
b1.download_button("⬇️ 下载 Markdown", md, f"digest-{d['date']}.md", "text/markdown")
b2.download_button("⬇️ 下载 HTML", html, f"digest-{d['date']}.html", "text/html")
tab1, tab2 = st.tabs(["网页预览", "Markdown 源文件"])
with tab1:
    components.html(html, height=1400, scrolling=True)
with tab2:
    st.code(md, language="markdown")
