# Awesome Dev Skill Pack 🚀

> 中文开发者专用的 AI 编程助手 Skill 包
> 让你的 AI 助手（Claude Code / Hermes Agent / Cursor / Copilot）更懂中文开发环境

<p align="center">
  <a href="https://github.com/lzhao8956-glitch/awesome-dev-skill-pack">
    <img src="https://img.shields.io/github/stars/lzhao8956-glitch/awesome-dev-skill-pack" alt="GitHub Stars">
  </a>
  <a href="https://afdian.com/a/lizhao">
    <img src="https://img.shields.io/badge/donate-爱发电-orange" alt="爱发电">
  </a>
  <img src="https://img.shields.io/badge/中国开发者-专为中文场景-blue" alt="中国开发者">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
</p>

---

## 📋 为什么你需要这个？

你是不是也遇到过这些问题？

- 🤨 **AI 生成的代码全是英文命名、英文注释**，放到中文团队项目里格格不入
- 😤 **让 AI 用 DeepSeek 写代码**，每次都要手动配置 API
- 😩 **在 WSL 里折腾环境**，Interop 报 126 错误、代理配不好、磁盘不够用
- 🤯 **写 Prompt 费劲**，每次审查代码、设计架构都要现想 Prompt

**这个 Skill 包就是来解决这些问题的。** 一套配置，搞定所有中文开发场景。

---

## 📦 7 个 Skill 一览

### 🇨🇳 cn-dev-setup — 国内开发环境配置
一键配置 DeepSeek/通义千问/豆包/百度文心/讯飞星火 API。
自动检测 WSL/Windows/Mac 环境，帮你配好代理、环境变量。

> **适合:** 刚装 AI 编程助手，需要配置国内 API 的开发者和团队

### 🎯 cn-coder — 中文代码生成规范
让 AI 生成符合中文团队规范的代码：
- 中文命名规范（变量/函数/类/文件命名）
- 中文注释规范（Python/JSDoc/GoDoc/Rustdoc）
- CRUD 代码生成模板
- 代码审查 checklist

> **适合:** 国内团队统一代码风格，提升代码可读性

### 🔌 api-wrapper — 国内 API 统一封装
一行代码切换 DeepSeek / 通义千问 / 百度文心 / 讯飞星火。
自带重试、错误处理、Token 计数。
**附带完整 Python 封装代码，可直接用。**

> **适合:** 需要在不同国产模型之间切换的开发者

### 🪟 wsl-helper — WSL/Windows 双环境管理
Interop 126 错误一键修复、代理自动配置、性能优化、多发行版管理。
**附带 fix-wsl.sh 脚本。**

> **适合:** WSL 用户，解决双系统开发中的各种坑

### 💬 prompt-engineering — 中文 Prompt 模板库
**24 个可直接复制使用的 Prompt 模板**，覆盖：
- 代码审查（基础/安全/SQL）
- 架构设计（系统设计/技术选型/微服务）
- Bug 修复（Debug/日志分析/性能排查）
- 重构（代码优化/大函数拆分/设计模式）
- 测试（单元测试/集成测试/覆盖率）
- 文档（API 文档/README/技术方案）
- API 设计（RESTful/GraphQL/错误码）

> **适合:** 想提升 AI 输出质量但不知道怎么写 Prompt 的人

### ☁️ deploy-china — 国内部署指南
从零部署到阿里云/腾讯云，含：
- 服务器选型、安全组配置、域名解析
- CDN 配置（阿里云/腾讯云）
- 备案全流程
- Docker/pip/npm 国内镜像
- GitHub Actions CI/CD 工作流
- **成本估算表**

> **适合:** 需要把项目部署到国内云服务的全栈开发者

### 🕷️ scrap-tool — 中文爬虫工具集
Python 爬虫模板 + 反爬绕过技巧 + Selenium 自动化。
**附完整爬虫示例代码。**
含法律合规说明。

> **适合:** 需要采集中文网站数据的开发者和数据分析师

---

## 🚀 快速开始

### Hermes Agent

```bash
# 克隆 Skills
git clone https://github.com/lzhao8956-glitch/awesome-dev-skill-pack.git \
  ~/.hermes/skills/awesome-dev-skill-pack

# 重启 Hermes，Skills 自动生效
```

### Claude Code

```bash
# 导入全部 Skill
claude import-skill https://github.com/lzhao8956-glitch/awesome-dev-skill-pack
```

### Cursor / Windsurf / 其他 AI 编辑器

直接将对应 SKILL.md 的内容复制到 `.cursorrules` 或项目根目录的 `AGENTS.md` 中。

---

## 💰 付费高级版

基础版完全免费 ❤️

如果你觉得这个包有帮助，可以考虑支持高级版（**¥29.9**）：

| 功能 | 基础版 | 高级版 |
|------|--------|--------|
| 7 个 Skill 基础内容 | ✅ | ✅ |
| **50+ 行业专用 Prompt 模板**（前端/后端/运维/数据/AI） | ❌ | ✅ |
| **100+ 企业级代码规范检查规则** | ❌ | ✅ |
| **国内云服务一键部署脚本**（含 Ansible/Terraform） | ❌ | ✅ |
| **AI 编程助手调优指南**（每个模型的专属配置） | ❌ | ✅ |
| **专属微信群 + 持续更新** | ❌ | ✅ |
| **付费定制 Skill** | ❌ | ✅ (3次) |

### 购买方式

👉 **[爱发电购买](https://afdian.com/a/lizhao)**

### 为什么要付费？

说实话 —— 维护 7 个 Skill 需要大量精力。高级版的内容是基础版的 **5 倍以上**，而且持续更新。

**我承诺：**
- 每月至少更新 1 次，紧跟 AI 编程助手的最新功能
- 付费用户专属微信群，有问题直接问
- 30 天内不满意全额退款

### 企业合作

团队采购（5 人以上）和企业定制 Skill 请联系：
- 邮箱: 210362553@qq.com
- 爱发电私信: https://afdian.com/a/lizhao

---

## ⭐ Star 历史

如果你觉得有用，点个 ⭐ 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=lzhao8956-glitch/awesome-dev-skill-pack&type=Date)](https://star-history.com/#lzhao8956-glitch/awesome-dev-skill-pack&Date)

---

## 📄 开源协议

MIT License — 基础版完全免费，高级版另行授权。

**做最懂中文开发者的 AI Skill 包 🇨🇳**
