#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文爬虫工具集 — 实战示例
===========================

爬取目标: 百度新闻热搜 (https://news.baidu.com/)
使用技术: requests + BeautifulSoup + CSV 保存

用法:
    python scraper_example.py

依赖安装:
    pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
import sys
from typing import List, Dict, Optional

# ============================================================
# 配置区
# ============================================================

# 目标 URL — 百度新闻热搜
URL = "https://news.baidu.com/"

# 浏览器伪装 Headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.baidu.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
}

# 输出文件名
OUTPUT_CSV = "baidu_news.csv"
OUTPUT_JSON = "baidu_news.json"

# 请求间隔 (秒)
MIN_DELAY = 0.5
MAX_DELAY = 1.5

# ============================================================
# 爬虫核心
# ============================================================


def polite_delay():
    """随机延迟，模拟人类浏览行为。"""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)


def fetch_page(url: str) -> Optional[requests.Response]:
    """
    请求网页，自动处理编码。

    返回:
        requests.Response 对象，失败返回 None
    """
    polite_delay()

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        # 自动检测编码（对中文网站至关重要）
        resp.encoding = resp.apparent_encoding

        # 检测是否被反爬
        if detect_blocked(resp):
            print("[警告] 可能被反爬机制拦截！")
            return None

        return resp

    except requests.exceptions.RequestException as e:
        print(f"[错误] 网络请求失败: {e}")
        return None


def detect_blocked(resp: requests.Response) -> bool:
    """检测是否被反爬机制拦截。"""
    # 状态码检测
    if resp.status_code in (403, 429, 503):
        return True

    # 内容检测
    text = resp.text[:1000].lower()
    blocked_keywords = [
        "验证码", "captcha", "访问被拒绝", "access denied",
        "请求过于频繁", "rate limit", "安全验证",
        "请滑动验证", "人机验证",
    ]
    return any(kw in text for kw in blocked_keywords)


def parse_news(resp: requests.Response) -> List[Dict[str, str]]:
    """
    从百度新闻页面解析新闻列表。

    返回:
        [{'标题': ..., '链接': ...}, ...]
    """
    soup = BeautifulSoup(resp.text, "html.parser")
    news_list = []

    # 策略 1: 百度新闻热搜链接选择器（多种可能的结构）
    selectors = [
        "ul.hot-list a",
        ".hot-news a",
        "a[mon*='hot']",
        ".hotwords a",
        ".news-title a",
    ]

    items = []
    for selector in selectors:
        items = soup.select(selector)
        if items:
            print(f"  [解析] 使用选择器 '{selector}' 找到 {len(items)} 个元素")
            break

    # 策略 2: 兜底 — 提取所有有意义的中文链接
    if not items:
        print("  [解析] 使用兜底策略提取链接")
        all_links = soup.find_all("a", href=True)
        items = [
            a for a in all_links
            if a.get_text(strip=True) and len(a.get_text(strip=True)) >= 6
        ][:30]

    # 提取标题和链接
    seen_titles = set()
    for a in items:
        title = a.get_text(strip=True)
        link = a.get("href", "")

        # 过滤无效项
        if not title or len(title) < 4:
            continue
        if title in seen_titles:
            continue  # 去重
        seen_titles.add(title)

        # 相对路径转绝对路径
        if link.startswith("//"):
            link = "https:" + link
        elif link.startswith("/"):
            link = resp.url.rstrip("/") + link
        elif not link.startswith("http"):
            link = resp.url.rstrip("/") + "/" + link

        news_list.append({"标题": title, "链接": link})

    return news_list


# ============================================================
# 数据保存
# ============================================================


def save_to_csv(data: List[Dict[str, str]], filepath: str):
    """保存为 CSV（utf-8-sig 编码，兼容 Excel）。"""
    if not data:
        print("[警告] 无数据，跳过 CSV 保存")
        return

    fieldnames = ["标题", "链接"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"  [保存] CSV → {filepath} ({len(data)} 行)")


def save_to_json(data: List[Dict[str, str]], filepath: str):
    """保存为 JSON（保留中文，格式化输出）。"""
    if not data:
        print("[警告] 无数据，跳过 JSON 保存")
        return

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  [保存] JSON → {filepath} ({len(data)} 行)")


def save_to_markdown(data: List[Dict[str, str]], filepath: str):
    """保存为 Markdown 表格。"""
    if not data:
        print("[警告] 无数据，跳过 Markdown 保存")
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# 百度新闻热搜\n\n")
        f.write("| 标题 | 链接 |\n")
        f.write("|------|------|\n")
        for item in data:
            f.write(f"| {item['标题']} | {item['链接']} |\n")

    print(f"  [保存] Markdown → {filepath} ({len(data)} 行)")


# ============================================================
# 主流程
# ============================================================


def main():
    print("=" * 55)
    print("  中文爬虫工具集 — 实战示例")
    print(f"  目标: {URL}")
    print("=" * 55)

    # 第 1 步：请求页面
    print("\n[1/3] 正在请求页面...")
    resp = fetch_page(URL)
    if resp is None:
        print("[失败] 无法获取页面，请检查网络或目标网站状态")
        sys.exit(1)
    print(f"  [OK] 状态码: {resp.status_code}, 编码: {resp.encoding}")

    # 第 2 步：解析数据
    print("\n[2/3] 正在解析新闻...")
    news = parse_news(resp)
    print(f"  [OK] 共提取 {len(news)} 条新闻")

    # 打印前 10 条预览
    if news:
        print("\n  前 10 条新闻预览:")
        for i, item in enumerate(news[:10], 1):
            print(f"    {i:2d}. {item['标题'][:50]}")
    else:
        print("  [警告] 未提取到新闻，可能是页面结构已更新")

    # 第 3 步：保存数据
    print("\n[3/3] 正在保存数据...")
    save_to_csv(news, OUTPUT_CSV)
    save_to_json(news, OUTPUT_JSON)
    save_to_markdown(news, "baidu_news.md")

    # 总结
    print("\n" + "=" * 55)
    print("  爬取完成！生成的文件:")
    print(f"    - {OUTPUT_CSV}")
    print(f"    - {OUTPUT_JSON}")
    print(f"    - baidu_news.md")
    print("=" * 55)


# ============================================================
# Selenium 版本（备选）
# ============================================================

def selenium_version():
    """
    如果目标网站使用 JavaScript 动态渲染，使用 Selenium 版本。

    依赖安装:
        pip install selenium webdriver-manager
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("请安装依赖: pip install selenium webdriver-manager")
        return

    print("\n[Selenium 模式] 正在启动浏览器...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    # 隐藏自动化标识
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    # 注入 JS 隐藏 webdriver 属性
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )

    try:
        driver.get(URL)
        time.sleep(3)  # 等待 JS 渲染

        # 滚动到底部触发懒加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 提取所有标题
        items = driver.find_elements(By.CSS_SELECTOR, "a[href*='baidu']")
        news = []
        seen = set()
        for el in items:
            title = el.text.strip()
            link = el.get_attribute("href") or ""
            if title and len(title) >= 4 and title not in seen:
                seen.add(title)
                news.append({"标题": title, "链接": link})

        print(f"  [Selenium] 提取 {len(news)} 条新闻")
        save_to_csv(news, "baidu_news_selenium.csv")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

    # 如需使用 Selenium 版本，取消下面注释：
    # selenium_version()
