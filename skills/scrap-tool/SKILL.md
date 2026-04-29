---
name: scrap-tool
description: "中文爬虫工具集 —— Python requests/BS4 爬虫模板、反爬虫绕过、Selenium 自动化、数据导出"
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [scraping, crawler, selenium, beautifulsoup, requests, proxy, chinese-web]
    related_skills: [wsl-helper, python-dev]
---

# 中文爬虫工具集

> 专为中文互联网环境设计的爬虫工具包。涵盖 requests 基础爬虫、反爬虫绕过、Selenium 自动化、数据持久化等完整链路。

---

## 目录

1. [requests + BeautifulSoup 基础爬虫](#1-requests--beautifulsoup-基础爬虫)
2. [反爬虫绕过技巧](#2-反爬虫绕过技巧)
3. [中文网站爬取最佳实践](#3-中文网站爬取最佳实践)
4. [Selenium 自动化操作模板](#4-selenium-自动化操作模板)
5. [数据保存 CSV / JSON / Markdown](#5-数据保存-csv--json--markdown)
6. [完整示例代码](#6-完整示例代码)
7. [法律免责声明](#7-法律免责声明)

---

## 1. requests + BeautifulSoup 基础爬虫

### 1.1 通用爬虫函数

```python
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Any


def fetch_page(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    encoding: Optional[str] = None,
) -> Optional[BeautifulSoup]:
    """
    请求网页并返回 BeautifulSoup 对象。

    参数:
        url: 目标 URL
        headers: 自定义请求头（默认伪装为 Chrome 浏览器）
        timeout: 超时秒数
        encoding: 手动指定编码（如 'utf-8', 'gbk', 'gb2312'）
    """
    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
    }
    if headers:
        default_headers.update(headers)

    try:
        resp = requests.get(url, headers=default_headers, timeout=timeout)
        resp.raise_for_status()

        # 编码处理
        if encoding:
            resp.encoding = encoding
        else:
            # 自动检测编码
            resp.encoding = resp.apparent_encoding

        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"[错误] 请求失败: {e}")
        return None


def find_text(soup: BeautifulSoup, selector: str, attr: Optional[str] = None) -> Optional[str]:
    """
    从 BeautifulSoup 对象中按 CSS 选择器提取文本或属性。
    """
    if not soup:
        return None
    tag = soup.select_one(selector)
    if tag is None:
        return None
    if attr:
        return tag.get(attr, "").strip()
    return tag.get_text(strip=True)


def find_all_text(soup: BeautifulSoup, selector: str, attr: Optional[str] = None) -> List[str]:
    """提取所有匹配元素的文本或属性。"""
    if not soup:
        return []
    tags = soup.select(selector)
    if attr:
        return [t.get(attr, "").strip() for t in tags]
    return [t.get_text(strip=True) for t in tags]
```

### 1.2 使用示例

```python
soup = fetch_page("https://example.com")
if soup:
    title = find_text(soup, "h1")
    links = find_all_text(soup, "a", attr="href")
    print(f"标题: {title}")
    print(f"链接数: {len(links)}")
```

---

## 2. 反爬虫绕过技巧

### 2.1 Headers 伪装

```python
# 完整浏览器指纹伪装
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.baidu.com/",
    "Origin": "https://example.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}
```

### 2.2 User-Agent 轮换池

```python
import random

USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    # macOS Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Linux Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # 移动端 Chrome
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]


def random_headers() -> Dict[str, str]:
    """返回一个携带随机 UA 的 Headers 字典。"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.baidu.com/",
    }
```

### 2.3 Cookie 管理与 Session

```python
from requests import Session

session = Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
})

# 首次访问获取 Cookie
resp = session.get("https://example.com")

# 自动携带 Cookie 进行后续请求
resp2 = session.get("https://example.com/protected-page")

# 手动设置 Cookie
session.cookies.set("session_id", "abc123", domain=".example.com")

# 从文件加载 Cookie
import json
with open("cookies.json", "r") as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)
```

### 2.4 代理轮换

```python
def fetch_with_proxy(url: str, proxy_list: List[str]) -> Optional[str]:
    """
    使用代理池请求，失败时自动重试下一个代理。
    代理格式: "http://user:pass@ip:port" 或 "socks5://ip:port"
    """
    for proxy_url in proxy_list:
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        try:
            resp = requests.get(
                url,
                headers=random_headers(),
                proxies=proxies,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[代理失败] {proxy_url}: {e}")
            continue
    print("[错误] 所有代理均不可用")
    return None
```

---

## 3. 中文网站爬取最佳实践

### 3.1 编码处理

中文网站常见的编码问题及解决方案：

```python
# 方案一：自动检测编码（推荐）
resp = requests.get(url)
resp.encoding = resp.apparent_encoding  # chardet 检测

# 方案二：手动指定编码
# 常见中文编码：
#   GBK / GB2312  → 国内老牌门户（新浪、网易等）
#   GB18030       → 更全面的国标扩展
#   UTF-8         → 现代网站标准
#   Big5          → 繁体中文网站（台湾、香港）

# 方案三：从 HTML 的 <meta> 标签解析编码
import re
meta_charset = re.search(r'charset=["\']?([\w-]+)', resp.text[:2000])
if meta_charset:
    resp.encoding = meta_charset.group(1)
```

### 3.2 请求间隔与限速

```python
import time
import random

def polite_request(url: str, min_delay: float = 1.0, max_delay: float = 3.0) -> Optional[str]:
    """
    带随机延迟的礼貌请求，降低被封概率。
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    return fetch_page(url)
```

### 3.3 验证码检测与提示

遇到验证码时的处理策略：

1. **检测特征**
   - 响应中包含 `<img.*captcha` 或 `verify` 关键字
   - 状态码 403 / 429（Rate Limit）
   - 响应文本小于预期且包含"验证码"、"请滑动"等关键词
   - 返回 JSON 且包含 `"code": -1` 等业务错误码

2. **应对策略**
   - 降低请求频率，增加随机延迟
   - 更换 IP 代理
   - 使用 OCR（如 `ddddocr`）识别简单图形验证码
   - 打码平台（如 打码兔、超级鹰）用于复杂验证码
   - Selenium + 人工介入手动填写

```python
def detect_captcha(text: str) -> bool:
    """简易验证码检测。"""
    keywords = ["验证码", "captcha", "请输入验证码", "请滑动验证", "人机验证"]
    return any(kw in text for kw in keywords)
```

### 3.4 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def robust_fetch(url: str) -> str:
    """带指数退避重试的请求函数。"""
    resp = requests.get(url, headers=random_headers(), timeout=10)
    resp.raise_for_status()
    return resp.text
```

---

## 4. Selenium 自动化操作模板

### 4.1 基础模板

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """创建配置好的 Chrome WebDriver。"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # 禁用自动化标识
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # 替换 navigator.webdriver 属性，防止被检测
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        },
    )
    return driver


def wait_and_find(driver: webdriver.Chrome, by: str, value: str, timeout: int = 10):
    """等待元素出现并返回。"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_and_click(driver: webdriver.Chrome, by: str, value: str, timeout: int = 10):
    """等待元素可点击并点击。"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
```

### 4.2 页面滚动（应对懒加载）

```python
def scroll_to_bottom(driver: webdriver.Chrome, step: int = 500, delay: float = 0.5):
    """模拟用户滚动页面底部，触发懒加载。"""
    current_height = driver.execute_script("return document.body.scrollHeight")
    for y in range(0, current_height, step):
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(delay)


def scroll_and_collect(
    url: str,
    item_selector: str,
    scroll_times: int = 5,
    delay: float = 1.0,
) -> List[str]:
    """滚动加载后收集元素文本。"""
    driver = create_driver()
    driver.get(url)
    time.sleep(2)

    for _ in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    elements = driver.find_elements(By.CSS_SELECTOR, item_selector)
    result = [el.text for el in elements if el.text.strip()]
    driver.quit()
    return result
```

### 4.3 表单填写与提交

```python
def login_example(driver: webdriver.Chrome, username: str, password: str):
    """登录流程示例。"""
    driver.get("https://example.com/login")

    # 填写用户名
    username_input = wait_and_find(driver, By.CSS_SELECTOR, "#username")
    username_input.clear()
    username_input.send_keys(username)

    # 填写密码
    password_input = wait_and_find(driver, By.CSS_SELECTOR, "#password")
    password_input.clear()
    password_input.send_keys(password)

    # 点击登录
    wait_and_click(driver, By.CSS_SELECTOR, "button[type='submit']")
    time.sleep(3)  # 等待登录完成
```

---

## 5. 数据保存 CSV / JSON / Markdown

### 5.1 保存为 CSV

```python
import csv


def save_to_csv(data: List[Dict[str, Any]], filepath: str, encoding: str = "utf-8-sig"):
    """
    将字典列表保存为 CSV 文件。
    使用 utf-8-sig 编码，确保 Excel 正确显示中文。
    """
    if not data:
        print("[警告] 数据为空，未生成 CSV")
        return

    fieldnames = data[0].keys()
    with open(filepath, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] CSV 已保存: {filepath}")


load_data = [
    {"标题": "新闻A", "链接": "https://...", "时间": "2025-01-01"},
    {"标题": "新闻B", "链接": "https://...", "时间": "2025-01-02"},
]
save_to_csv(load_data, "output.csv")
```

### 5.2 保存为 JSON

```python
import json


def save_to_json(data: Any, filepath: str, ensure_ascii: bool = False, indent: int = 2):
    """
    将数据保存为 JSON 文件。
    ensure_ascii=False 保证中文不被转义为 \\uXXXX。
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
    print(f"[OK] JSON 已保存: {filepath}")


save_to_json(load_data, "output.json")
```

### 5.3 保存为 Markdown

```python
def save_to_markdown(rows: List[Dict[str, str]], filepath: str, title: str = "爬取结果"):
    """将列表数据保存为 Markdown 表格。"""
    if not rows:
        print("[警告] 数据为空")
        return

    fieldnames = list(rows[0].keys())
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        # 表头
        f.write("| " + " | ".join(fieldnames) + " |\n")
        # 分隔行
        f.write("| " + " | ".join(["---"] * len(fieldnames)) + " |\n")
        # 数据行
        for row in rows:
            f.write("| " + " | ".join(str(row.get(k, "")) for k in fieldnames) + " |\n")
    print(f"[OK] Markdown 已保存: {filepath}")
```

### 5.4 便捷函数

```python
def save_data(data: Any, filepath: str, format: str = "auto"):
    """根据文件扩展名自动选择保存格式。"""
    if format == "auto":
        ext = filepath.rsplit(".", 1)[-1].lower() if "." in filepath else ""
        format = ext

    if format in ("csv",):
        save_to_csv(data, filepath)
    elif format in ("json",):
        save_to_json(data, filepath)
    elif format in ("md", "markdown"):
        save_to_markdown(data, filepath)
    else:
        print(f"[错误] 不支持的格式: {format}")
```

---

## 6. 完整示例代码

> 以下示例爬取一个中文新闻网站，演示完整流程。
> 实战代码请参见同目录下的 `scraper_example.py`。

```python
# scraper_example.py — 中文新闻爬虫完整示例
#
# 爬取目标: https://news.baidu.com/ 的实时热搜列表
# 技术栈:  requests + BeautifulSoup + CSV 保存

import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# ---------- 配置 ----------
URL = "https://news.baidu.com/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.baidu.com/",
}
OUTPUT_FILE = "baidu_news.csv"


# ---------- 爬取 ----------
def fetch_news():
    """爬取百度新闻热搜列表。"""
    time.sleep(random.uniform(0.5, 1.5))  # 礼貌延迟

    resp = requests.get(URL, headers=HEADERS, timeout=10)
    resp.encoding = resp.apparent_encoding  # 自动检测中文编码
    soup = BeautifulSoup(resp.text, "html.parser")

    news_list = []
    items = soup.select("ul.hot-list a") or soup.select(".hot-news a") or soup.select("a[mon*='hot']")

    if not items:
        # 兜底策略：提取所有包含新闻关键词的链接
        items = soup.find_all("a", href=True)
        items = [
            a for a in items
            if a.get_text(strip=True) and len(a.get_text(strip=True)) > 5
        ][:20]

    for a in items:
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if title and len(title) >= 4:
            news_list.append({"标题": title, "链接": link})

    return news_list


# ---------- 保存 ----------
def save_csv(data, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["标题", "链接"])
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] 已保存 {len(data)} 条新闻到 {path}")


# ---------- 主函数 ----------
def main():
    print("=" * 50)
    print("  中文爬虫工具集 — 示例程序")
    print("=" * 50)

    news = fetch_news()
    if news:
        print(f"\n共获取 {len(news)} 条新闻：")
        for i, item in enumerate(news[:5], 1):
            print(f"  {i}. {item['标题']}")
        save_csv(news, OUTPUT_FILE)
    else:
        print("[警告] 未获取到新闻数据，可能是页面结构发生变化")
        # 输出 HTML 前 500 字符供调试
        print(f"  HTML 预览: {resp.text[:200]}")


if __name__ == "__main__":
    main()


# ---------- 更多示例：使用 Selenium ----------
# 如果目标网站使用 JavaScript 动态渲染，改用以下方式：
#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
# def fetch_news_selenium():
#     options = Options()
#     options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     driver = webdriver.Chrome(options=options)
#     driver.get("https://news.baidu.com/")
#     time.sleep(3)
#
#     # 滚动到底部
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(1)
#
#     items = driver.find_elements(By.CSS_SELECTOR, "a[href*='baidu']")
#     news = [{"标题": el.text, "链接": el.get_attribute("href")} for el in items if el.text.strip()]
#     driver.quit()
#     return news
```

---

## 7. 法律免责声明

> **重要：在使用本工具集之前，请务必阅读并理解以下条款。**

### 7.1 合规使用

1. **遵守网站 robots.txt** — 在爬取前请检查目标网站的 `/robots.txt` 文件，遵守其爬取规则。
2. **尊重版权** — 爬取的内容不得侵犯他人知识产权。转载或商业使用需获得授权。
3. **遵守法律法规** — 根据《中华人民共和国网络安全法》《个人信息保护法》《数据安全法》等法律法规：
   - 不得爬取涉及国家秘密、商业秘密、个人隐私的数据
   - 不得对目标网站造成拒绝服务（DDoS）或破坏其正常运行
   - 不得绕过技术保护措施获取受版权保护的内容
   - 收集个人信息需遵循合法、正当、必要原则

### 7.2 使用建议

- ⚡ **控制频率** — 设置合理的请求间隔，避免对目标服务器造成压力
- 🔒 **数据脱敏** — 爬取到个人信息时应进行脱敏处理
- 📝 **标注来源** — 公开数据使用时建议注明出处
- 🚫 **禁止滥用** — 不得将本工具用于任何非法目的

### 7.3 免责声明

本工具集仅供学习和研究使用。作者不对因使用本工具而产生的任何直接或间接损失承担责任。使用者应自行评估法律风险，并确保使用方式符合所在司法管辖区的法律规定。如因使用本工具引发任何法律纠纷，责任由使用者自行承担。

---

## 附录：常用资源

| 资源 | 链接 | 说明 |
|------|------|------|
| requests 文档 | https://requests.readthedocs.io/ | Python HTTP 库 |
| BeautifulSoup 文档 | https://www.crummy.com/software/BeautifulSoup/bs4/doc/ | HTML/XML 解析 |
| Selenium 文档 | https://www.selenium.dev/documentation/ | 浏览器自动化 |
| 代理服务商 | 快代理、芝麻代理、StormProxies | 企业级代理池 |
| 打码平台 | 超级鹰、打码兔、2Captcha | 验证码识别 |

---

*本工具集由 Hermes Agent 维护。欢迎提交 Issue 和 PR 改进。*
