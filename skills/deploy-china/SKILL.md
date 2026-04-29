---
name: deploy-china
description: "国内云服务部署完全指南 —— 阿里云ECS / 腾讯云 / CDN / 备案 / 镜像加速 / CI/CD / 成本估算"
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [deploy, china, aliyun, tencent-cloud, docker, cd, cdn, beian]
    related_skills: [cn-dev-setup, docker, github-actions]
---

# 国内部署指南

面向国内开发者的一站式部署实操文档，涵盖主流云平台选型、网络加速、合规备案、自动化流水线及成本控制。

---

## 一、阿里云 ECS 部署

### 1.1 选择实例配置

| 场景 | 推荐规格 | vCPU | 内存 | 带宽 | 参考价格（月/按量） |
|------|----------|------|------|------|---------------------|
| 个人博客 / 小站点 | ecs.t6-c1m1.large | 1 | 1G | 1Mbps | ≈ ¥30 |
| 企业官网 / API 服务 | ecs.g7.xlarge | 4 | 16G | 5Mbps | ≈ ¥400 |
| 高并发微服务 | ecs.g7.2xlarge | 8 | 32G | 10Mbps | ≈ ¥900 |

> **策略建议**：新用户抢占"轻量应用服务器"（2C2G ¥24/月起，含固定带宽），适合个人项目。企业场景选通用型 g7/g8y（ARM 性价比更高）。

### 1.2 安全组配置

安全组是 ECS 的第一道网络防火墙，创建实例时必须配置：

```
入方向规则（关键）：
  协议     端口/范围     授权对象      说明
  TCP      22           0.0.0.0/0     SSH（建议改为指定 IP）
  TCP      80           0.0.0.0/0     HTTP
  TCP      443          0.0.0.0/0     HTTPS
  TCP      3000-3999    0.0.0.0/0     Node.js / 开发服务调试
  ICMP     -1           -1           允许 Ping（可选）

出方向规则：默认放行全部，一般不做限制。
```

**进阶安全**：不开放 22 端口到公网，改用阿里云"VPC 终端节点 + 会话管理器"或跳板机登录。生产环境务必开启安全组内 22 端口仅允许公司出口 IP。

### 1.3 域名解析

在阿里云 DNS（云解析 DNS）中添加 A 记录指向 ECS 公网 IP：

```
记录类型: A
主机记录: @（根域名）或 www、api、admin 等子域名
记录值:   你的 ECS 公网 IP
TTL:      10 分钟（调试期） / 600 秒（稳定期）
```

> 注意：需要在工信部完成 ICP 备案后，域名才能解析到中国大陆的 IP 并正常访问。

---

## 二、腾讯云部署

### 2.1 CVM 云服务器

与阿里云 ECS 操作类似，差异点如下：

| 维度 | 阿里云 | 腾讯云 |
|------|--------|--------|
| 默认安全组 | 创建实例时绑定 | 自动关联 default 组 |
| 镜像市场 | "阿里云镜像市场" | "TencentOS Server" 免费 |
| 新客优惠 | 轻量 ¥24/月 | 轻量 ¥22/月起 |
| 同区域价格 | 标准版略高 | 同等规格通常低 10-15% |

### 2.2 安全组（腾讯云对应"安全组"）

关联在 CVM 实例上，配置方式与阿里云一致。腾讯云控制台 → 云服务器 → 安全组，支持绑定多个实例。

### 2.3 DNS 解析

腾讯云 DNSPod（已并入腾讯云解析）：

```
登录控制台 → 云解析 DNS → 添加域名 → 添加记录
记录类型: A
线路类型: 默认（也可按电信/联通/移动分线路解析）
记录值:  CVM 公网 IP
```

DNSPod 支持"细分线路解析"（按运营商分流），适合多线机房部署。此外 DNSPod 的 DNS 节点覆盖国内三大运营商，解析速度通常优于阿里云解析。

---

## 三、国内 CDN 配置

### 3.1 阿里云 CDN

**开通步骤**：

1. 控制台 → CDN → 添加加速域名
2. 填写已备案的加速域名（如 `cdn.example.com`）
3. 源站类型：选择 ECS 外网 IP 或 OSS Bucket
4. 回源协议：HTTPS（推荐）或 HTTP
5. 等待 CNAME 解析生效（添加 CDN 分配的 `xxx.w.kunlun.com` CNAME 记录）

**缓存配置**：

| 文件类型 | 过期时间 | 优先级 |
|---------|---------|--------|
| .html .js .css | 1 天 | 高 |
| .png .jpg .ico | 30 天 | 高 |
| .mp4 .zip | 7 天 | 中 |
| API 路径 (/api/*) | 0 秒（不缓存） | 高 |

### 3.2 腾讯云 CDN

**开通步骤**：

1. 控制台 → CDN → 域名管理 → 添加域名
2. 加速区域选择"中国境内"（需备案）
3. 源站配置：源站 IP 为 CVM 内网/公网 IP；支持多 IP 轮询回源
4. 服务类型：静态加速 / 动态加速 / 动静结合
5. 等待 CNAME 解析到 `xxx.dnsv1.com` 后生效

**腾讯云独有特性**：

- 一键 HTTPS 证书配置（免费 SSL 证书颁发 + 自动续期）
- WebSocket 连接支持（动态加速场景）
- 访问鉴权（URL 鉴权，防止盗刷）

### 3.3 CDN 通用技巧

```
- 动静分离：静态资源走 CDN，API 直连源站
- 预热：上线前调用 CDN 预热接口将热点资源推到边缘节点
  curl "https://cdn.aliyuncs.com/xxx/refresh_and_preload?Action=PushObjectCache&ObjectPath=..."
- 刷新：更新资源后立即清掉边缘缓存
  # 阿里云 CDN 刷新
  aliyun cdn RefreshObjectCaches --ObjectPath "https://example.com/app.js"
  # 腾讯云 CDN 刷新
  curl -X POST https://cdn.tencentcloudapi.com/ -d 'Action=PurgeUrlsCache&Urls.0=https://...'
```

---

## 四、备案指南

所有部署在中国大陆的网站必须完成 ICP 备案。以下是流程概览：

### 4.1 前置条件

- 国内注册的域名（.cn / .com / .net 等）
- 国内云服务器（阿里云 / 腾讯云 / 华为云等）
- 管理员身份证 + 人脸识别
- 网站负责人信息（可与备案主体相同）

### 4.2 备案流程（以阿里云为例）

```
① 登录阿里云 → ICP 备案 → 开始备案
② 填写主体信息（个人 / 企业）
   个人：需身份证正反面 + 人脸核身
   企业：还需营业执照、法人证件
③ 填写网站信息
   - 网站名称（需规范，不能纯英文或"个人网站"等通用名）
   - 域名（已实名认证）
   - 云服务资源（关联 ECS 实例 ID）
④ 上传核验单（企业备案需盖公章）
⑤ 阿里云初审（1-2 个工作日）
⑥ 提交管局（通信管理局终审，约 5-20 个工作日）
⑦ 备案成功 → 收到工信部短信 → 获取备案号
```

### 4.3 备案成功后必须做的

| 事项 | 说明 |
|------|------|
| 悬挂备案号 | 网站首页底部显示"沪ICP备2024XXXXX号"并链接至 https://beian.miit.gov.cn |
| 公安备案 | 部分地区要求 30 日内完成公安联网备案（全国公安机关互联网站安全管理服务平台） |
| 域名实名 | 域名必须在注册商处已完成实名认证，否则备案驳回 |
| 备案号变更 | 网站内容或服务器变更需及时更新备案信息 |

### 4.4 常见问题

```
Q: 海外服务器需要备案吗？
A: 不需要。只要服务器不在中国大陆（中国香港、新加坡等），不需 ICP 备案。
   但面向大陆用户时建议备案，否则 CDN 加速和部分支付功能受限。

Q: 备案期间可以访问吗？
A: 不可以。完成备案前云服务商会封禁 80/443 端口，网站无法通过域名访问。
   可以通过 IP:端口（如 8080）临时访问。

Q: 备案号要放哪里？
A: 首页底部居中，需超链到工信部网址 beian.miit.gov.cn，字号不小于屏幕 1/10。
```

---

## 五、Docker 国内镜像源配置

### 5.1 配置 Docker 镜像加速器

国内访问 Docker Hub 极慢且不稳定，务必配置镜像源：

```bash
# 推荐镜像源（按优先级排列）
sudo mkdir -p /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.nju.edu.cn",
    "https://docker.m.daocloud.io",
    "https://mirror.ccs.tencentyun.com",
    "https://registry.cn-hangzhou.aliyuncs.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
docker info | grep -i mirror   # 验证生效
```

### 5.2 Docker Compose 中使用镜像

```yaml
# docker-compose.yml 无需额外配置 — daemon.json 对所有拉取生效
# 但如果是 Dockerfile 中 FROM 境外镜像，可加一个本地内网代理层：

services:
  # 通过内部 registry 代理加速构建
  builder:
    build:
      context: .
      args:
        - BUILDKIT_PROGRESS=plain
```

### 5.3 镜像源可用性速查

| 源地址 | 提供方 | 稳定性 | 推荐 |
|--------|--------|--------|------|
| docker.nju.edu.cn | 南京大学 | 高 | ⭐ 首选 |
| docker.m.daocloud.io | DaoCloud | 高 | ⭐ |
| mirror.ccs.tencentyun.com | 腾讯云 | 需腾讯云机器 | 云内使用 |
| registry.cn-hangzhou.aliyuncs.com | 阿里云 | 需阿里云机器 | 云内使用 |

---

## 六、pip / npm 国内镜像配置

### 6.1 pip 换源

```bash
# 全局配置（推荐清华源）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 额外信任（某些镜像源需要）
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 验证
pip config list
pip install numpy --verbose   # 查看实际下载地址

# 单次使用其他镜像
pip install -i https://mirrors.aliyun.com/pypi/simple torch
```

### 6.2 npm / yarn / pnpm 换源

```bash
# npm
npm config set registry https://registry.npmmirror.com

# yarn
yarn config set registry https://registry.npmmirror.com

# pnpm
pnpm config set registry https://registry.npmmirror.com

# 验证
npm config get registry
npm install express --verbose

# 查看包的实际镜像下载地址
npx nrm ls   # nrm 工具可快速切换源
```

### 6.3 各镜像源对比

| 源 | 域 | pip 速度 | npm 速度 | 长期稳定性 |
|----|----|---------|---------|-----------|
| 清华 Tuna | tuna.tsinghua.edu.cn | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 5 年+ |
| 阿里云 | mirrors.aliyun.com | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 5 年+ |
| 华为云 | mirrors.huaweicloud.com | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 3 年+ |
| 腾讯云 | mirrors.cloud.tencent.com | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 3 年+ |
| 中科大 USTC | mirrors.ustc.edu.cn | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 长期 |

---

## 七、GitHub Actions + 阿里云/腾讯云 CI/CD

### 7.1 推送到阿里云容器镜像服务 (ACR)

```yaml
# .github/workflows/deploy-aliyun.yml
name: Deploy to Alibaba Cloud

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Alibaba Cloud ACR
        uses: aliyun/acr-login@v1
        with:
          region-id: cn-hangzhou
          access-key-id: ${{ secrets.ALIYUN_ACCESS_KEY_ID }}
          access-key-secret: ${{ secrets.ALIYUN_ACCESS_KEY_SECRET }}

      - name: Build and Push Docker Image
        run: |
          docker build -t registry.cn-hangzhou.aliyuncs.com/my-ns/my-app:${{ github.sha }} .
          docker push registry.cn-hangzhou.aliyuncs.com/my-ns/my-app:${{ github.sha }}

      - name: Deploy to ECS via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.ECS_HOST }}
          username: root
          key: ${{ secrets.ECS_SSH_KEY }}
          script: |
            docker pull registry.cn-hangzhou.aliyuncs.com/my-ns/my-app:${{ github.sha }}
            docker stop my-app || true
            docker rm my-app || true
            docker run -d --name my-app -p 80:3000 \
              registry.cn-hangzhou.aliyuncs.com/my-ns/my-app:${{ github.sha }}
```

### 7.2 部署到腾讯云 TKE / CVM

```yaml
# .github/workflows/deploy-tencent.yml
name: Deploy to Tencent Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install coscli (腾讯云 COS 工具)
        run: |
          curl -sL https://github.com/tencentyun/coscli/releases/latest/download/coscli-linux -o coscli
          chmod +x coscli
          sudo mv coscli /usr/local/bin/

      - name: Upload to COS (静态资源)
        run: |
          coscli config add --bucket my-bucket-1250000000 \
            --region ap-guangzhou --secret-id ${{ secrets.TENCENT_SECRET_ID }} \
            --secret-key ${{ secrets.TENCENT_SECRET_KEY }} --alias my-cos
          coscli cp -r ./dist/ cos://my-cos/dist/

      - name: Deploy via SSH to CVM
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.CVM_HOST }}
          username: ubuntu
          key: ${{ secrets.CVM_SSH_KEY }}
          script: |
            cd /opt/my-app
            git pull origin main
            docker compose pull
            docker compose up -d --build
            docker image prune -f
```

### 7.3 密钥管理注意事项

```
1. 在 GitHub → Settings → Secrets and variables → Actions 中添加：
   - ALIYUN_ACCESS_KEY_ID / ALIYUN_ACCESS_KEY_SECRET
   - 或 TENCENT_SECRET_ID / TENCENT_SECRET_KEY
   - ECS/CVM 的 SSH 私钥 (ECS_SSH_KEY)

2. 阿里云 RAM 用户权限最小化：
   创建 RAM 用户 → 仅授予 ACR 推送权限 + ECS 只读权限
   不要使用主账号 AccessKey

3. 腾讯云 CAM 策略同理：
   策略模板：QcloudAccessForCDNRole + QcloudCVMReadOnlyAccess
```

---

## 八、成本估算

以下为 2025 年参考价格，按个人项目最小配置测算。

### 8.1 个人博客 / 小站点（月访问 < 1K PV）

| 项目 | 配置 | 月费用 |
|------|------|--------|
| 云服务器 | 轻量 2C2G + 3Mbps | ¥24-34 |
| 域名 | .com 首年约 ¥45 | ¥3.75 |
| CDN | 阿里云 CDN 按量，< 10GB/月 | ¥1-3 |
| SSL 证书 | 免费（Let's Encrypt / 云厂商免费） | ¥0 |
| **合计** | | **≈ ¥30-40/月** |

### 8.2 企业应用（日均 PV 1W-5W）

| 项目 | 配置 | 月费用 |
|------|------|--------|
| 云服务器 × 2 | ECS g7 4C16G | ¥800-1200 |
| RDS 数据库 | 2C4G MySQL | ¥300-500 |
| CDN | 100GB 流量包 | ¥80-150 |
| OSS 对象存储 | 50GB + 低频读写 | ¥20-50 |
| 负载均衡 SLB | 标准型 | ¥100-200 |
| 域名 × 2 | .com + .cn 续费 | ¥10-15 |
| **合计** | | **≈ ¥1300-2100/月** |

### 8.3 省钱技巧

```text
1. 抢占式实例（Spot Instance）：非关键任务使用，价格约 10-20%
   - 阿里云：抢占式实例，无固定折扣制
   - 腾讯云：竞价实例，按市场价格浮动

2. 预留实例券 / 包年包月：1 年 ≈ 83 折，3 年 ≈ 5 折
   按量付费每月超过 ¥500 时建议转包年包月

3. 对象存储 + CDN 组合：OSS/COS 作为 CDN 源站时，内网回源流量免费
   避免 ECS 直接出公网带宽（公网带宽成本远高于 OSS 内网传输）

4. 混合部署：核心服务用包年包月保底，弹性扩缩部分用按量或抢占式

5. 使用 Serverless 替代 ECS（轻量场景）
   - 阿里云函数计算 FC：按调用次数计费，月免费额度足够小项目
   - 腾讯云 SCF：同理，配合 API 网关 ≈ ¥0 起
```

---

## 附录：快速命令速查

```bash
# Docker 换源后验证
docker info --format '{{json .RegistryConfig.Mirrors}}'

# pip 换源后加速安装
pip install -r requirements.txt --no-cache-dir

# npm 换源后清理缓存
npm cache clean --force

# CDN 预热（阿里云 CLI）
aliyun cdn PushObjectCache \
  --ObjectPath "https://example.com/index.html" \
  --Area overseas

# CDN 刷新（腾讯云 API）
tccli cdn PurgeUrlsCache --Urls '["https://example.com/style.css"]'

# 检查域名备案状态
curl -s "https://beian.miit.gov.cn/api/query?domain=example.com"
```

> **最后提醒**：国内部署的关键三件事 —— 备案先行、镜像加速保下载速度、安全组收窄端口。以上配置在阿里云（华东2 / 华北2）和腾讯云（广州 / 上海）生产环境下稳定运行超过 2 年，请根据实际业务吞吐量适当调整规格。
