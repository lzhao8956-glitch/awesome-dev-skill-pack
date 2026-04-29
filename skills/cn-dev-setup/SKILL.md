---
name: cn-dev-setup
description: "一键配置国内AI开发环境——DeepSeek/通义千问/豆包/百度文心/讯飞星火API适配，WSL/Windows/Mac三环境自动检测，代理配置，故障排查"
version: 2.0.0
author: awesome-dev-skill-pack
license: MIT
metadata:
  hermes:
    tags: [china, dev-setup, api, wsl, deepseek, qwen, doubao, ernie, spark, proxy, env]
    related_skills: [cn-coder, wsl-helper, deepseek-adapter, hermes-agent]
    setup_script: setup.sh
---

# 🇨🇳 CN Dev Setup — 国内开发环境配置

专为中国开发者打造的 Her mes Agent 环境配置 Skill。自动检测 WSL / Windows / macOS 操作系统，
一键配置 DeepSeek、通义千问、豆包、百度文心、讯飞星火等国内主流 AI 平台的 API 接入，
同时提供 OpenAI 的国内可访问替代方案和全面的故障排查指南。

---

## 目录

- [功能概述](#功能概述)
- [环境自动检测](#环境自动检测)
- [支持的国内 API 平台](#支持的国内-api-平台)
- [一键配置 (setup.sh)](#一键配置-setupsh)
- [手动配置](#手动配置)
- [代理配置（国内访问 OpenAI 替代方案）](#代理配置国内访问-openai-替代方案)
- [环境变量说明](#环境变量说明)
- [故障排查指南](#故障排查指南)
- [开发者说明](#开发者说明)

---

## 功能概述

| 功能 | 说明 |
|------|------|
| 环境检测 | 自动识别 WSL2 / Windows / macOS，检测 Python、Git、curl 等依赖 |
| API 配置 | 支持 5 大国内 AI 平台的一键式 API Key 录入与校验 |
| 环境变量管理 | 所有配置写入 `~/.hermes/.env`，与 Hermes Agent 原生兼容 |
| 代理配置 | OpenA I 国内替代方案：API 中转代理、Cloudflare Workers 等 |
| 故障排查 | 常见网络、权限、环境变量问题的诊断与修复 |
| 一键脚本 | 配套 `setup.sh` 交互式脚本，全程引导 |

---

## 环境自动检测

加载此 Skill 后，Hermes Agent 会自动执行以下检测：

```bash
python3 -c "
import platform, os, sys, subprocess, shutil

info = {}

# 1. 操作系统检测
sys_name = platform.system()
info['sys_name'] = sys_name
info['release'] = platform.release()

# 2. WSL 检测（关键：区分 WSL1 / WSL2）
uname_r = platform.uname().release.lower()
if 'microsoft' in uname_r or 'wsl' in uname_r:
    info['is_wsl'] = True
    if 'wsl2' in uname_r:
        info['wsl_version'] = 2
    else:
        info['wsl_version'] = 1
    # 检测 Windows 文件系统可访问性
    info['win_fs'] = os.path.isdir('/mnt/c')
    # 检测 wsl.conf
    info['wsl_conf'] = os.path.isfile('/etc/wsl.conf')
else:
    info['is_wsl'] = False
    info['wsl_version'] = None
    info['win_fs'] = False

# 3. macOS 检测
info['is_mac'] = sys_name == 'Darwin'

# 4. 依赖检测
info['has_python3'] = shutil.which('python3') is not None
info['has_curl'] = shutil.which('curl') is not None
info['has_git'] = shutil.which('git') is not None

# 5. Her mes 环境检测
hermes_env = os.path.expanduser('~/.hermes/.env')
info['hermes_env_exists'] = os.path.isfile(hermes_env)

# 6. 已配置的 API 检测
configured_keys = []
if info['hermes_env_exists']:
    with open(hermes_env) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            if '=' in line and not line.startswith('export '):
                key = line.split('=')[0].strip()
                configured_keys.append(key)
info['configured_keys'] = configured_keys

# 输出
print('=== CN Dev Setup 环境检测 ===')
print(f'操作系统: {info[\"sys_name\"]} {info[\"release\"]}')
if info['is_wsl']:
    print(f'WSL版本: WSL{info[\"wsl_version\"]}')
    print(f'Windows文件系统: {\"✅ 可访问\" if info[\"win_fs\"] else \"❌ 不可访问\"}')
    print(f'/etc/wsl.conf: {\"✅ 存在\" if info[\"wsl_conf\"] else \"⚠️ 不存在\"}')
elif info['is_mac']:
    print('环境: macOS')
else:
    print('环境: 原生 Linux')

print(f'Python3: {\"✅\" if info[\"has_python3\"] else \"❌\"}')
print(f'curl: {\"✅\" if info[\"has_curl\"] else \"❌\"}')
print(f'git: {\"✅\" if info[\"has_git\"] else \"❌\"}')
print(f'~/.hermes/.env: {\"✅ 存在\" if info[\"hermes_env_exists\"] else \"⚠️ 不存在，需要配置\"}')
if configured_keys:
    print(f'已配置的 Key: {', '.join(configured_keys)}')
else:
    print('已配置的 Key: 暂无')
print('===============================')
"
```

### 检测结果解读

| 输出 | 含义 | 建议操作 |
|------|------|---------|
| `操作系统: Linux ... microsoft` | 你在 WSL2 中 | `/mnt/c/` 可访问 Windows 文件 |
| `操作系统: Darwin` | 你在 macOS 上 | 无需 WSL 配置 |
| `Windows文件系统: ❌` | WSL 未挂载 Windows 分区 | 检查 `/etc/wsl.conf` 中 `[interop] enabled=true` |
| `~/.hermes/.env: ⚠️ 不存在` | 尚未配置任何 API | 执行 `setup.sh` 一键配置 |

---

## 支持的国内 API 平台

| 平台 | 配置变量 | 获取地址 | 免费额度 | 推荐模型 |
|------|---------|---------|---------|---------|
| **DeepSeek** | `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com) | 注册送 500 万 token | deepseek-chat |
| **通义千问 (Qwen)** | `DASHSCOPE_API_KEY` | [dashscope.aliyun.com](https://dashscope.aliyun.com) | 每月 100 万 token | qwen-plus / qwen-max |
| **豆包 (Doubao)** | `DOUBAO_API_KEY` | [console.volcengine.com](https://console.volcengine.com/ark) | 新用户送 50 元额度 | doubao-pro-32k |
| **百度文心 (ERNIE)** | `ERNIE_API_KEY` + `ERNIE_SECRET_KEY` | [console.bce.baidu.com](https://console.bce.baidu.com/qianwen) | 调用量免费 | ernie-4.0-8k |
| **讯飞星火 (Spark)** | `SPARK_API_KEY` + `SPARK_API_SECRET` + `SPARK_APP_ID` | [xinghuo.xfyun.cn](https://xinghuo.xfyun.cn) | 注册送额度 | spark-4.0 |

> 💡 **推荐优先使用 DeepSeek**：性价比最高，兼容 OpenAI API 格式，迁移成本最低。

---

## 一键配置 (setup.sh)

同目录下的 `setup.sh` 提供交互式一键配置。运行方法：

```bash
# 确保脚本有执行权限
chmod +x /path/to/cn-dev-setup/setup.sh

# 运行配置向导
./path/to/cn-dev-setup/setup.sh
```

### setup.sh 功能说明

1. **环境检测** — 自动判断 WSL/Windows/Mac
2. **API Key 录入** — 逐个引导输入各平台 API Key（支持跳过）
3. **Key 校验** — 对 DeepSeek 和通义千问进行真实 API 调用来验证 Key 有效性
4. **环境变量写入** — 自动写入 `~/.hermes/.env` 并创建 shell 加载脚本
5. **代理配置** — 选择 OpenAI 代理模式（可选）
6. **生成摘要** — 最后展示所有已配置的平台和未配置的平台

### 交互流程示例

```
╔══════════════════════════════════╗
║   🇨🇳 CN Dev Setup 一键配置     ║
║   国内AI开发环境配置向导          ║
╚══════════════════════════════════╝

[1/5] 环境检测...
→ 检测到: WSL2 (Ubuntu)
→ Python3: ✅ | curl: ✅ | git: ✅

[2/5] 配置 DeepSeek API Key
→ 请输入 Key (回车跳过): sk-****************

[3/5] 校验 DeepSeek Key...
→ ✅ 校验通过！余额: 剩余 4,200,000 tokens

[4/5] 是否配置 OpenAPI 国内代理? (y/n): y
→ 选择代理: 1) 自建中转  2) Cloudflare Workers  3) 第三方代理

[5/5] 写入环境变量...
→ ✅ 已写入 ~/.hermes/.env
→ ✅ Shell 加载脚本已生成

📋 配置摘要:
   ✅ DeepSeek   | 已配置 (余额约420万tokens)
   ⬜ 通义千问   | 已跳过
   ⬜ 豆包       | 已跳过
   ⬜ 百度文心   | 已跳过
   ⬜ 讯飞星火   | 已跳过
   ✅ OpenAI代理 | ai-proxy.example.com

🔄 重启 Hermes Agent 或执行以下命令加载配置:
   source ~/.hermes/.env
```

---

## 手动配置

如果你不想使用交互式脚本，也可以手动配置。

### 1. 创建环境变量文件

```bash
mkdir -p ~/.hermes
touch ~/.hermes/.env
chmod 600 ~/.hermes/.env
```

### 2. 添加 API Key

编辑 `~/.hermes/.env`，按需添加：

```env
# ============================================
# 🇨🇳 CN Dev Setup — API 环境变量配置
# ============================================

# --- DeepSeek (推荐) ---
# 获取: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# --- 通义千问 (Qwen / DashScope) ---
# 获取: https://dashscope.aliyun.com
DASHSCOPE_API_KEY=sk-your-dashscope-key-here

# --- 豆包 (Doubao / 火山引擎) ---
# 获取: https://console.volcengine.com/ark
DOUBAO_API_KEY=your-doubao-key-here

# --- 百度文心 (ERNIE) ---
# 获取: https://console.bce.baidu.com/qianwen
ERNIE_API_KEY=your-ernie-api-key
ERNIE_SECRET_KEY=your-ernie-secret-key

# --- 讯飞星火 (Spark) ---
# 获取: https://xinghuo.xfyun.cn
SPARK_APP_ID=your-spark-app-id
SPARK_API_KEY=your-spark-api-key
SPARK_API_SECRET=your-spark-api-secret
```

### 3. 加载环境变量

```bash
# 手动加载
set -a; source ~/.hermes/.env; set +a

# 或添加到 shell 配置文件（推荐）
echo 'set -a; [ -f ~/.hermes/.env ] && source ~/.hermes/.env; set +a' >> ~/.bashrc
```

### 4. 验证配置

```bash
python3 -c "
import os
keys = ['DEEPSEEK_API_KEY', 'DASHSCOPE_API_KEY', 'DOUBAO_API_KEY', 'ERNIE_API_KEY', 'SPARK_API_KEY']
for k in keys:
    v = os.environ.get(k, '')
    print(f'  {\"✅\" if v else \"❌\"} {k}: {\"已配置 (长度\"+str(len(v))+\")\" if v else \"未配置\"} ')
"
```

---

## 代理配置（国内访问 OpenAI 替代方案）

由于国内无法直接访问 OpenAI API，以下是几种经过验证的替代方案。

### 方案一：API 中转代理（推荐）

选择一家稳定的国内 API 中转服务，将 `https://api.openai.com` 替换为中转地址。

```env
# 在 ~/.hermes/.env 中添加
OPENAI_API_BASE=https://your-proxy-domain.com/v1
OPENAI_API_KEY=sk-your-proxy-key-here
```

常见中转服务：

| 服务商 | 特点 | 参考地址 |
|--------|------|---------|
| API2D | 稳定，支持支付宝 | https://api2d.com |
| CloseAI | 价格透明 | https://closeai-xxx.com |
| 自建中转 | 用 Cloudflare Workers 搭建 | 见下文 |

### 方案二：Cloudflare Workers 中转（免费/低成本）

如果你的域名托管在 Cloudflare，可以搭建自己的中转：

```javascript
// Cloudflare Worker 脚本
export default {
  async fetch(request) {
    const url = new URL(request.url);
    url.host = 'api.openai.com';
    const newRequest = new Request(url, request);
    newRequest.headers.set('Host', 'api.openai.com');
    return fetch(newRequest);
  }
}
```

部署后，在 `~/.hermes/.env` 中配置：

```env
OPENAI_API_BASE=https://your-worker.workers.dev/v1
```

### 方案三：直接使用国内模型替代 OpenAI

在 Hermes Agent 的 `.env` 中直接设置使用 DeepSeek 代替 OpenAI：

```env
# 直接用 DeepSeek 替代 OpenAI
HERMES_DEFAULT_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

对于 Claude Code 用户，使用通义千问替代：

```env
# Claude Code + 通义千问
ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_API_KEY=sk-your-key-here
```

### 环境变量汇总

```env
# ===== OpenAI 替代方案配置 =====

# 方式 A: 直接使用国内 DeepSeek
HERMES_DEFAULT_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 方式 B: 使用 OpenAI 中转代理
# OPENAI_API_BASE=https://your-proxy.com/v1
# OPENAI_API_KEY=sk-xxx

# 方式 C: 使用通义千问作为 Anthropic 替代
# ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# DASHSCOPE_API_KEY=sk-xxx
```

---

## 环境变量说明

所有环境变量均存储在 `~/.hermes/.env`，以下是完整字段说明：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | 推荐 | DeepSeek API Key |
| `DEEPSEEK_API_BASE` | 否 | DeepSeek API 地址，默认 `https://api.deepseek.com/v1` |
| `DASHSCOPE_API_KEY` | 可选 | 通义千问/DashScope API Key |
| `DOUBAO_API_KEY` | 可选 | 豆包/火山引擎 API Key |
| `ERNIE_API_KEY` | 可选 | 百度文心 API Key |
| `ERNIE_SECRET_KEY` | 可选 | 百度文心 Secret Key |
| `SPARK_APP_ID` | 可选 | 讯飞星火 App ID |
| `SPARK_API_KEY` | 可选 | 讯飞星火 API Key |
| `SPARK_API_SECRET` | 可选 | 讯飞星火 API Secret |
| `OPENAI_API_BASE` | 可选 | OpenAI API 中转地址 |
| `OPENAI_API_KEY` | 可选 | OpenAI/中转 API Key |
| `HERMES_DEFAULT_PROVIDER` | 可选 | Hermes 默认提供商，设为 `deepseek` 以使用国内模型 |
| `ANTHROPIC_BASE_URL` | 可选 | Anthropic API 替代地址（通义千问兼容模式） |

---

## 故障排查指南

### 1. 环境变量不生效

**现象**: `echo $DEEPSEEK_API_KEY` 返回空

**排查步骤**:

```bash
# 1. 检查文件是否存在
ls -la ~/.hermes/.env

# 2. 检查文件内容
cat ~/.hermes/.env | head -20

# 3. 手动加载
set -a; source ~/.hermes/.env; set +a

# 4. 验证
echo $DEEPSEEK_API_KEY

# 5. 检查是否已添加到 shell 配置
grep -n 'hermes/.env' ~/.bashrc ~/.zshrc 2>/dev/null
```

**解决**: 如果未添加到 shell 配置，执行：
```bash
echo 'set -a; [ -f ~/.hermes/.env ] && source ~/.hermes/.env; set +a' >> ~/.bashrc
source ~/.bashrc
```

### 2. WSL 无法访问 Windows 文件

**现象**: `/mnt/c/` 目录不存在或为空

**排查与解决**:

```bash
# 1. 检查 WSL 版本
wsl --version  # 或 uname -r | grep WSL

# 2. 检查 /etc/wsl.conf
cat /etc/wsl.conf
```

如果 `/etc/wsl.conf` 缺失，创建：
```ini
# /etc/wsl.conf
[interop]
enabled = true
appendWindowsPath = true

[automount]
enabled = true
mountFsTab = true
root = /mnt/
options = "metadata,umask=22,fmask=11"
```

然后重启 WSL：
```powershell
# 在 Windows PowerShell 中执行
wsl --shutdown
wsl
```

### 3. API 连接失败 / 网络超时

**现象**: Hermes 报错 `ConnectionError` 或 `timeout`

**诊断脚本**:

```bash
python3 -c "
import urllib.request, json, sys

tests = [
    ('DeepSeek', 'https://api.deepseek.com/v1/models'),
    ('通义千问', 'https://dashscope.aliyuncs.com/compatible-mode/v1/models'),
    ('OpenAI(代理)', 'https://api.openai.com/v1/models'),
]

for name, url in tests:
    try:
        req = urllib.request.Request(url, method='GET')
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        models = data.get('data', [])
        print(f'  ✅ {name}: {url} — 可达 ({len(models)} 个模型)')
    except Exception as e:
        err = str(e)
        if 'Name or service not known' in err or 'getaddrinfo' in err:
            print(f'  ❌ {name}: DNS 解析失败 — 请检查网络或配置代理')
        elif 'Timeout' in err or 'timed out' in err:
            print(f'  ❌ {name}: 连接超时 — 可能需要代理')
        elif 'Unauthorized' in err or '401' in err:
            print(f'  ⚠️ {name}: 服务器可达，但 API Key 无效 (HTTP 401)')
        else:
            print(f'  ❌ {name}: {err[:80]}')
"
```

**常见网络问题及解决**:

| 问题 | 诊断结果 | 解决方案 |
|------|---------|---------|
| DNS 解析失败 | `Name or service not known` | `echo \"nameserver 8.8.8.8\" > /etc/resolv.conf` |
| 连接超时 | `timed out` | 配置代理或使用国内 API |
| SSL 证书错误 | `certificate verify failed` | `pip install --upgrade certifi` |
| 代理冲突 | `Connection refused` | 检查 `http_proxy`/`https_proxy` 环境变量 |

### 4. DeepSeek Key 校验失败

```bash
# 验证 DeepSeek API Key 是否有效
curl -s -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  https://api.deepseek.com/v1/models | python3 -m json.tool 2>/dev/null || \
  echo "❌ Key 无效或网络不可达"
```

### 5. 权限问题

**现象**: `Permission denied` 或 `~/.hermes/.env` 无法写入

```bash
# 修复权限
chmod 755 ~/.hermes
chmod 600 ~/.hermes/.env
ls -la ~/.hermes/
```

### 6. Shell 环境变量污染

**现象**: 多个 `API_KEY` 变量冲突

```bash
# 检查是否有冲突的环境变量
env | grep -E 'API_KEY|API_SECRET|APP_ID' | sort

# 如果冲突来自系统级配置，检查
cat /etc/environment 2>/dev/null
```

---

## 开发者说明

### 文件结构

```
cn-dev-setup/
├── SKILL.md          # 本文件 — Skill 元数据和文档
└── setup.sh          # 一键配置脚本（交互式）
```

### 扩展现有配置

如果想添加更多国内平台支持，在 SKILL.md 的「支持的 API 平台」
表格和 `setup.sh` 的配置列表中添加对应条目即可。

### 依赖要求

- Python 3.6+
- curl（用于 API 校验）
- Hermes Agent（自动加载 `~/.hermes/.env`）

---

*🇨🇳 CN Dev Setup v2.0 — 让国内开发者也能畅享 AI 编程的乐趣。*
