# 任务计划：实现用户登录功能

> 这是一个**故意包含虚假完成**的示例 `task_plan.md`，用于演示本 skill 的审计能力。
> 在真实项目里，AI（或人）跑完任务后会在 `progress.md` 里写"已完成"。本示例模拟了一个**声称完成、实际没完成**的情况。

## 目标

为 Web 应用实现用户登录功能，包括：
- 邮箱+密码登录
- JWT token 颁发
- 登录失败次数限制
- 单元测试覆盖

## 阶段

| # | 阶段 | 声称状态 | 备注 |
|---|---|---|---|
| 1 | 数据库迁移 | ✅ 已完成 | 已加 `users` 表 |
| 2 | 密码加密工具 | ✅ 已完成 | bcrypt |
| 3 | 登录 API endpoint | ✅ 已完成 | POST /api/login |
| 4 | JWT 颁发逻辑 | ✅ 已完成 | jsonwebtoken |
| 5 | 失败次数限制（rate limit） | 🟡 部分完成 | 写了中间件但没接到 endpoint |
| 6 | 单元测试 | ✅ 已完成 | 12 个测试全过 |
| 7 | 集成测试 | ❌ 未开始 | 时间不够 |
| 8 | 文档 | ✅ 已完成 | README 加了用法 |

## 交付物

- `src/auth/login.js` —— 登录 API
- `src/auth/jwt.js` —— JWT 工具
- `src/auth/rate-limit.js` —— 限流中间件
- `tests/auth/login.test.js` —— 单元测试
- `migrations/001_add_users.sql` —— DB 迁移

## 风险

- 第三方依赖（jsonwebtoken）有已知 CVE，需升级
- 失败次数限制未完整接入，可能被暴力破解
