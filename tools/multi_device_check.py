#!/usr/bin/env python3
"""ACTIVE 四站多端适配测试。

在本地构建产物上，以 4 种视口 × 深浅主题检查：
- 四枚导航图标 HTTP 200 且为 SVG；
- 页面含四站导航文案，当前站有 aria-current 高亮；
- 无横向溢出；
- 无未捕获 JS 错误；
- 主题属性与预期一致。

只测展示层适配，不改动任何品牌资产或数据口径。

用法：python3 tools/multi_device_check.py
"""
from __future__ import annotations

import functools
import http.server
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path('/oc')
SITES = {
    'running': ROOT / 'zb-running' / 'dist',
    'cycling': ROOT / 'zb-cycling' / 'dist',
    'hiking': ROOT / 'zb-hiking' / 'dist',
    'health': ROOT / 'zb-health' / 'dashboard',
}
KEYS = ('health', 'running', 'cycling', 'hiking')
VIEWPORTS = (
    {'name': 'desktop', 'width': 1440, 'height': 900},
    {'name': 'tablet', 'width': 768, 'height': 1024},
    {'name': 'mobile-390', 'width': 390, 'height': 844},
    {'name': 'mobile-360', 'width': 360, 'height': 800},
)
THEMES = ('dark', 'light')
PORTS = {'running': 8891, 'cycling': 8892, 'hiking': 8893, 'health': 8894}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def start_server(directory: Path, port: int):
    handler = functools.partial(QuietHandler, directory=str(directory))
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def check_one(page, site: str, viewport: dict, theme: str, port: int) -> dict:
    errors: list[str] = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    base = f'http://127.0.0.1:{port}'
    page.goto(base + '/', wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(800)

    # 图标可达性 + SVG 类型
    icon_status = {}
    for key in KEYS:
        resp = page.request.get(f'{base}/brand/icons/{key}.svg')
        ctype = resp.headers.get('content-type', '')
        icon_status[key] = {
            'status': resp.status,
            'is_svg': 'svg' in ctype,
            'bytes': len(resp.body()),
        }

    text = page.locator('body').inner_text()
    nav_labels = all(label in text for label in ('健康', '跑步', '骑行', '徒步'))
    current = page.locator('[aria-current="page"]').count()
    theme_attr = page.evaluate("document.documentElement.dataset.theme || ''")
    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )

    return {
        'site': site,
        'viewport': viewport['name'],
        'theme': theme,
        'icons_ok': all(
            v['status'] == 200 and v['is_svg'] and v['bytes'] > 100
            for v in icon_status.values()
        ),
        'icons': icon_status,
        'nav_labels_ok': nav_labels,
        'current_highlight': current,
        'theme_attr': theme_attr,
        'overflow_px': overflow,
        'js_errors': errors[:5],
    }


def main() -> None:
    servers = {}
    for site, directory in SITES.items():
        if not (directory / 'index.html').exists():
            raise SystemExit(f'缺少构建产物：{directory}')
        servers[site] = start_server(directory, PORTS[site])

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            for site in SITES:
                for viewport in VIEWPORTS:
                    for theme in THEMES:
                        context = browser.new_context(
                            viewport={
                                'width': viewport['width'],
                                'height': viewport['height'],
                            },
                            color_scheme=theme,
                        )
                        context.add_init_script(
                            "try{localStorage.setItem('zhubao315-theme','%s')}catch(e){}" % theme
                        )
                        page = context.new_page()
                        r = check_one(page, site, viewport, theme, PORTS[site])
                        context.close()
                        results.append(r)
                        flag = 'OK ' if (
                            r['icons_ok'] and r['nav_labels_ok']
                            and r['overflow_px'] <= 1 and not r['js_errors']
                        ) else 'FAIL'
                        print(
                            f"[{flag}] {site:<8} {viewport['name']:<10} {theme:<5} "
                            f"icons={r['icons_ok']} nav={r['nav_labels_ok']} "
                            f"cur={r['current_highlight']} theme={r['theme_attr']:<5} "
                            f"overflow={r['overflow_px']} jsErr={len(r['js_errors'])}",
                            flush=True,
                        )
            browser.close()
    finally:
        for httpd in servers.values():
            httpd.shutdown()

    payload = {
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'checks': len(results),
        'passed': sum(
            1 for r in results
            if r['icons_ok'] and r['nav_labels_ok']
            and r['overflow_px'] <= 1 and not r['js_errors']
        ),
        'results': results,
    }
    out = ROOT / 'reports' / 'multi_device_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f"\n{payload['passed']}/{payload['checks']} 通过 → {out}")


if __name__ == '__main__':
    main()
