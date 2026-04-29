---
name: wsl-helper
description: "WSL/Windows双环境自动化管理——轻松在WSL和Windows之间协作，解决Interop/路径/权限/代理/性能问题"
version: 2.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [wsl, windows, interop, cross-platform, automation, devops]
    related_skills: [cn-dev-setup]
---

# 🪟 WSL Helper

> WSL (Windows Subsystem for Linux) 开发环境管理助手。
> 解决双系统开发中最头疼的问题，让你在WSL里写代码像在原生Linux一样丝滑。

## 目录

- [一、环境检测与诊断](#一环境检测与诊断)
- [二、Interop修复（126错误）](#二interop修复126错误)
- [三、文件系统与路径管理](#三文件系统与路径管理)
- [四、代理与网络配置](#四代理与网络配置)
- [五、性能优化](#五性能优化)
- [六、多个WSL发行版管理](#六多个wsl发行版管理)
- [七、常用Windows工具调用](#七常用windows工具调用)
- [八、WSL 2 网络模式详解](#八wsl-2-网络模式详解)
- [九、故障排查速查表](#九故障排查速查表)

---

## 一、环境检测与诊断

### 一键检测脚本

```bash
# 运行此命令快速了解当前WSL环境状态
cat << 'EOF' | bash
#!/bin/bash
echo "═══════════════════════════════════════"
echo "        WSL 环境诊断报告"
echo "═══════════════════════════════════════"

# WSL 版本
if grep -qi microsoft /proc/version 2>/dev/null; then
    if uname -r | grep -qi WSL2; then
        echo "[✓] WSL 2"
    else
        echo "[✓] WSL 1"
    fi
else
    echo "[✗] 不是 WSL 环境"
fi
echo "    内核: $(uname -r)"
echo "    发行版: $(lsb_release -ds 2>/dev/null || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"

# Interop 状态
if [ -f /proc/sys/fs/binfmt_misc/WSLInterop ]; then
    interop=$(cat /proc/sys/fs/binfmt_misc/WSLInterop | head -1)
    echo "[✓] Interop: $interop"
else
    echo "[✗] Interop: 未启用（无法执行Windows程序）"
fi

# Windows 访问
if ls /mnt/c/Windows/System32/notepad.exe &>/dev/null; then
    echo "[✓] Windows 文件系统: 可访问"
else
    echo "[✗] Windows 文件系统: 不可访问"
fi

# 磁盘使用
echo ""
echo "── 磁盘使用 ──"
df -h / | tail -1 | awk '{print "  WSL 根分区: " $3 " / " $2 " (" $5 ")"}'
df -h /mnt/c | tail -1 | awk '{print "  Windows C盘: " $3 " / " $2 " (" $5 ")"}'

# 网络
echo ""
echo "── 网络 ──"
echo "  IP: $(hostname -I 2>/dev/null | awk '{print $1}')"
if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
    echo "  [✓] 外网连通"
else
    echo "  [✗] 外网不通"
fi

# 代理（如果设置了）
echo ""
echo "── 代理 ──"
for var in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY; do
    val=${!var}
    if [ -n "$val" ]; then
        echo "  $var=$val"
    fi
done
[ -z "$http_proxy" ] && [ -z "$HTTP_PROXY" ] && echo "  (未设置代理)"

# 环境检查
echo ""
echo "── 开发工具 ──"
for cmd in python3 node go rustc docker git; do
    if command -v $cmd &>/dev/null; then
        echo "  [✓] $cmd: $($cmd --version 2>/dev/null | head -1)"
    else
        echo "  [✗] $cmd: 未安装"
    fi
done

echo ""
echo "═══════════════════════════════════════"
EOF
```

### 查看 WSL 配置

```bash
# 查看 /etc/wsl.conf
cat /etc/wsl.conf 2>/dev/null || echo "文件不存在，使用默认配置"
```

---

## 二、Interop修复（126错误）

### 症状

在 WSL 中执行 Windows 程序时报错：

```bash
$ notepad.exe
-bash: /mnt/c/Windows/System32/notepad.exe: 126: Exec format error
$ explorer.exe .
-bash: /mnt/c/Windows/explorer.exe: 126: Exec format error
```

### 修复方法

```bash
# 1. 检查 interop 状态
cat /proc/sys/fs/binfmt_misc/WSLInterop

# 2. 如果显示 disabled，编辑 /etc/wsl.conf
sudo tee /etc/wsl.conf > /dev/null << 'EOF'
[interop]
enabled=true
appendWindowsPath=true

[network]
generateResolvConf=true

[automount]
enabled=true
mountFsTab=true
options="metadata,uid=1000,gid=1000,umask=22,fmask=11"
EOF

# 3. 重启 WSL（在 Windows PowerShell 或 CMD 中执行）
# 方式一：完全重启
# wsl --shutdown
# 然后重新打开 WSL

# 方式二：只重启当前发行版（PowerShell）
# wsl -t <发行版名称>  # 如 wsl -t Ubuntu
# wsl ~

# 4. 验证修复
cmd.exe /c "echo Interop OK" 2>/dev/null && echo "[✓] Interop 已修复" || echo "[✗] Interop 仍有问题"
```

### 常见问题

| 症状 | 原因 | 解决 |
|------|------|------|
| 执行 .exe 返回 126 | interop 未启用 | 配置 /etc/wsl.conf 后重启 |
| `cmd.exe` 找不到 | PATH 未包含 Windows 目录 | 设置 appendWindowsPath=true |
| `wsl --shutdown` 后未生效 | Windows 端缓存的 WSL 配置 | 重启 Windows Terminal 或重新打开 WSL |
| 错误 0x80070002 | WSL 服务未启动 | 管理员 PowerShell: `net start LxssManager` |

---

## 三、文件系统与路径管理

### 路径转换

```bash
# WSL 路径 → Windows 路径
wslpath -w /home/user/project
# 输出: \\wsl.localhost\Ubuntu\home\user\project

# Windows 路径 → WSL 路径
wslpath -u 'C:\Users\Administrator\Desktop'
# 输出: /mnt/c/Users/Administrator/Desktop

# 获取 Windows 桌面路径
WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
DESKTOP_PATH="/mnt/c/Users/$WINDOWS_USER/Desktop"
echo "桌面路径: $DESKTOP_PATH"
```

### 常用文件操作

```bash
# Windows 桌面 ↔ WSL 快速传输
# 从 WSL 复制到桌面
cp output.txt "$(wslpath -u $(cmd.exe /c "echo %USERPROFILE%\Desktop" 2>/dev/null | tr -d '\r'))/"

# 从桌面复制到 WSL
cp "/mnt/c/Users/$WINDOWS_USER/Desktop/report.pdf" ~/

# 创建 Windows 符号链接
# 在 WSL 里创建指向 Windows 文件的链接
ln -s "/mnt/c/Users/$WINDOWS_USER/Desktop" ~/win-desktop

# Windows 快捷方式 (.lnk) 无法直接打开，需要用 cmd.exe
cmd.exe /c start "" "C:\Users\$WINDOWS_USER\Desktop\项目文档.docx"
```

### 性能最佳实践

```
推荐做法:
  ✅ 项目代码放在 WSL 文件系统 (~/project/) — I/O 性能好
  ✅ 通过 /mnt/c 访问 Windows 文件（不影响性能的场景）
  ✅ 使用 wslpath 进行路径转换
  
避免:
  ❌ 在 /mnt/c 下 git clone 大型仓库 — I/O 性能差 5-10 倍
  ❌ 在 /mnt/c 下运行 node_modules 重的项目
  ❌ 用 WSL 直接修改 Windows 系统文件
  ❌ 用 Windows 工具修改 WSL 文件（可能损坏元数据）
```

---

## 四、代理与网络配置

### 自动获取 Windows 代理

```bash
# 从 Windows 注册表或系统设置读取代理配置
get_windows_proxy() {
    local proxy=$(powershell.exe -NoProfile -Command \
        "[System.Net.WebRequest]::GetSystemWebProxy().GetProxy('http://example.com')" 2>/dev/null | tr -d '\r')
    if [ -n "$proxy" ] && [ "$proxy" != "http://example.com" ]; then
        echo "$proxy"
    else
        echo ""
    fi
}

# 自动设置 WSL 代理为 Windows 宿主机的代理
setup_wsl_proxy() {
    # 获取 Windows 宿主机 IP（WSL 2 中通过 resolv.conf 获取）
    local host_ip=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    
    # 常见代理端口
    for port in 7890 10809 1080 3128 8080; do
        if timeout 1 bash -c "echo > /dev/tcp/$host_ip/$port" 2>/dev/null; then
            export http_proxy="http://$host_ip:$port"
            export https_proxy="http://$host_ip:$port"
            export all_proxy="socks5://$host_ip:$port"
            echo "[✓] 代理已设置: http://$host_ip:$port"
            return 0
        fi
    done
    echo "[!] 未检测到代理服务，请确认 Windows 代理客户端已开启"
    return 1
}

# 运行
setup_wsl_proxy
```

### 代理配置文件

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
# WSL 代理自动配置
if grep -qi microsoft /proc/version 2>/dev/null; then
    # 获取宿主机 IP
    export WSL_HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    
    # 如果代理软件正在运行则自动设置
    if timeout 1 bash -c "echo > /dev/tcp/$WSL_HOST_IP/7890" 2>/dev/null; then
        export http_proxy="http://$WSL_HOST_IP:7890"
        export https_proxy="http://$WSL_HOST_IP:7890"
    fi
    
    # 设置 no_proxy（不走代理的内网地址）
    export no_proxy="localhost,127.0.0.1,.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
fi
```

### 代理切换函数

```bash
# 一键开关代理
proxy_on() {
    local ip=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    local port=${1:-7890}
    export http_proxy="http://$ip:$port"
    export https_proxy="http://$ip:$port"
    echo "[✓] 代理已开启 → http://$ip:$port"
}

proxy_off() {
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    echo "[✓] 代理已关闭"
}

# 测试代理是否生效
proxy_test() {
    curl -s --max-time 5 http://www.google.com -o /dev/null -w "Google: %{http_code} - %{time_total}s\n"
    curl -s --max-time 5 https://www.baidu.com -o /dev/null -w "Baidu: %{http_code} - %{time_total}s\n"
}
```

---

## 五、性能优化

### WSL 2 内存限制

默认 WSL 2 会占用宿主机大量内存。建议设置上限：

编辑 `%USERPROFILE%\.wslconfig`（在 Windows 中）：

```ini
[wsl2]
memory=4GB           # 限制最大使用 4GB 内存
processors=4         # 限制使用 4 个 CPU 核心
swap=2GB             # 交换分区大小
localhostForwarding=true
```

然后在 PowerShell 中执行：

```powershell
wsl --shutdown
# 重新打开 WSL 生效
```

### 磁盘性能

```bash
# 检查磁盘挂载选项（确保 metadata 启用）
mount | grep /mnt/c

# 如果性能差，考虑将项目移动到 WSL 文件系统
mv /mnt/c/Users/yourname/project ~/project/

# 或者用符号链接
ln -s ~/project /mnt/c/Users/yourname/project-wsl
```

### 减少 I/O 开销的技巧

```bash
# 1. 将 npm/pip 缓存指向 WSL 而非 Windows
npm config set cache ~/.npm-cache
pip config set global.cache-dir ~/.cache/pip

# 2. 禁用 Windows Defender 对 WSL 进程的实时扫描（PowerShell 管理员）
# Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\Packages\*"
# Add-MpPreference -ExclusionPath "\\wsl.localhost\*"

# 3. 减少 Windows PATH 注入的影响
# 在 /etc/wsl.conf 设置 appendWindowsPath=false
# 然后在 ~/.bashrc 中手动添加需要的路径
```

---

## 六、多个WSL发行版管理

```bash
# 列出所有发行版
wsl --list --verbose
# 或简写
wsl -l -v

# 输出示例:
#   NAME            STATE           VERSION
# * Ubuntu          Running         2
#   Ubuntu-24.04    Stopped         2
#   Debian          Stopped         2

# 安装新发行版
wsl --install -d Ubuntu-24.04

# 导出/导入发行版（备份或迁移）
# Windows PowerShell:
wsl --export Ubuntu-24.04 D:\backup\ubuntu24.tar
wsl --import Ubuntu-24.04-new D:\wsl\ubuntu24\ D:\backup\ubuntu24.tar

# 设置默认发行版
wsl --set-default Ubuntu-24.04

# 终止指定发行版
wsl -t Ubuntu-24.04

# 卸载发行版
wsl --unregister Ubuntu-24.04

# 在指定发行版中执行命令
wsl -d Ubuntu-24.04 -- python3 --version
```

---

## 七、常用Windows工具调用

```bash
# 打开 Windows 资源管理器到当前目录
explorer.exe .

# 在 Windows 默认浏览器中打开 URL
cmd.exe /c start https://github.com

# 打开 VS Code（从 WSL）
code .

# 打开 Windows 记事本编辑文件
notepad.exe README.md

# 打开 Windows Terminal 新标签页
wt.exe -d .

# 使用 Windows 版 Git
git.exe --version

# Windows 剪贴板操作
echo "hello" | clip.exe              # 复制到剪贴板
powershell.exe -Command "Get-Clipboard"  # 读取剪贴板

# 打开 Windows 计算器
calc.exe

# 打开 Windows 截图工具
snippingtool.exe 2>/dev/null || cmd.exe /c start snippingtool
```

### 获取 Windows 系统信息

```bash
# 获取 Windows IP
powershell.exe -NoProfile -Command \
  "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*' -and $_.PrefixOrigin -ne 'WellKnown'}).IPAddress | Select-Object -First 1" 2>/dev/null | tr -d '\r'

# 获取 Windows 用户名
cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r'

# 查看 Windows 环境变量
cmd.exe /c "set" 2>/dev/null | grep -i "^path=" | head -c 200

# Windows 系统信息
powershell.exe -Command "Get-ComputerInfo -Property OsName,OsVersion" 2>/dev/null
```

---

## 八、WSL 2 网络模式详解

WSL 2 使用 NAT 网络模式，与宿主机不在同一网段。

```
           ┌─────────────────────────┐
           │     Windows 宿主机       │
           │   IP: 192.168.1.100     │
           │                         │
           │  ┌─────────────────┐    │
           │  │   WSL 2 VM      │    │
           │  │  vSwitch (NAT)  │    │
           │  │                 │    │
           │  │ WSL IP: 172.x   │    │
           │  │ nameserver:     │    │
           │  │ 172.x.x.1      │    │
           │  └─────────────────┘    │
           └─────────────────────────┘
```

### 从 Windows 访问 WSL 服务

```bash
# WSL 2 中启动服务后，Windows 可以通过 localhost 访问
# WSL 2 自动转发 localhost 端口

# 示例: 在 WSL 中启动一个 web 服务
python3 -m http.server 8000

# 在 Windows 浏览器中打开
# http://localhost:8000

# 查看 WSL 的 IP（从 WSL 内部）
hostname -I

# 查看转发规则（PowerShell 管理员）
# netsh interface portproxy show all
```

### 从其他设备访问 WSL 服务

如果需要从局域网其他设备访问 WSL 中的服务，需要端口转发：

```powershell
# Windows PowerShell（管理员）
# 将 Windows 的 8000 端口转发到 WSL 的 8000 端口
netsh interface portproxy add v4tov4 \
  listenaddress=0.0.0.0 listenport=8000 \
  connectaddress=172.x.x.x connectport=8000

# 防火墙放行
New-NetFirewallRule -DisplayName "WSL Port 8000" \
  -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 查看转发规则
netsh interface portproxy show all

# 删除转发规则
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8000
```

---

## 九、故障排查速查表

| 症状 | 原因 | 快速解决 |
|------|------|----------|
| `wsl: 执行失败 0x800701bc` | WSL 2 组件未安装 | 管理员 PowerShell: `dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart` |
| `wsl: 执行失败 0x80370102` | BIOS 未开启虚拟化 | 重启进 BIOS → 开启 Intel VT-x 或 AMD SVM |
| `wsl: 执行失败 0x80072746` | WSL 服务未运行 | 管理员 PowerShell: `net start LxssManager` |
| 126 Exec format error | Interop 未启用 | 配置 /etc/wsl.conf → `wsl --shutdown` → 重启 |
| WSL 磁盘空间不足 | VHDX 自动增长不回收 | 管理员 PowerShell: `Optimize-VHD -Path \"$env:LOCALAPPDATA\\Packages\\*\\LocalState\\ext4.vhdx\" -Mode Full` |
| WSL 无法联网 | DNS 或网络配置问题 | `sudo rm /etc/resolv.conf && sudo tee /etc/resolv.conf <<< \"nameserver 8.8.8.8\" && sudo chattr +i /etc/resolv.conf` |
| `/mnt/c` 目录为空 | automount 未启用 | 配置 /etc/wsl.conf → 设置 mountFsTab=true |
| systemctl 不可用 | WSL 默认无 systemd | WSL 2 支持: 在 /etc/wsl.conf 添加 `[boot]\nsystemd=true` |
| Docker WSL 集成失败 | Docker Desktop 未设置 | Docker Desktop → Settings → Resources → WSL Integration → 启用 |
| 高内存占用 | WSL 2 内存无限制 | 在 Windows 设置 `.wslconfig` 的 memory 上限 |

---

## 脚本：一键修复 WSL 环境

将此保存为 `fix-wsl.sh`：

```bash
#!/bin/bash
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
echo "[...] WSL 磁盘使用: $disk_usage%"
if [ "$disk_usage" -gt 85 ]; then
    echo "[!] 磁盘空间不足，建议清理"
    echo "    推荐: docker system prune -a (如有 Docker)"
    echo "    推荐: sudo apt autoremove"
fi

# 检查内存
mem_total=$(free -m | awk '/^Mem:/{print $2}')
mem_used=$(free -m | awk '/^Mem:/{print $3}')
echo "[...] 内存: ${mem_used}MB / ${mem_total}MB"
if [ -f /proc/sys/fs/binfmt_misc/WSLInterop ] && [ "$mem_total" -gt 8000 ]; then
    echo "[!] 建议在 Windows 的 %USERPROFILE%\\.wslconfig 中设置 memory 限制"
fi

echo ""
echo "═══════════════════"
echo "修复完成！如果仍有问题，请参考 SKILL.md 的故障排查速查表。"
```
