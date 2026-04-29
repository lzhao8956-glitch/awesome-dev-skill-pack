#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内主流 AI 平台 API 统一封装层
=================================

支持平台：
  - DeepSeek (兼容 OpenAI SDK 格式)
  - 通义千问 DashScope
  - 百度文心 ERNIE
  - 讯飞星火 Spark

特性：
  - 统一调用接口，一行代码切换模型
  - 自动请求重试 (指数退避)
  - 结构化错误处理与日志
  - 简易 Token 计数
  - 流式 / 非流式双模式
"""

import os
import json
import time
import logging
from typing import Optional, Callable

import requests

# ---------------------------------------------------------------------------
# 日志 & 常量
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api-wrapper")

DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # 指数退避基数 (秒)

# 简易 Token 估算: 中英文混合 ≈ 词数 × 1.3
def estimate_tokens(text: str) -> int:
    """粗略估算文本 token 数 (仅用于日志 / 成本展示)."""
    return int(len(text) * 1.3)


# ---------------------------------------------------------------------------
# 重试装饰器
# ---------------------------------------------------------------------------

def retry_on_failure(
    max_retries: int = MAX_RETRIES,
    backoff: float = RETRY_BACKOFF,
    retryable_exceptions: tuple = (requests.ConnectionError, requests.Timeout),
):
    """带指数退避的重试装饰器."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exc = e
                    if attempt < max_retries:
                        sleep_time = backoff * (2 ** (attempt - 1))
                        logger.warning(
                            "[重试 %d/%d] %s 失败, %.1f 秒后重试 ...",
                            attempt, max_retries, func.__name__, sleep_time,
                        )
                        time.sleep(sleep_time)
            raise RuntimeError(
                f"[{func.__name__}] 重试 {max_retries} 次后仍然失败: {last_exc}"
            ) from last_exc
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# 底层实现
# ---------------------------------------------------------------------------

class DeepSeekAPI:
    """DeepSeek API (OpenAI 兼容格式)."""

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY")

    @retry_on_failure()
    def chat(
        self,
        messages: list,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}/chat/completions"

        resp = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"DeepSeek API 错误 [{resp.status_code}]: {resp.text}")

        data = resp.json()
        logger.info(
            "DeepSeek [%s] ↑%d ↓%d tokens",
            model,
            data.get("usage", {}).get("prompt_tokens", 0),
            data.get("usage", {}).get("completion_tokens", 0),
        )
        return data


class DashScopeAPI:
    """通义千问 DashScope API."""

    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY")

    @retry_on_failure()
    def chat(
        self,
        messages: list,
        model: str = "qwen-max",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "result_format": "message",
            },
        }
        if stream:
            payload["parameters"]["incremental_output"] = True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}/services/aigc/text-generation/generation"

        resp = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"DashScope API 错误 [{resp.status_code}]: {resp.text}")

        data = resp.json()
        usage = data.get("usage", {})
        logger.info(
            "通义千问 [%s] ↑%d ↓%d tokens",
            model,
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0),
        )
        return data


class ERNIEAPI:
    """百度文心 ERNIE API (4.0 / 3.5)."""

    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    BASE_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"

    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ERNIE_API_KEY")
        self.secret_key = secret_key or os.getenv("ERNIE_SECRET_KEY")
        if not self.api_key or not self.secret_key:
            raise ValueError("请设置 ERNIE_API_KEY 和 ERNIE_SECRET_KEY")
        self._access_token: Optional[str] = None

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        resp = requests.post(
            self.TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取 ERNIE access_token 失败: {data}")
        self._access_token = data["access_token"]
        return self._access_token

    def _model_endpoint(self, model: str) -> str:
        mapping = {
            "ernie-4.0": "completions_pro",
            "ernie-3.5": "completions",
            "ernie-lite": "eb_instance",
        }
        suffix = mapping.get(model, model)
        return f"{self.BASE_URL}/{suffix}"

    @retry_on_failure()
    def chat(
        self,
        messages: list,
        model: str = "ernie-4.0",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        token = self._get_access_token()
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        url = f"{self._model_endpoint(model)}?access_token={token}"

        resp = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"ERNIE API 错误 [{resp.status_code}]: {resp.text}")

        data = resp.json()
        usage = data.get("usage", {})
        logger.info(
            "百度文心 [%s] ↑%d ↓%d tokens",
            model,
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )
        return data


class SparkAPI:
    """讯飞星火 Spark API (HTTP 长轮询模式)."""

    BASE_URL = "https://spark-api.xf-yun.com/v3.5/chat"

    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.app_id = app_id or os.getenv("SPARK_APP_ID")
        self.api_key = api_key or os.getenv("SPARK_API_KEY")
        self.api_secret = api_secret or os.getenv("SPARK_API_SECRET")
        if not all([self.app_id, self.api_key, self.api_secret]):
            raise ValueError("请设置 SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET")

    def _build_auth_url(self) -> str:
        """构建带签名的 URL (简化实现, 仅用于 HTTP 模式)."""
        import urllib.parse
        from hashlib import md5
        from datetime import datetime

        now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        signature_raw = f"{self.app_id}\n{now}"
        signature = md5(signature_raw.encode()).hexdigest()

        params = urllib.parse.urlencode({
            "appid": self.app_id,
            "timestamp": now,
            "signature": signature,
        })
        return f"{self.BASE_URL}?{params}"

    @retry_on_failure()
    def chat(
        self,
        messages: list,
        model: str = "spark-3.5",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        # 讯飞 HTTP API 需要将 messages 转为对话历史
        payload = {
            "header": {"app_id": self.app_id},
            "parameter": {
                "chat": {
                    "domain": "generalv3.5",
                    "temperature": temperature,
                }
            },
            "payload": {
                "message": {
                    "text": messages,
                }
            },
        }

        url = self._build_auth_url()
        resp = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"Spark API 错误 [{resp.status_code}]: {resp.text}")

        data = resp.json()
        usage = data.get("payload", {}).get("usage", {}).get("text", {})
        logger.info(
            "讯飞星火 [%s] ↑%d ↓%d tokens",
            model,
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )
        return data


# ---------------------------------------------------------------------------
# API 工厂 — 统一调用入口
# ---------------------------------------------------------------------------

_platform_registry = {
    "deepseek": DeepSeekAPI,
    "dashscope": DashScopeAPI,
    "qwen": DashScopeAPI,          # 别名
    "ernie": ERNIEAPI,
    "baidu": ERNIEAPI,             # 别名
    "spark": SparkAPI,
    "xunfei": SparkAPI,            # 别名
}


def create_api(platform: str, **kwargs):
    """
    创建指定平台的 API 客户端.

    参数:
        platform: deepseek / dashscope(qwen) / ernie(baidu) / spark(xunfei)
        **kwargs: 传入对应客户端的 API Key 等参数

    返回:
        客户端实例 (具有 chat() 方法)
    """
    platform = platform.lower().strip()
    cls = _platform_registry.get(platform)
    if not cls:
        raise ValueError(
            f"不支持的平台 '{platform}'。可选: {list(_platform_registry.keys())}"
        )
    return cls(**kwargs)


def call_ai(
    platform: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    stream: bool = False,
    **kwargs,
) -> dict:
    """
    统一 AI 调用接口 — 一行代码切换任意模型.

    参数:
        platform:      模型平台 (deepseek / qwen / ernie / spark)
        prompt:        用户输入文本
        system_prompt: 系统提示词 (可选)
        model:         模型名称 (可选, 各平台有默认值)
        temperature:   生成温度 (0~2)
        stream:        是否流式输出
        **kwargs:      透传给平台客户端的额外参数

    返回:
        原始 API JSON 响应 (dict)
    """
    client = create_api(platform, **kwargs)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # 自动选择默认模型
    _default_model = {
        "deepseek": "deepseek-chat",
        "qwen": "qwen-max",
        "dashscope": "qwen-max",
        "ernie": "ernie-4.0",
        "baidu": "ernie-4.0",
        "spark": "spark-3.5",
        "xunfei": "spark-3.5",
    }
    if model is None:
        model = _default_model.get(platform, "deepseek-chat")

    logger.info(
        "调用 [%s/%s] | prompt=%d字 ~%d tokens | temperature=%.1f",
        platform, model, len(prompt), estimate_tokens(prompt), temperature,
    )

    result = client.chat(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=stream,
    )

    logger.info("调用成功 [%s/%s]", platform, model)
    return result


def extract_content(response: dict) -> str:
    """
    从各平台返回的 JSON 中统一提取文本内容.

    参数:
        response: call_ai() 返回的原始 dict

    返回:
        模型生成的文本 (str)
    """
    # DeepSeek / OpenAI 格式
    choices = response.get("choices")
    if choices:
        return choices[0].get("message", {}).get("content", "")

    # DashScope 格式
    output = response.get("output")
    if output:
        choices = output.get("choices")
        if choices:
            return choices[0].get("message", {}).get("content", "")

    # ERNIE 格式
    result = response.get("result")
    if result:
        return result

    # Spark 格式
    payload = response.get("payload", {})
    choices = payload.get("choices", {})
    if choices:
        texts = choices.get("text", [])
        if texts:
            return texts[0].get("content", "")

    raise ValueError(f"无法从响应中提取内容: {json.dumps(response, ensure_ascii=False)[:200]}")


# ---------------------------------------------------------------------------
# 使用示例
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # 用法: python api_wrapper.py <platform> "<prompt>"
    # 例如: python api_wrapper.py deepseek "你好, 请介绍一下你自己"
    #       python api_wrapper.py qwen "用 Python 写一个二分查找"

    platform = sys.argv[1] if len(sys.argv) > 1 else "deepseek"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "请用一句话介绍你自己"

    print(f"\n{'='*60}")
    print(f"  调用平台: {platform}")
    print(f"  提示词:   {prompt}")
    print(f"{'='*60}\n")

    try:
        resp = call_ai(platform, prompt)
        content = extract_content(resp)
        print(f"\n>>> 回复:\n{content}\n")
    except Exception as e:
        logger.error("调用失败: %s", e)
        sys.exit(1)
