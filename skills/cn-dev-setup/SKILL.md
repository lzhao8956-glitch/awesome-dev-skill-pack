---
name: cn-dev-setup
description: "一键配置国内AI开发环境——DeepSeek/通义千问/豆包/百度文心/讯飞星火API适配，WSL/Windows双环境自动检测"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [china, dev-setup, api, wsl, deepseek, qwen]
    related_skills: [cn-coder, wsl-helper]
---

# 🇨🇳 CN Dev Setup

## 概述

专为中国开发者设计的AI开发环境配置 Skill。自动检测你的操作系统和环境，一键配置国内各大AI平台的API接入。

## 使用场景

- 你刚装了 Hermes Agent / Claude Code，需要配置国内的 API Key
- 你在 WSL/Windows/Mac 之间切换，需要统一配置
- 你想用 DeepSeek/通义千问 替代 OpenAI

## 支持的国内API

| 平台 | 配置变量 | 免费额度 |
|------|---------|---------|
| DeepSeek | DEEPSEEK_API_KEY | 注册送500万token |
| 通义千问 (Qwen) | DASHSCOPE_API_KEY | 每月100万token |
| 豆包 (Doubao) | DOUBAO_API_KEY | 新用户送额度 |
| 百度文心 (ERNIE) | ERNIE_API_KEY | 调用量免费 |
| 讯飞星火 (Spark) | SPARK_API_KEY | 注册送额度 |

## 快速配置

### 自动检测环境

```bash
# Hermes Agent 加载此 Skill 后自动运行
python3 -c "
import platform, os, sys
print(f'系统: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'WSL: {\"是\" if \"microsoft\" in platform.uname().release.lower() else \"否\"}')
print(f'Windows路径: {\"可访问\" if os.path.isdir(\"/mnt/c\") else \"不可访问\"}')
"
```

### 配置 API Key

在 `~/.hermes/.env` 中添加：

```env
# DeepSeek（推荐，性价比最高）
DEEPSEEK_API_KEY=sk-your-key-here

# 通义千问
DASHSCOPE_API_KEY=sk-your-key-here

# 百度文心
ERNIE_API_KEY=your-key-here
ERNIE_SECRET_KEY=your-secret-here
```

## 常见问题

1. **WSL 里调不了 Windows exe？** → 检查 /etc/wsl.conf 是否启用了 [interop]
2. **API 连不上？** → 国内可能需要配置代理
3. **环境变量不生效？** → 重启 Hermes 或 source ~/.hermes/.env
