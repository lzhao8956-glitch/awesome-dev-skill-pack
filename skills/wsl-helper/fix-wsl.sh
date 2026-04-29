#!/bin/bash
# WSL 环境修复脚本
set -e

echo "🪟 WSL 环境修复工具"
echo "═══════════════════"

# 检测是否为 WSL
if ! grep -qi microsoft /proc/version 2>/dev/null; then
    echo "[✗] 非 WSL 环境，脚本退出"
    exit 1
fi

# 修复 Interop
if [ ! -f /etc/wsl.conf ] || ! grep -q "enabled=true" /etc/wsl.conf 2>/dev/null; then
    echo "[...] 修复 Interop 配置..."
    sudo tee /etc/wsl.conf > /dev/null << 'CONF'
[interop]
enabled=true
appendWindowsPath=true

[automount]
enabled=true
mountFsTab=true
options="metadata,uid=1000,gid=1000,umask=22,fmask=11"
CONF
    echo "[✓] /etc/wsl.conf 已写入"
    echo "[!] 请在 Windows PowerShell 执行: wsl --shutdown"
    echo "    然后重新打开 WSL 终端"
else
    echo "[✓] Interop 配置已正确"
fi

# 检查 WSL 版本
echo -n "[...] WSL 版本: "
if uname -r | grep -qi WSL2; then
    echo "WSL 2 ✓"
else
    echo "WSL 1"
    echo "[!] 建议升级到 WSL 2: wsl --set-version <发行版名> 2"
fi

# 检查磁盘空间
disk_usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
echo "[...] WSL 磁盘使用: ${disk_usage}%"
if [ "$disk_usage" -gt 85 ]; then
    echo "[!] 磁盘空间不足，建议清理"
    echo "    推荐: docker system prune -a (如有 Docker)"
    echo "    推荐: sudo apt autoremove"
fi

# 检查内存
mem_total=$(free -m | awk '/^Mem:/{print $2}')
mem_used=$(free -m | awk '/^Mem:/{print $3}')
echo "[...] 内存: ${mem_used}MB / ${mem_total}MB"
if [ "$mem_total" -gt 8000 ]; then
    echo "[!] 建议在 Windows 的 %USERPROFILE%\\.wslconfig 中设置 memory 限制"
fi

echo ""
echo "═══════════════════"
echo "修复完成！如果仍有问题，请参考 SKILL.md 的故障排查速查表。"
