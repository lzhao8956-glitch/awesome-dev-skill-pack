---
name: cn-coder
description: "中文代码生成规范：命名规范、注释规范、多语言代码规则、CRUD模板、代码审查清单"
version: 2.0.0
author: awesome-dev-skill-pack
license: MIT
metadata:
  hermes:
    tags: [coding, china, convention, style, crud, review, best-practice]
    related_skills: [cn-dev-setup, wsl-helper]
---

# 🇨🇳 CN Coder — 中文代码生成规范

## 概述

面向中文团队的 AI 编程规范。解决三个核心痛点：

- AI 生成的代码命名字义不准确、风格不统一
- 注释全是英文或机器翻译痕迹明显
- 生成代码不符合国内团队的项目结构和命名惯例

本规范提供了 **命名规范 → 注释模板 → 多语言规则 → 提示词模板 → CRUD 模板 → 审查清单** 的完整闭环。

---

## 一、中文命名规范

### 1.1 核心原则

| 层级 | 原则 | 说明 |
|------|------|------|
| 项目/模块 | 英文 | 项目名、包名、模块名统一英文 |
| 代码标识符 | 英文 | 变量/函数/类/方法名统一英文 |
| 注释/文档 | 中文 | 所有自然语言描述使用中文 |
| 配置/资源 | 中文 | 国际化 Key、菜单名、权限名可中文 |
| 数据库 | 英文 | 表名、字段名统一英文 |

### 1.2 命名策略选型

#### 选英文名（推荐）—— 绝大多数场景

```
# 好
user_name, order_status, get_user_info(), OrderHandler

# 不好 —— 语法错误或中式英文
people_name, buy_goods, do_thing(), ThingDoer
```

**选英文时的原则：**

- 使用团队维护的 **中英术语对照表**（见下文 1.3）
- 不认识的英文查词典，不必硬造
- 优先使用业务领域的标准术语（`order` / `invoice` / `sku` / `workflow`）
- 动词+名词组合保持语序一致：`getUser` 不是 `userGet`

#### 选拼音 —— 仅限以下特例

- 专有名词/地名：`beijing`、`weixin`（微信生态专用）
- 无准确英文对应且跨团队共识的术语：`pinyin`（拼音本身）、`hukou`（户口）
- 内部业务黑话：如果整个团队都说"打款"，用 `daKuan` 比 `makePayment` 更可维护

**严禁拼音场景：**

```
# ❌ 坚决禁止
user_xingming, shoujihao, yonghubiao, btn_dianji
```

### 1.3 中英术语对照表（推荐）

在项目根目录维护 `TERMS.md`：

```markdown
# 项目术语对照表

| 中文 | 英文 | 说明 |
|------|------|------|
| 用户 | user | — |
| 订单 | order | — |
| 商品 | product / item | item 特指订单行 |
| 优惠券 | coupon | — |
| 审核 | review | 内容审核用 moderate |
| 提现 | withdraw | — |
| 余额 | balance | — |
| 打款 | payout | 财务付款专用 |
| 分页 | pagination | — |
| 校验 | validate | 后端校验用 verify |
| 转换 | convert / transform | 数据格式转换 |
| 映射 | map / mapping | — |
```

### 1.4 各要素命名规则

#### 变量名

```python
# ✅ 好
user_name = "张三"       # 名词 + 名词
is_active = True         # is_ + 形容词
order_list = []          # 名词 + 集合后缀
product_count = 0        # 名词 + 度量词

# ❌ 不好
username = "张三"        # 有歧义（username 可以是登录名）
active_flag = True       # flag 冗余
arr = []                 # 无意义
temp_str = ""            # temp/str 无信息量
```

#### 函数/方法名

```python
# ✅ 好
def get_user_info(user_id): ...
def create_order(items, address): ...
def validate_email(email): ...
def is_order_paid(order_id): ...

# 动词习惯：get/create/update/delete + 名词
# 布尔判断：is/has/can/should + 形容词/过去分词

# ❌ 不好
def user_info(): ...                       # 无动词
def deal_with_order(): ...                 # deal_with 模糊
def check_email_is_ok(email): ...          # is_ok 不规范
def do_thing(): ...                        # 无意义
```

#### 类名

```python
# ✅ 好
class OrderService: ...
class UserController: ...
class PaymentProvider: ...
class OrderStatus(Enum): ...
class NotFoundError(Exception): ...

# 名词 + 名词/后缀：Service / Controller / Provider / Handler / Manager / Factory / Builder / Strategy

# ❌ 不好
class OrderThing: ...        # 无意义后缀
class DoOrder: ...           # 动词开头
class order_utils: ...       # 小写下划线
```

#### 常量

```python
# ✅ 好
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
ORDER_STATUS_PENDING = "pending"
API_BASE_URL = "https://api.example.com"

# 全大写 + 下划线
```

#### 文件名

| 项目类型 | 风格 | 示例 |
|----------|------|------|
| Python 后端 | 小写下划线 | `user_service.py`, `order_controller.py` |
| JavaScript/TS 前端 | 小写连词符 | `user-profile.tsx`, `api-service.ts` |
| Go 后端 | 小写下划线 | `user_service.go`, `order_handler.go` |
| Rust 后端 | 小写下划线 | `user_service.rs`, `order_model.rs` |
| 测试文件 | 与被测文件一致 | `user_service_test.py` |

---

## 二、代码注释规范

### 2.1 通用原则

```
1. 注释用中文，代码用英文
2. 注释说明"为什么"，不说明"是什么"（代码本身应自说明）
3. 复杂逻辑写注释，简单逻辑不写注释
4. 文档字符串必写，公共 API 必写
5. TODO / FIXME / HACK 用英文标记，中文说明
```

### 2.2 行内注释

```python
# 价格必须是正数（业务规则：不允许负定价）
if price <= 0:
    raise ValueError("价格不合法")

items = fetch_items()  # 从缓存中获取商品列表，若缓存不存在则回源 DB
```

### 2.3 块注释

```python
# ──────────────────────────────────────────────
# 订单超时处理逻辑
# 1. 扫描所有状态为 "待支付" 且超过 30 分钟的订单
# 2. 将其状态变更为 "已取消"
# 3. 释放预占库存
# 4. 发送取消通知给用户
# ──────────────────────────────────────────────
```

### 2.4 模块/包注释

```python
"""
订单模块

提供订单的创建、支付、取消、退款全生命周期管理。
依赖：
  - user_service: 用户信息
  - payment_service: 支付渠道对接
  - inventory_service: 库存锁定与释放
"""
```

### 2.5 文档字符串模板

#### Python（Google 风格，中文描述）

```python
def create_order(
    user_id: int,
    items: list[OrderItem],
    address: Address,
    coupon_code: str | None = None
) -> Order:
    """创建订单

    校验商品库存、计算金额、应用优惠券、锁定库存。
    若校验失败或库存不足，抛出对应的业务异常。

    Args:
        user_id: 用户 ID
        items: 订单商品列表（至少包含一个商品）
        address: 收货地址
        coupon_code: 优惠券编码（可选）

    Returns:
        已创建的 Order 对象

    Raises:
        UserNotFoundError: 用户不存在
        InsufficientStockError: 库存不足
        CouponInvalidError: 优惠券无效或已过期

    Example:
        >>> order = create_order(1, [item1], addr, code="NEW2024")
        >>> order.status
        'pending'
    """
    ...
```

#### JavaScript / TypeScript（JSDoc，中文描述）

```typescript
/**
 * 创建订单
 *
 * 校验商品库存、计算金额、应用优惠券、锁定库存。
 *
 * @param {number} userId - 用户 ID
 * @param {OrderItem[]} items - 订单商品列表
 * @param {Address} address - 收货地址
 * @param {string} [couponCode] - 优惠券编码（可选）
 * @returns {Promise<Order>} 创建的订单对象
 * @throws {UserNotFoundError} 用户不存在
 * @throws {InsufficientStockError} 库存不足
 *
 * @example
 * const order = await createOrder(1, [item1], addr, 'NEW2024')
 * console.log(order.status) // 'pending'
 */
async function createOrder(userId, items, address, couponCode) { ... }
```

#### Go（中文注释）

```go
// CreateOrder 创建订单
//
// 校验商品库存、计算金额、应用优惠券、锁定库存。
// 参数验证失败或库存不足时返回对应的业务错误。
//
// 参数:
//   - ctx: 上下文（包含超时控制）
//   - req: 创建订单请求体
//
// 返回值:
//   - *Order: 已创建的订单对象
//   - error: 业务错误（可能为 ErrUserNotFound / ErrInsufficientStock / ErrCouponInvalid）
func CreateOrder(ctx context.Context, req *CreateOrderReq) (*Order, error) { ... }
```

#### Rust（中文注释）

```rust
/// 创建订单
///
/// 校验商品库存、计算金额、应用优惠券、锁定库存。
/// 校验失败或库存不足时返回对应的错误。
///
/// # 参数
/// - `user_id`: 用户 ID
/// - `items`: 订单商品列表
/// - `address`: 收货地址
/// - `coupon_code`: 优惠券编码（可选）
///
/// # 返回值
/// - `Ok(Order)`: 已创建的订单
/// - `Err(AppError)`: 业务错误
///
/// # 示例
/// ```
/// let order = create_order(1, vec![item], addr, Some("NEW2024")).await?;
/// assert_eq!(order.status, OrderStatus::Pending);
/// ```
pub async fn create_order(
    user_id: i32,
    items: Vec<OrderItem>,
    address: Address,
    coupon_code: Option<String>,
) -> Result<Order, AppError> { ... }
```

---

## 三、多语言代码生成规则

### 3.1 通用规则（适用于所有语言）

```
1. 所有标识符使用英文，注释使用中文
2. 错误消息中英双份（日志用中文，用户端用英文或国际化）
3. 日志消息使用中文，方便排查
4. 配置项注释使用中文
5. 测试用例描述使用中文
```

### 3.2 Python 规则

```python
# 命名风格：变量/函数 → snake_case，类 → PascalCase，常量 → UPPER_CASE
# 类型注解必须写
# 文件名：小写下划线
# 项目结构：

# my_project/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py          # 应用入口
# │   ├── config.py        # 配置（中文注释）
# │   ├── models/          # 数据模型
# │   │   ├── __init__.py
# │   │   └── user.py
# │   ├── services/        # 业务逻辑
# │   │   ├── __init__.py
# │   │   └── user_service.py
# │   ├── controllers/     # 接口层
# │   │   ├── __init__.py
# │   │   └── user_controller.py
# │   └── utils/           # 工具函数
# │       └── validators.py
# └── tests/
#     ├── conftest.py
#     └── test_user_service.py
```

### 3.3 JavaScript / TypeScript 规则

```typescript
// 命名风格：变量/函数 → camelCase，类/组件 → PascalCase，常量 → UPPER_CASE
// 文件名：组件用 PascalCase（UserProfile.tsx），工具用小写连词符（api-service.ts）
// TypeScript 类型定义必须写
// 异步函数统一 async/await
// 项目结构（前端）：

// src/
// ├── api/                  # API 请求层
// │   ├── request.ts        # axios/fetch 封装
// │   └── user.ts           # 用户相关接口
// ├── components/           # 通用组件
// │   ├── UserTable/
// │   │   ├── index.tsx
// │   │   └── style.module.css
// │   └── Pagination.tsx
// ├── pages/                # 页面组件
// │   └── user/
// │       ├── UserList.tsx
// │       └── UserDetail.tsx
// ├── hooks/                # 自定义 hooks
// │   └── useUser.ts
// ├── types/                # 类型定义
// │   └── user.ts
// ├── utils/                # 工具函数
// │   └── format.ts
// ├── i18n/                 # 国际化
// └── App.tsx
```

### 3.4 Go 规则

```go
// 命名风格：函数 → PascalCase（导出）或 camelCase（私有），变量 → camelCase
// 常量 → PascalCase
// 文件名：小写下划线
// 错误变量以 Err 开头：ErrUserNotFound
// 接口名以 er 结尾：UserService / OrderRepository
// 项目结构：

// my-server/
// ├── cmd/
// │   └── server/
// │       └── main.go          # 应用入口
// ├── internal/
// │   ├── config/
// │   │   └── config.go        # 配置（中文注释）
// │   ├── model/
// │   │   ├── user.go          # 数据模型
// │   │   └── order.go
// │   ├── repo/
// │   │   └── user_repo.go     # 数据访问层
// │   ├── service/
// │   │   └── user_service.go  # 业务逻辑
// │   ├── handler/
// │   │   └── user_handler.go  # HTTP 处理器
// │   └── middleware/
// │       └── auth.go
// ├── pkg/
// │   └── errors/
// │       └── errors.go
// └── go.mod
```

### 3.5 Rust 规则

```rust
// 命名风格：变量/函数 → snake_case，类/枚举 → PascalCase
// 常量 → UPPER_CASE
// 文件名：小写下划线
// 错误类型以 Error 结尾，使用 thiserror/anyhow
// 所有公共项必须有文档注释（///）
// 模块结构：

// my-service/
// ├── src/
// │   ├── main.rs              # 应用入口
// │   ├── config.rs            # 配置（中文注释）
// │   ├── model/
// │   │   ├── mod.rs
// │   │   ├── user.rs          # 数据模型
// │   │   └── order.rs
// │   ├── repository/
// │   │   ├── mod.rs
// │   │   └── user_repo.rs     # 数据访问层
// │   ├── service/
// │   │   ├── mod.rs
// │   │   └── user_service.rs  # 业务逻辑
// │   ├── handler/
// │   │   ├── mod.rs
// │   │   └── user_handler.rs  # HTTP 处理器
// │   └── error.rs             # 错误定义
// ├── tests/
// └── Cargo.toml
```

---

## 四、提示词模板

### 4.1 通用提示词（项目初始化）

```
请按照 cn-coder 规范生成以下项目的代码：

项目类型: {Python/JS/Go/Rust}
项目名称: {项目名}
核心功能: {一句话说明}

规范要求：
1. 所有标识符（变量/函数/类/方法/文件名）使用英文
2. 所有注释、文档字符串使用中文
3. 遵循 {语言} 的语言惯例命名风格
4. 项目结构参照 cn-coder 推荐的目录模板
5. 公共函数/方法必须写中文文档字符串
6. 错误消息：日志用中文，用户端用英文
```

### 4.2 提示词模板（CRUD 生成）

```
请使用 cn-coder 规范，生成 {实体名} 的 CRUD 代码。

语言: {Python/JS/Go/Rust}
框架: {FastAPI/Express/Gin/Axum}
数据表: {表名}
字段列表:
  - {字段名1}: {类型1} — {中文说明1}
  - {字段名2}: {类型2} — {中文说明2}
  ...

请生成：
1. 数据模型定义（含中文注释的字段说明）
2. 创建接口（含输入校验逻辑）
3. 查询接口（支持分页、筛选）
4. 更新接口（部分更新）
5. 删除接口（逻辑删除或物理删除）
6. 单元测试（测试用例用中文描述）

额外要求：
- {可选：权限校验 / 日志记录 / 缓存策略 等}
```

### 4.3 提示词模板（代码优化/重构）

```
请按照 cn-coder 规范重构以下代码。

问题描述: {当前代码的问题}
重构目标: {可读性 / 性能 / 可维护性 / 命名优化}

规范要求：
1. 将所有中文拼音命名替换为英文命名
2. 补充中文注释和文档字符串
3. 统一命名风格
4. 抽取重复逻辑为独立函数

以下是原始代码：
```{language}
{代码内容}
```
```

### 4.4 提示词模板（代码审查）

```
请按照 cn-coder 代码审查清单，审查以下代码：

语言: {Python/JS/Go/Rust}
功能: {功能描述}

审查重点：
1. 命名是否规范（英文命名、语义准确）
2. 注释是否完整且使用中文
3. 代码结构是否符合项目规范
4. 异常处理是否完备
5. 是否存在安全隐患

原始代码：
```{language}
{代码内容}
```
```

---

## 五、CRUD 代码生成模板

### 5.1 通用 API 设计规范

```text
# RESTful API 路径设计

列表查询: GET    /api/{资源}?page=1&size=20&status=active
详情查询: GET    /api/{资源}/{id}
创建:     POST   /api/{资源}
更新:     PUT    /api/{资源}/{id}       （全量更新）
部分更新: PATCH  /api/{资源}/{id}       （推荐）
删除:     DELETE /api/{资源}/{id}       （逻辑删除）
批量删除: DELETE /api/{资源}?ids=1,2,3

# 统一返回格式
{
  "code": 0,          # 0=成功，非0=业务错误码
  "message": "操作成功",  # 中文或英文消息
  "data": {},         # 业务数据
  "request_id": "..."  # 链路追踪 ID
}

# 分页返回格式
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "total_pages": 5
  }
}

# 错误返回格式
{
  "code": 40001,
  "message": "用户不存在",
  "detail": "无法找到 ID 为 123 的用户",
  "request_id": "..."
}
```

### 5.2 Python + FastAPI CRUD 完整模板

```python
# user_controller.py —— 用户 CRUD 接口
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserQuery, UserResponse, PaginatedResponse

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    query: UserQuery = Depends(),
    service: UserService = Depends(),
):
    """获取用户列表（支持分页和筛选）"""
    result = await service.list_users(
        page=query.page,
        size=query.size,
        status=query.status,
        keyword=query.keyword,
    )
    return PaginatedResponse(
        code=0,
        message="查询成功",
        data=result,
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserService = Depends()):
    """获取用户详情"""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(code=0, message="查询成功", data=user)

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, service: UserService = Depends()):
    """创建用户"""
    user = await service.create_user(data)
    return UserResponse(code=0, message="创建成功", data=user)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, service: UserService = Depends()):
    """更新用户信息（部分更新）"""
    user = await service.update_user(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(code=0, message="更新成功", data=user)

@router.delete("/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends()):
    """删除用户（逻辑删除）"""
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 0, "message": "删除成功"}
```

```python
# user_service.py —— 用户业务逻辑
from app.repositories.user_repo import UserRepository
from app.models.user import User

class UserService:
    """用户业务逻辑层"""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def list_users(self, page: int, size: int, status: str | None, keyword: str | None):
        """查询用户列表，支持按状态和关键词筛选"""
        offset = (page - 1) * size
        users, total = await self.repo.find_all(
            offset=offset,
            limit=size,
            status=status,
            keyword=keyword,
        )
        return {
            "list": users,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size,
        }

    async def get_user(self, user_id: int) -> User | None:
        """根据 ID 获取用户"""
        return await self.repo.find_by_id(user_id)

    async def create_user(self, data) -> User:
        """创建新用户，含重复检测"""
        exists = await self.repo.find_by_email(data.email)
        if exists:
            raise ValueError("邮箱已被注册")
        return await self.repo.create(data)

    async def update_user(self, user_id: int, data) -> User | None:
        """更新用户，跳过 None 字段（部分更新）"""
        user = await self.repo.find_by_id(user_id)
        if not user:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(user_id, update_data)

    async def delete_user(self, user_id: int) -> bool:
        """逻辑删除用户"""
        user = await self.repo.find_by_id(user_id)
        if not user:
            return False
        await self.repo.soft_delete(user_id)
        return True
```

```python
# user_repo.py —— 用户数据访问层
from app.models.user import User
from app.database import db

class UserRepository:
    """用户数据访问层"""

    async def find_all(self, offset: int, limit: int, status: str | None, keyword: str | None):
        """查询用户列表，支持筛选和分页"""
        query = "SELECT * FROM users WHERE deleted_at IS NULL"
        count_query = "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL"
        params = []

        if status:
            query += " AND status = ?"
            count_query += " AND status = ?"
            params.append(status)
        if keyword:
            query += " AND (name LIKE ? OR email LIKE ?)"
            count_query += " AND (name LIKE ? OR email LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = await db.fetch_all(query, params)
        total = await db.fetch_val(count_query, params[:2])  # 不含 limit/offset 的参数

        return [User(**row) for row in rows], total

    async def find_by_id(self, user_id: int) -> User | None:
        """根据主键查询用户"""
        row = await db.fetch_one(
            "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL",
            [user_id],
        )
        return User(**row) if row else None

    async def find_by_email(self, email: str) -> User | None:
        """根据邮箱查询用户（用于重复检测）"""
        row = await db.fetch_one(
            "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL",
            [email],
        )
        return User(**row) if row else None

    async def create(self, data) -> User:
        """插入新用户并返回"""
        row = await db.fetch_one(
            "INSERT INTO users (name, email, phone, status) VALUES (?, ?, ?, ?) RETURNING *",
            [data.name, data.email, data.phone, data.status or "active"],
        )
        return User(**row)

    async def update(self, user_id: int, data: dict) -> User | None:
        """更新用户字段（只更新 data 中包含的字段）"""
        if not data:
            return await self.find_by_id(user_id)
        set_clause = ", ".join(f"{k} = ?" for k in data.keys())
        values = list(data.values()) + [user_id]
        await db.execute(
            f"UPDATE users SET {set_clause} WHERE id = ? AND deleted_at IS NULL",
            values,
        )
        return await self.find_by_id(user_id)

    async def soft_delete(self, user_id: int):
        """逻辑删除：设置 deleted_at 时间戳"""
        await db.execute(
            "UPDATE users SET deleted_at = datetime('now') WHERE id = ?",
            [user_id],
        )
```

---

## 六、代码审查清单

### 6.1 命名审查

- [ ] 所有标识符使用英文，无拼音命名
- [ ] 变量名语义准确，无模糊含义（`data`/`info`/`tmp` 是否合理？）
- [ ] 函数名体现"动词+名词"结构
- [ ] 类名使用 PascalCase，名词性后缀
- [ ] 常量使用 UPPER_CASE
- [ ] 文件名符合语言惯例（Python snake_case，JS kebab-case）
- [ ] 布尔函数/变量使用 `is_`/`has_`/`can_`/`should_` 前缀
- [ ] 集合变量使用复数或 `_list`/`_set` 后缀

### 6.2 注释审查

- [ ] 所有注释使用中文，无英文注释（英文术语除外）
- [ ] 公共 API 必须有文档字符串/注释
- [ ] 文档字符串包含：功能说明、参数、返回值、异常
- [ ] 复杂逻辑有关键性注释（解释"为什么"）
- [ ] 无"废注释"（逐行解释"是什么"）
- [ ] TODO/FIXME 有责任人/时间标记
- [ ] 注释与代码同步更新（无过期注释）

### 6.3 代码结构审查

- [ ] 函数/方法单一职责（不超过 50 行）
- [ ] 无重复代码（DRY 原则）
- [ ] 项目结构遵循分层的约定（controller → service → repository）
- [ ] 异常/错误处理完备
- [ ] 日志记录完整（链路的入口/出口/异常点）
- [ ] 数据库查询无 N+1 问题
- [ ] 关键路径有单元测试

### 6.4 安全审查

- [ ] SQL 使用参数化查询，无字符串拼接
- [ ] 用户输入经过校验/过滤
- [ ] 密码/密钥不硬编码，使用环境变量
- [ ] API 有权限校验（认证+鉴权）
- [ ] 分页大小有上限限制
- [ ] 敏感字段（密码、手机号）不返回前端

### 6.5 性能审查

- [ ] 数据库查询有条件限制（无全表扫描）
- [ ] 循环内无数据库查询/IO 操作（可批量处理）
- [ ] 列表数据有分页
- [ ] 高频查询有缓存策略
- [ ] 大对象/文件使用流式处理
- [ ] 连接有超时和重连机制

---

## 附录：快速启动

如果项目尚未建立规范，执行以下三步：

### 第 1 步：创建术语表

```bash
touch TERMS.md
# 填入 1.3 节的中英术语对照表模板
```

### 第 2 步：集成到 AI 工具

在项目根目录创建 CLAUDE.md（Claude Code）或 .cursorrules（Cursor）：

```markdown
# 项目规范

遵循 cn-coder 中文代码生成规范：

## 命名
- 变量/函数/类/文件名使用英文
- 注释/文档使用中文
- 参考 TERMS.md 中的术语对照表
- Python: snake_case | JS/TS: camelCase | Go: PascalCase/snake_case | Rust: snake_case
- 类名使用 PascalCase + 名词后缀

## 注释
- 所有公共函数/方法必须写中文文档字符串
- 说明"为什么"，不说明"是什么"

## 项目结构
- controller → service → repository 三层
- 错误统一处理
- 统一返回格式 {code, message, data}
```

### 第 3 步：运行代码审查

使用 4.4 节的审查提示词模板，或人工对照 6.x 审查清单逐项检查。
