"""礼貌的 HTTP 客户端：统一 UA、超时、按域名限速、robots.txt 检查、磁盘缓存。"""
from __future__ import annotations

import hashlib
import os
import threading
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = os.getenv("DIGEST_USER_AGENT",
                       "news-digest/0.1 (+https://github.com/zhangyan560/news-digest)")
MIN_INTERVAL = float(os.getenv("DIGEST_MIN_INTERVAL", "1.0"))  # 同一域名两次请求的最小间隔（秒）
CACHE_DIR = Path(os.getenv("DIGEST_CACHE_DIR", ".cache"))
CACHE_TTL = 6 * 3600

_session = requests.Session()
_retry = Retry(total=2, backoff_factor=1.0, status_forcelist=(429, 502, 503, 504), allowed_methods=("GET",))
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))
_session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
_last: dict[str, float] = {}
_delay: dict[str, float] = {}  # robots.txt 中声明的 Crawl-delay
_locks: dict[str, threading.Lock] = {}
_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_glock = threading.Lock()
robots_blocked: list[str] = []  # 本次运行因 robots.txt 跳过的 URL（用于统计展示）


def _domain_lock(host: str) -> threading.Lock:
    with _glock:
        return _locks.setdefault(host, threading.Lock())


def _throttle(host: str):
    with _domain_lock(host):
        wait = _last.get(host, 0) + max(MIN_INTERVAL, _delay.get(host, 0)) - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()


def allowed(url: str) -> bool:
    """遵守 robots.txt。
    - 2xx：按规则判断；401/403：视为全部禁止；其他 4xx（如 404）：视为全部允许；
    - 5xx 或网络错误：保守起见视为禁止（与主流搜索引擎做法一致）。"""
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp: urllib.robotparser.RobotFileParser | None = urllib.robotparser.RobotFileParser()
        try:
            _throttle(p.netloc)
            r = _session.get(base + "/robots.txt", timeout=10)
            if r.ok:
                rp.parse(r.text.splitlines())
            elif r.status_code in (401, 403) or r.status_code >= 500:
                rp = None
            else:
                rp.parse([])
        except requests.RequestException:
            rp = None
        _robots[base] = rp
        if rp is not None and rp.crawl_delay(USER_AGENT):
            _delay[p.netloc] = min(float(rp.crawl_delay(USER_AGENT)), 30.0)
    rp = _robots[base]
    return bool(rp and rp.can_fetch(USER_AGENT, url))


def get(url: str, *, check_robots=True, cache=True, timeout=15, **kw) -> requests.Response | None:
    key = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if cache and key.exists() and time.time() - key.stat().st_mtime < CACHE_TTL:
        r = requests.Response()
        r.status_code, r._content, r.url, r.encoding = 200, key.read_bytes(), url, "utf-8"
        return r
    if check_robots and not allowed(url):
        robots_blocked.append(url)
        return None
    _throttle(urlparse(url).netloc)
    try:
        r = _session.get(url, timeout=timeout, **kw)
    except requests.RequestException:
        return None
    if r.ok and cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        key.write_bytes(r.content)
    return r if r.ok else None


def post_json(url: str, payload: dict, headers: dict | None = None, timeout=30) -> dict:
    _throttle(urlparse(url).netloc)
    r = _session.post(url, json=payload, headers=headers or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()
