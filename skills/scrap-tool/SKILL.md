---
name: scrap-tool
description: "AI驱动的数据采集工具——网页爬虫、API采集、数据清洗、自动化导出"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [scraping, crawler, data, automation]
    related_skills: [wsl-helper]
---

# Scrap Tool

## 爬虫模板

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_table(url):
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = pd.read_html(resp.text)
    return tables[0]
```
