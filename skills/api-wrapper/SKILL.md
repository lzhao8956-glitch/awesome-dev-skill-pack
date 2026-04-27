---
name: api-wrapper
description: "国内AI平台API一键封装——DeepSeek/通义千问/百度文心/讯飞星火/豆包统一接口"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [api, china, deepseek, qwen, ernie, spark]
    related_skills: [cn-dev-setup]
---

# API Wrapper

国内主流AI平台API的统一封装层。一套代码适配所有平台。

## 支持的平台

| 平台 | 模型 | 费用 |
|------|------|------|
| DeepSeek | deepseek-chat | ¥1/百万token |
| 通义千问 | qwen-max | 免费额度 |
| 百度文心 | ernie-4.0 | 按量付费 |
| 讯飞星火 | spark-4.0 | 免费额度 |

## 统一调用

```python
def call_ai(platform, prompt):
    if platform == "deepseek":
        return call_deepseek(prompt)
    elif platform == "qwen":
        return call_qwen(prompt)
```
