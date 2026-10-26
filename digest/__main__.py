"""命令行：python -m digest run --config config/topics.yaml --out output/"""
import argparse
import logging

from .pipeline import load_config, run, write


def main():
    ap = argparse.ArgumentParser(prog="digest", description="AI 与开源技术资讯汇总")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="生成一份日报")
    r.add_argument("--config", default="config/topics.yaml")
    r.add_argument("--out", default="output")
    r.add_argument("--hours", type=int, help="时间窗口（小时），默认取配置")
    r.add_argument("--topics", nargs="*", help="只生成指定主题")
    r.add_argument("--stem", help="输出文件名（不含扩展名），默认 digest-日期")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    d = run(load_config(a.config), hours=a.hours, topics=a.topics)
    md, html = write(d, a.out, a.stem)
    print(f"已生成：{md}  {html}  （模式：{d['modes']}，robots 跳过 {d['stats']['robots_blocked']} 条）")


if __name__ == "__main__":
    main()
