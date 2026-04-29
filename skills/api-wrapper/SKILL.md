---
name: api-wrapper
description: "国内AI平台API统一封装 —— DeepSeek / 通义千问 / 百度文心 / 讯飞星火 一键切换"
version: 2.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [api, china, deepseek, qwen, ernie, spark, wrapper]
    related_skills: [cn-dev-setup, python-utils]
---

# API Wrapper — 国内主流 AI 平台统一封装层

一套 Python 代码搞定 DeepSeek、通义千问 (DashScope)、百度文心 (ERNIE)、讯飞星火四个平台的 API 调用。提供**统一接口**，一行代码切换任意模型，内置重试、错误处理、Token 计数。

---

## 支持平台一览

| 平台 | SDK 类 | 默认模型 | 鉴权方式 | 费用参考 |
|------|--------|----------|----------|----------|
| **DeepSeek** | `DeepSeekAPI` | `deepseek-chat` | API Key (兼容 OpenAI 格式) | ¥1/百万 tokens |
| **通义千问** | `DashScopeAPI` | `qwen-max` | API Key (Bearer Token) | 有免费额度 |
| **百度文心** | `ERNIEAPI` | `ernie-4.0` | API Key + Secret Key (OAuth) | 按量付费 |
| **讯飞星火** | `SparkAPI` | `spark-3.5` | App ID + API Key + Secret | 有免费额度 |

---

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 设置环境变量

根据你要使用的平台，设置对应的密钥：

```bash
# DeepSeek
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"

# 通义千问
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxx"

# 百度文心
export ERNIE_API_KEY="xxxxxxxxxxxx"
export ERNIE_SECRET_KEY="xxxxxxxxxxxx"

# 讯飞星火
export SPARK_APP_ID="xxxxx"
export SPARK_API_KEY="xxxxxxxxxxxx"
export SPARK_API_SECRET="xxxxxxxxxxxx"
```

也可以直接在代码中传入参数（见下文）。

### 3. 一行代码调用

```python
from api_wrapper import call_ai, extract_content

# DeepSeek
resp = call_ai("deepseek", "用 Python 写一个快排")
print(extract_content(resp))

# 切到通义千问 —— 改一个参数名即可
resp = call_ai("qwen", "用 Python 写一个快排")
print(extract_content(resp))

# 百度文心
resp = call_ai("ernie", "用 Python 写一个快排")
print(extract_content(resp))

# 讯飞星火
resp = call_ai("spark", "用 Python 写一个快排")
print(extract_content(resp))
```

### 4. 高级调用

```python
resp = call_ai(
    platform="deepseek",
    prompt="解释一下什么是闭包",
    system_prompt="你是一位资深 Python 架构师，回答简洁、深刻。",
    model="deepseek-chat",
    temperature=0.3,
    stream=False,                # 暂不支持流式解析，保留字段
)
```

---

## API 参考

### `call_ai(platform, prompt, ...)` — 统一入口

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `platform` | str | 必填 | 平台名称: `deepseek` / `qwen` (或 `dashscope`) / `ernie` (或 `baidu`) / `spark` (或 `xunfei`) |
| `prompt` | str | 必填 | 用户输入文本 |
| `system_prompt` | str \| None | `None` | 系统提示词 |
| `model` | str \| None | 各平台默认值 | 模型名称，如 `deepseek-chat`, `qwen-max`, `ernie-4.0`, `spark-3.5` |
| `temperature` | float | 0.7 | 生成温度 (0~2)，值越大输出越随机 |
| `stream` | bool | `False` | 是否启用流式 (传递到 API) |
| `**kwargs` | dict | — | 透传给平台构造函数的额外参数，例如 `api_key`、`secret_key` 等 |

**返回**: 原始 API JSON 响应 (dict)

### `extract_content(response)` — 统一内容提取

从各平台不同格式的响应中提取模型生成的文本。

| 参数 | 类型 | 说明 |
|------|------|------|
| `response` | dict | `call_ai()` 返回的原始响应 |

**返回**: 模型回复文本 (str)

### `create_api(platform, **kwargs)` — 客户端工厂

获取指定平台的 API 客户端实例，适用于需要复用客户端的场景。

```python
from api_wrapper import create_api

client = create_api("deepseek", api_key="sk-xxx")
resp = client.chat(
    messages=[{"role": "user", "content": "你好"}],
    model="deepseek-chat",
)
```

### `estimate_tokens(text)` — 简易 Token 估算

```python
from api_wrapper import estimate_tokens
tokens = estimate_tokens("你好世界")  # ≈ 5
```

> **注意**: 这是基于字符数的粗略估算（中英文混合 ×1.3），仅用于日志和成本展示，**不可替代**平台的精确计数。

---

## 架构设计

```
用户代码
    │
    ▼
call_ai(platform, prompt, ...)   ← 统一入口
    │
    ▼
create_api(platform, **kwargs)   ← 工厂模式
    │              │              │              │
    ▼              ▼              ▼              ▼
DeepSeekAPI   DashScopeAPI    ERNIEAPI       SparkAPI
    │              │              │              │
    └──────────────┴──────────────┴──────────────┘
                          │
                    retry_on_failure               ← 指数退避重试
                    estimate_tokens                ← 简易 Token 计数
                    extract_content                ← 统一内容提取
```

### 请求重试机制

- 网络层面的 `ConnectionError` 和 `Timeout` 会自动重试
- 最多重试 **3 次**
- 间隔按指数退避: 2s → 4s → 8s
- HTTP 状态码异常（如 429、500）会直接抛出异常，不自动重试（避免放大故障）
- 可通过 `@retry_on_failure(max_retries=5, backoff=1.0)` 自定义

### 错误处理策略

| 异常类型 | 说明 |
|----------|------|
| `ValueError` | 缺少 API Key、不支持的平台 |
| `RuntimeError` | API 返回错误 (含状态码和响应体) |
| `requests.ConnectionError` | 网络不可达（会被重试） |
| `requests.Timeout` | 请求超时（会被重试） |

所有异常都包含**中文错误消息**，便于排查。

### Token 计费追踪

每次调用返回的原始响应中包含了平台的用量数据，`call_ai()` 内部会自动打印日志：

```
2026-04-29 13:25:01 [INFO] api-wrapper: DeepSeek [deepseek-chat] ↑42 ↓158 tokens
```

你可以从 `response["usage"]` 或 `extract_content()` 之外的工具函数中提取具体数字。

---

## 命令行直接使用

安装后也支持命令行调用：

```bash
# 调用 DeepSeek
python api_wrapper.py deepseek "你好, 请自我介绍一下"

# 调用通义千问
python api_wrapper.py qwen "用 Python 写一个二分查找"

# 调用百度文心
python api_wrapper.py ernie "解释量子计算的基本原理"
```

---

## 文件和结构

```
api-wrapper/
├── SKILL.md            ← 本文档
└── api_wrapper.py      ← 完整 Python 封装实现
```

`api_wrapper.py` 约 380 行，包含了全部四个平台的 API 实现、统一入口、重试机制、错误处理和 CLI 入口。

---

## 注意事项

1. **API Key 安全**: 建议通过环境变量注入，不要硬编码在源码中。
2. **流式响应**: 当前 `stream=True` 会透传参数到 API，但未提供流式解析回调。如需完整流式支持，可基于 `api_wrapper.py` 扩展 SSE/WebSocket 处理。
3. **Token 估算**: `estimate_tokens()` 是粗略值，实际消耗以各平台返回的用量为准。
4. **并发限制**: 各平台有各自 QPS 限制，生产环境建议加入信号量或限流中间件。

---

## 扩展指引

如果要添加新平台（例如 豆包、Kimi、百川），只需三步：

1. 在 `api_wrapper.py` 中新增一个类，实现 `chat(messages, model, temperature, stream) -> dict` 方法
2. 在 `_platform_registry` 字典中注册类名
3. 在 `_default_model` 字典中加入默认模型名

无需修改任何调用侧代码。

---

## License

MIT
