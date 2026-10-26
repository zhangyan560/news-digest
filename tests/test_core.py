"""离线单元测试：不访问网络（远程服务全部 mock）。"""
from datetime import datetime, timezone

from digest import fetchers, sources, summarize
from digest.dedupe import dedupe, normalize_url
from digest.models import Item
from digest.tagging import Tagger


def test_normalize_url_strips_tracking_and_www():
    a = normalize_url("https://www.infoq.cn/article/abc/?utm_source=rss&utm_medium=article")
    b = normalize_url("http://infoq.cn/article/abc")
    assert a == b
    assert normalize_url("https://arxiv.org/pdf/2610.31701v2") == normalize_url("https://arxiv.org/abs/2610.31701")


def test_dedupe_by_url_and_title():
    items = [
        Item("Ollama 0.12 released with new engine", "https://ollama.com/blog/x?utm_source=hn", "HN", points=120),
        Item("Ollama 0.12 released with new engine", "https://github.com/ollama/ollama/releases/x", "GitHub"),
        Item("Ollama 0.12 released with a new engine!", "https://example.com/ollama", "博客"),
        Item("Completely different story about Rust", "https://ollama.com/blog/x", "HN 搜索"),
        Item("PostgreSQL 18 发布", "https://www.oschina.net/news/1", "开源中国"),
    ]
    out = dedupe(items)
    titles = [o.title for o in out]
    assert len(out) == 2 and "PostgreSQL 18 发布" in titles
    top = next(o for o in out if o.source == "HN")
    assert {"GitHub", "博客", "HN 搜索"} <= set(top.also_in)


def test_tagging_word_boundaries_and_sources():
    t = Tagger([{"name": "AI", "keywords": ["rag", "大模型", "fine-tun*"]},
                {"name": "论文", "keywords": ["paper"], "sources": ["arXiv"]}])
    assert t.tag(Item("New storage engine", "u", "HN")) == []          # storage 不应命中 rag
    assert t.tag(Item("RAG 实战：大模型检索增强", "u", "HN"))[0][0] == "AI"
    assert t.tag(Item("Fine-tuning tricks", "u", "HN"))[0][0] == "AI"
    assert t.tag(Item("Some title", "u", "arXiv cs.AI"))[0][0] == "论文"


def test_extractive_summary_zh_and_en():
    zh = ("月之暗面今天发布了新一代大模型，参数规模达到三万亿。新模型在代码生成和长上下文任务上表现突出。"
          "官方同时开放了部分权重供研究使用。发布会上还介绍了面向企业的服务方案。")
    it = Item("新模型发布", "u", "s", content=zh)
    summarize.ExtractiveSummarizer().summarize("AI", [it])
    assert it.summary and len(it.summary) <= 161 and it.summary[:4] in zh
    en = Item("Rust 2.0", "u", "s", snippet="The Rust team announced a new edition today. It brings faster compile times. "
              "Run cargo install foo && cargo build to try it. The release also improves async support significantly.")
    summarize.ExtractiveSummarizer().summarize("Dev", [en])
    assert "cargo install" not in en.summary and "Rust team" in en.summary


def test_provider_selection(monkeypatch):
    for k in ("TAVILY_API_KEY", "BRAVE_API_KEY", "FIRECRAWL_API_KEY", "LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL", "SEARCH_PROVIDER"):
        monkeypatch.delenv(k, raising=False)
    assert isinstance(sources.get_search_provider(), sources.HNAlgoliaSearch)
    assert isinstance(fetchers.get_fetcher(), fetchers.LocalFetcher)
    assert isinstance(summarize.get_summarizer(), summarize.ExtractiveSummarizer)
    monkeypatch.setenv("BRAVE_API_KEY", "x")
    assert isinstance(sources.get_search_provider(), sources.BraveSearch)
    monkeypatch.setenv("TAVILY_API_KEY", "x")
    assert isinstance(sources.get_search_provider(), sources.TavilySearch)
    monkeypatch.setenv("SEARCH_PROVIDER", "brave")
    assert isinstance(sources.get_search_provider(), sources.BraveSearch)
    monkeypatch.setenv("FIRECRAWL_API_KEY", "x")
    assert isinstance(fetchers.get_fetcher(), fetchers.FirecrawlFetcher)


def test_tavily_and_firecrawl_request_shape(monkeypatch):
    calls = []

    def fake_post(url, payload, headers=None, timeout=30):
        calls.append((url, payload, headers))
        if "tavily" in url:
            return {"results": [{"title": "T", "url": "https://a.com/1", "content": "c", "published_date": None}]}
        return {"success": True, "data": {"markdown": "# Hello\nbody"}}

    monkeypatch.setattr(sources.http, "post_json", fake_post)
    res = sources.TavilySearch("k").search("LLM", 48, 5)
    assert res[0].url == "https://a.com/1" and calls[0][1]["topic"] == "news" and calls[0][1]["days"] == 2
    assert calls[0][2]["Authorization"] == "Bearer k"
    md = fetchers.FirecrawlFetcher("k", base="https://api.firecrawl.dev").fetch("https://a.com/1")
    assert md.startswith("# Hello") and calls[1][0].endswith("/v2/scrape")
    assert calls[1][1]["formats"] == ["markdown"] and calls[1][1]["onlyMainContent"] is True


def test_llm_summarizer_falls_back_on_error(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:1/v1")
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("LLM_MODEL", "m")

    def boom(*a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(summarize.http, "post_json", boom)
    s = summarize.get_summarizer()
    it = Item("标题", "u", "s", published=datetime.now(timezone.utc),
              content="这是第一句比较长的正文内容用于测试。这是第二句同样比较长的正文内容。")
    s.summarize("AI", [it])
    assert it.summary  # 降级为抽取式


def test_llm_summarizer_parses_json(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://x/v1")
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setattr(summarize.http, "post_json", lambda *a, **k: {"choices": [{"message": {
        "content": '```json\n[{"id":0,"summary":"中文摘要。","keywords":["a","b"]}]\n```'}}]})
    it = Item("Title", "u", "s", snippet="English text here that is long enough.")
    summarize.get_summarizer().summarize("AI", [it])
    assert it.summary == "中文摘要。" and it.keywords == ["a", "b"]
