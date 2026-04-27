---
name: cn-coder
description: "中文开发者的AI编程最佳实践：中文命名规范、注释规范、代码风格、项目结构模板"
version: 1.0.0
author: lzhao8956-glitch
license: MIT
metadata:
  hermes:
    tags: [coding, china, convention, style, best-practice]
    related_skills: [cn-dev-setup, wsl-helper]
---

# 🇨🇳 CN Coder

## 概述

中文开发者的 AI 编程规范指南。解决 AI 生成代码时"命名全英文但语义不对"、"注释不会中文"、"项目结构不符合国内习惯"等问题。

## 使用方式

在对话中告诉 AI：
> "请使用 cn-coder 规范生成代码"

AI 会自动应用以下规范。

## 命名规范

| 项目类型 | 推荐风格 | 示例 |
|---------|---------|------|
| 前端项目 | 文件名小写+连词符 | user-profile.tsx, api-service.ts |
| 后端项目 | 文件名小写+下划线 | user_service.py, order_controller.go |
| 数据库表 | 小写+下划线 | sys_user, order_detail |
| API接口 | RESTful + 中文文档 | GET /api/user/list |

## 注释规范

```python
# 中文注释，简洁明了
def get_user_info(user_id: int) -> dict:
    """获取用户信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户信息字典
    """
    pass
```

## 集成到 Claude Code

在项目根目录创建 CLAUDE.md：
```markdown
遵循 cn-coder 规范：
- 注释用中文
- 文件名用小写+下划线
- API 接口名用英文，注释用中文
```
