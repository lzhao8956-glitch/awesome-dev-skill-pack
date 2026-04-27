---
name: wsl-helper
description: "WSL/Windows双环境自动化管理——轻松在WSL和Windows之间协作，解决Interop/路径/权限问题"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [wsl, windows, interop, cross-platform, automation]
    related_skills: [cn-dev-setup]
---

# 🪟 WSL Helper

## 概述

WSL (Windows Subsystem for Linux) 开发环境管理助手。解决双系统开发中最头疼的问题。

## 问题排查

### 1️⃣ WSL 里不能执行 Windows 程序（126错误）

```bash
# 检查 interop 是否启用
cat /proc/sys/fs/binfmt_misc/WSLInterop

# 如果显示 disabled，修复 /etc/wsl.conf
sudo sh -c 'cat >> /etc/wsl.conf << EOF
[interop]
enabled=true
appendWindowsPath=true
EOF'

# 重启 WSL（在 Windows PowerShell 中）
wsl --shutdown
```

### 2️⃣ 访问 Windows 文件

```bash
# Windows C盘在 /mnt/c/
ls /mnt/c/Users/Administrator/Desktop/

# 复制文件到 WSL
cp /mnt/c/Users/Administrator/Desktop/file.txt ~/

# 从 WSL 复制到桌面
cp ~/result.txt /mnt/c/Users/Administrator/Desktop/
```

### 3️⃣ 调用 Windows Python

```bash
# Windows Python 通常在
/mnt/c/Program\ Files/Python312/python.exe --version

# 或通过 PowerShell 查找
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
  -Command "Get-Command python | Select Source"
```

## 实用脚本

```bash
# 一键检测环境
cat << 'SCRIPT' | bash
echo "=== 环境检测 ==="
echo "WSL版本: $(uname -r)"
echo "Interop: $(cat /proc/sys/fs/binfmt_misc/WSLInterop 2>/dev/null | head -1)"
echo "Windows: $(ls /mnt/c/Windows/System32/notepad.exe 2>/dev/null && echo '✓' || echo '✗')"
echo "Python: $(python3 --version 2>/dev/null || echo '未安装')"
echo "磁盘: $(df -h /mnt/c | tail -1 | awk '{print $3 \" / \" $2}')"
SCRIPT
```
