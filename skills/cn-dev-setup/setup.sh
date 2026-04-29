#!/usr/bin/env bash
# ==============================================================
# 🇨🇳 CN Dev Setup — 国内AI开发环境一键配置脚本
# 版本: 2.0.0
# 描述: 交互式配置 DeepSeek/通义千问/豆包/百度文心/讯飞星火 API
#       自动检测 WSL/Windows/Mac 环境，写入 ~/.hermes/.env
# ==============================================================

set -euo pipefail

# ── 颜色定义 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ── 工具函数 ──
info()  { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }
header() { echo -e "\n${CYAN}═══════════════════════════════════════${NC}"; echo -e "${BOLD} $1${NC}"; echo -e "${CYAN}═══════════════════════════════════════${NC}"; }
prompt() { echo -e -n "${BLUE}?${NC} $1 "; }

# ── Banner ──
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║   🇨🇳 CN Dev Setup — 一键配置            ║"
echo "║   国内AI开发环境配置向导                  ║"
echo "║   版本 2.0.0                             ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ══════════════════════════════════════════════════════════
# 第一步: 环境检测
# ══════════════════════════════════════════════════════════
header "[1/5] 环境检测"

# OS 检测
OS=""
case "$(uname -s)" in
    Linux*) OS="Linux";;
    Darwin*) OS="macOS";;
    CYGWIN*|MINGW*|MSYS*) OS="Windows";;
    *) OS="未知";;
esac

# WSL 检测
IS_WSL=false
WSL_VER=""
if [ -f /proc/version ] && grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
    if grep -qi wsl2 /proc/version 2>/dev/null || uname -r | grep -qi wsl2; then
        WSL_VER="2"
    else
        WSL_VER="1"
    fi
fi

# 依赖检测
HAS_PYTHON3=false; command -v python3 &>/dev/null && HAS_PYTHON3=true
HAS_CURL=false;   command -v curl &>/dev/null   && HAS_CURL=true
HAS_GIT=false;    command -v git &>/dev/null    && HAS_GIT=true

# 输出检测结果
info "操作系统: $OS"
if [ "$IS_WSL" = true ]; then
    info "WSL版本: WSL$WSL_VER"
    if [ -d /mnt/c ]; then
        success "Windows文件系统: 可访问"
    else
        warn "Windows文件系统: 不可访问（/mnt/c 不存在）"
    fi
    if [ -f /etc/wsl.conf ]; then
        success "/etc/wsl.conf: 存在"
    else
        warn "/etc/wsl.conf: 不存在（建议创建，详见故障排查指南）"
    fi
fi
$HAS_PYTHON3 && success "Python3: 可用" || error "Python3: 未安装"
$HAS_CURL && success "curl: 可用" || error "curl: 未安装"
$HAS_GIT && success "git: 可用" || warn "git: 未安装（部分功能受限）"

if ! $HAS_PYTHON3; then
    if [ "$OS" = "macOS" ]; then
        info "请安装 Python3: brew install python"
    elif [ "$OS" = "Linux" ]; then
        info "请安装 Python3: sudo apt install python3 python3-pip"
    fi
    exit 1
fi

# ══════════════════════════════════════════════════════════
# 第二步: Her mes 环境初始化
# ══════════════════════════════════════════════════════════
header "[2/5] Her mes 环境初始化"

HERMES_DIR="$HOME/.hermes"
ENV_FILE="$HERMES_DIR/.env"

mkdir -p "$HERMES_DIR"

if [ -f "$ENV_FILE" ]; then
    warn "检测到已有 $ENV_FILE"
    prompt "是否覆盖? (y/N):"
    read -r overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        info "保留原有配置，新 Key 将追加到文件末尾"
    else
        cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"
        success "已备份旧文件到 ${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"
        : > "$ENV_FILE"
        success "已清空旧配置"
    fi
else
    touch "$ENV_FILE"
fi

chmod 600 "$ENV_FILE"

# 写入文件头
if ! grep -q "CN Dev Setup" "$ENV_FILE" 2>/dev/null; then
    cat >> "$ENV_FILE" << 'EOF'
# ============================================
# 🇨🇳 CN Dev Setup — API 环境变量配置
# 由 setup.sh 自动生成，手动修改请谨慎
# ============================================

EOF
fi

# ══════════════════════════════════════════════════════════
# 第三步: API Key 录入与写入
# ══════════════════════════════════════════════════════════
header "[3/5] API Key 配置"

# 定义支持的平台
declare -A PLATFORMS
PLATFORMS=(
    ["DeepSeek"]="DEEPSEEK_API_KEY"
    ["通义千问"]="DASHSCOPE_API_KEY"
    ["豆包"]="DOUBAO_API_KEY"
    ["百度文心"]="ERNIE_API_KEY"
    ["讯飞星火"]="SPARK_API_KEY"
)

# 支持多字段的平台
declare -A EXTRA_FIELDS
EXTRA_FIELDS["百度文心"]="ERNIE_SECRET_KEY"
EXTRA_FIELDS["讯飞星火"]="SPARK_API_SECRET,SPARK_APP_ID"

# 获取 Key 的指导 URL
declare -A KEY_URLS
KEY_URLS["DeepSeek"]="https://platform.deepseek.com/api_keys"
KEY_URLS["通义千问"]="https://dashscope.aliyun.com"
KEY_URLS["豆包"]="https://console.volcengine.com/ark"
KEY_URLS["百度文心"]="https://console.bce.baidu.com/qianwen"
KEY_URLS["讯飞星火"]="https://xinghuo.xfyun.cn"

configured_platforms=()
skipped_platforms=()

for platform in "DeepSeek" "通义千问" "豆包" "百度文心" "讯飞星火"; do
    var_name="${PLATFORMS[$platform]}"
    url="${KEY_URLS[$platform]}"

    echo ""
    prompt "配置 ${BOLD}$platform${NC} API Key? (y/N):"
    read -r choice

    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        skipped_platforms+=("$platform")
        warn "跳过 $platform"
        continue
    fi

    # 显示获取地址
    info "获取 Key: $url"

    # 读取主 Key
    prompt "请输入 $var_name:"
    read -rs key_value
    echo ""

    if [ -z "$key_value" ]; then
        warn "输入为空，跳过 $platform"
        skipped_platforms+=("$platform")
        continue
    fi

    # 写入主 Key
    if grep -q "^${var_name}=" "$ENV_FILE" 2>/dev/null; then
        sed -i "s|^${var_name}=.*|${var_name}=${key_value}|" "$ENV_FILE"
    else
        echo "${var_name}=${key_value}" >> "$ENV_FILE"
    fi
    success "$var_name 已写入"

    # 处理平台特有额外字段
    case "$platform" in
        百度文心)
            prompt "请输入 ERNIE_SECRET_KEY:"
            read -rs secret_key
            echo ""
            if [ -n "$secret_key" ]; then
                if grep -q "^ERNIE_SECRET_KEY=" "$ENV_FILE" 2>/dev/null; then
                    sed -i "s|^ERNIE_SECRET_KEY=.*|ERNIE_SECRET_KEY=${secret_key}|" "$ENV_FILE"
                else
                    echo "ERNIE_SECRET_KEY=${secret_key}" >> "$ENV_FILE"
                fi
                success "ERNIE_SECRET_KEY 已写入"
            fi
            ;;
        讯飞星火)
            prompt "请输入 SPARK_APP_ID:"
            read -r app_id
            if [ -n "$app_id" ]; then
                if grep -q "^SPARK_APP_ID=" "$ENV_FILE" 2>/dev/null; then
                    sed -i "s|^SPARK_APP_ID=.*|SPARK_APP_ID=${app_id}|" "$ENV_FILE"
                else
                    echo "SPARK_APP_ID=${app_id}" >> "$ENV_FILE"
                fi
                success "SPARK_APP_ID 已写入"
            fi
            prompt "请输入 SPARK_API_SECRET:"
            read -rs secret
            echo ""
            if [ -n "$secret" ]; then
                if grep -q "^SPARK_API_SECRET=" "$ENV_FILE" 2>/dev/null; then
                    sed -i "s|^SPARK_API_SECRET=.*|SPARK_API_SECRET=${secret}|" "$ENV_FILE"
                else
                    echo "SPARK_API_SECRET=${secret}" >> "$ENV_FILE"
                fi
                success "SPARK_API_SECRET 已写入"
            fi
            ;;
    esac

    configured_platforms+=("$platform")

    # 对 DeepSeek 进行 Key 校验
    if [ "$platform" = "DeepSeek" ] && $HAS_CURL; then
        info "校验 DeepSeek API Key..."
        if curl -s --max-time 5 -H "Authorization: Bearer ${key_value}" \
            https://api.deepseek.com/v1/models | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = data.get('data', [])
    if models:
        print(f'✅ 校验通过！发现 {len(models)} 个可用模型')
    else:
        print('⚠️ 服务器响应，但未返回模型列表')
except Exception:
    print('❌ Key 无效或网络不可达')
" 2>/dev/null; then
            : # ok
        else
            warn "DeepSeek Key 校验失败，但已保存配置，稍后可重试"
        fi
    fi
done

# ══════════════════════════════════════════════════════════
# 第四步: 代理/OpenAI 替代配置
# ══════════════════════════════════════════════════════════
header "[4/5] OpenAI 代理配置"

echo "是否需要配置 OpenAI 国内代理（用于访问 ChatGPT API）?"
echo "  1) 跳过，暂不需要"
echo "  2) 使用国内 API 中转服务"
echo "  3) 使用 DeepSeek 作为默认提供商（推荐）"
echo "  4) 使用通义千问兼容模式（替代 Claude）"
prompt "请选择 [1-4] (默认 3):"
read -r proxy_choice

case "${proxy_choice:-3}" in
    2)
        prompt "请输入中转代理地址 (例如 https://your-proxy.com/v1):"
        read -r proxy_url
        if [ -n "$proxy_url" ]; then
            echo "OPENAI_API_BASE=${proxy_url}" >> "$ENV_FILE"
            success "OPENAI_API_BASE 已配置"
            prompt "请输入中转 API Key:"
            read -rs proxy_key
            echo ""
            if [ -n "$proxy_key" ]; then
                echo "OPENAI_API_KEY=${proxy_key}" >> "$ENV_FILE"
                success "OPENAI_API_KEY 已配置"
            fi
        fi
        ;;
    3)
        if grep -q "^DEEPSEEK_API_KEY=" "$ENV_FILE"; then
            echo "HERMES_DEFAULT_PROVIDER=deepseek" >> "$ENV_FILE"
            echo "DEEPSEEK_API_BASE=https://api.deepseek.com/v1" >> "$ENV_FILE"
            success "默认提供商设为 DeepSeek"
        else
            warn "尚未配置 DeepSeek Key，请在后续补充"
            echo "# HERMES_DEFAULT_PROVIDER=deepseek" >> "$ENV_FILE"
            echo "# DEEPSEEK_API_BASE=https://api.deepseek.com/v1" >> "$ENV_FILE"
        fi
        ;;
    4)
        if grep -q "^DASHSCOPE_API_KEY=" "$ENV_FILE"; then
            echo "ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1" >> "$ENV_FILE"
            success "通义千问兼容模式已启用（替代 Claude）"
        else
            warn "尚未配置通义千问 Key，请在后续补充"
            echo "# ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1" >> "$ENV_FILE"
        fi
        ;;
    *)
        info "跳过代理配置"
        ;;
esac

# ══════════════════════════════════════════════════════════
# 第五步: Shell 集成 & 最终摘要
# ══════════════════════════════════════════════════════════
header "[5/5] Shell 集成 & 完成"

# 生成 shell 加载配置
SHELL_RC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

LOAD_LINE='set -a; [ -f "$HOME/.hermes/.env" ] && source "$HOME/.hermes/.env"; set +a'

if grep -q "hermes/.env" "$SHELL_RC" 2>/dev/null; then
    success "Shell 加载配置已存在 ($SHELL_RC)"
else
    echo "" >> "$SHELL_RC"
    echo "# 🇨🇳 CN Dev Setup — 自动加载环境变量" >> "$SHELL_RC"
    echo "$LOAD_LINE" >> "$SHELL_RC"
    success "已添加到 $SHELL_RC"
fi

# 立即加载
eval "$LOAD_LINE"

# 最终摘要
header "📋 配置摘要"

echo ""
echo -e " ${BOLD}已配置的平台:${NC}"
if [ ${#configured_platforms[@]} -eq 0 ]; then
    echo -e "   ${YELLOW}(暂无)${NC}"
else
    for p in "${configured_platforms[@]}"; do
        echo -e "   ${GREEN}✅${NC} $p"
    done
fi

echo ""
echo -e " ${BOLD}未配置/跳过的平台:${NC}"
if [ ${#skipped_platforms[@]} -eq 0 ] && [ ${#configured_platforms[@]} -gt 0 ]; then
    echo -e "   ${GREEN}(全部已配置)${NC}"
else
    for p in "${skipped_platforms[@]}"; do
        echo -e "   ${YELLOW}⬜${NC} $p"
    done
fi

# 校验环境变量是否生效
echo ""
info "环境变量生效检查:"
python3 -c "
import os
keys = ['DEEPSEEK_API_KEY', 'DASHSCOPE_API_KEY', 'DOUBAO_API_KEY', 'ERNIE_API_KEY', 'SPARK_API_KEY']
for k in keys:
    v = os.environ.get(k, '')
    print(f'  {\"✅\" if v else \"❌\"} {k}: {\"已配置 (长度\"+str(len(v))+\")\" if v else \"未配置\"}')
"

echo ""
echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════╗"
echo "║   配置完成！                               ║"
echo "║                                           ║"
echo "║   重启 Hermes Agent 或执行:               ║"
echo "║     source ~/.hermes/.env                 ║"
echo "║                                           ║"
echo "║   配置已写入: $ENV_FILE"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# 常见问题提示
if [ "$IS_WSL" = true ] && [ ! -f /etc/wsl.conf ]; then
    echo ""
    warn "提示: 未检测到 /etc/wsl.conf，建议创建以优化 WSL 体验："
    echo "  sudo tee /etc/wsl.conf << 'EOF'"
    echo "  [interop]"
    echo "  enabled = true"
    echo "  appendWindowsPath = true"
    echo "  [automount]"
    echo "  enabled = true"
    echo "  root = /mnt/"
    echo "  options = \"metadata,umask=22,fmask=11\""
    echo "  EOF"
    echo "  然后重启 WSL: wsl --shutdown && wsl"
fi
