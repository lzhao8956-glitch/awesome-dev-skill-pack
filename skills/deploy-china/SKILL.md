---
name: deploy-china
description: "国内云服务一键部署指南——阿里云/腾讯云/Docker镜像加速/备案指南"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [deploy, china, aliyun, docker]
    related_skills: [cn-dev-setup]
---

# Deploy China

## 国内镜像加速

```bash
# Docker国内镜像
echo '{"registry-mirrors":["https://docker.mirrors.ustc.edu.cn"]}' > /etc/docker/daemon.json

# pip国内源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# npm国内源
npm config set registry https://registry.npmmirror.com
```

## 一键部署

```bash
# 阿里云函数计算
fun deploy
```
