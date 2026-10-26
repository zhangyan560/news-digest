"""用 Playwright 截图：Streamlit 界面（需先 streamlit run app.py）与生成的 HTML 日报。

用法：python scripts/screenshot.py [chrome 可执行文件路径] [streamlit 地址]
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

exe = sys.argv[1] if len(sys.argv) > 1 else None
URL = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8501"
OUT = Path("screenshots")
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    page = b.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(URL)
    page.get_by_role("button", name="生成日报").click(timeout=60000)
    page.get_by_text("下载 Markdown").wait_for(timeout=300000)
    page.wait_for_timeout(3000)
    page.screenshot(path=OUT / "01_streamlit_digest.png")
    print("saved 01")
    page.get_by_role("tab", name="Markdown 源文件").click()
    page.wait_for_timeout(1500)
    page.screenshot(path=OUT / "02_streamlit_markdown.png")
    print("saved 02")
    html = Path("docs/sample_digest.html").resolve()
    page2 = b.new_page(viewport={"width": 1000, "height": 1600})
    page2.goto(html.as_uri())
    page2.wait_for_timeout(800)
    page2.screenshot(path=OUT / "03_html_digest.png")
    print("saved 03")
    b.close()
