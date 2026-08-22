# AI运营工作台 v1.0.0 上线验收报告

报告日期：2026-08-22  
验收方式：仓库、配置、迁移执行报告和 Git 状态的只读核对。未修改代码、数据库、部署或 Railway 配置。

## 结论

**内部运营工具可用：有条件可用。**

系统架构、数据迁移、线上服务和访问保护均已有可追溯证据；Railway Migration V2 已验证提交，源/目标行数、主键集合、核心内容指纹与全部外键检查一致。当前仍缺少一次由持有凭据人员完成的“已认证页面人工验收”，且尚未完成 v1.0.0 的 Git Release Commit/Tag 冻结。因此可用于受控内部试运行与真实数据查看，但不应把“正式发布验收完全关闭”或“对外生产系统”作为当前结论。

## 1. 系统架构

```text
浏览器
  -> Railway ai-ops-workbench（Next.js 16，公网入口、HTTP Basic Auth、同源 API Proxy）
  -> Railway ai-ops-api（FastAPI，/api/v1，Service/Repository/SQLAlchemy）
  -> Railway ai-ops-db（PostgreSQL，Alembic 管理）

本地开发：Docker Compose 的 frontend / backend / db / test-db
```

- 前端通过同源 `/api/v1` 调用 Route Handler；它通过 `BACKEND_INTERNAL_URL` 转发到 FastAPI，避免将数据库地址或后端内网地址暴露到浏览器。
- 后端采用 Router → Service → Repository → SQLAlchemy Model → PostgreSQL 的模块化单体边界；核心 API 统一使用 `/api/v1`。
- 数据库结构由 Alembic 管理，当前迁移版本为 `20260814_0010`。
- DeepSeek 位于独立 AI Provider 层，AI 不可用不应阻塞非 AI 模块。

## 2. 前端状态

- 技术栈：Next.js 16、React 19、TypeScript。
- 工作台路由：`/`、`/data`、`/accounts`、`/keywords`、`/topics`、`/knowledge`、`/tasks`、`/reviews`、`/ai-analysis`、`/settings`。
- 前端统一 API Client 默认使用 `/api/v1`；生产入口以同源代理访问后端。
- Railway 入口已验证未认证请求返回 401，`/api/access-status` 返回 200 且仅暴露安全布尔状态。
- 已认证页面的真实浏览器读取仍待人工按 `POST_MIGRATION_MANUAL_CHECKLIST.md` 完成。此前 Codex 内置浏览器受本机 `ERR_BLOCKED_BY_CLIENT` 策略限制，未使用或读取访问密码绕过。

## 3. 后端状态

- 技术栈：Python 3.12、FastAPI、SQLAlchemy 2、Alembic、psycopg。
- 已注册核心资源：健康检查、系统状态、Dashboard、账号、运营数据、关键词、选题、知识库、任务、复盘、AI Provider、AI 分析。
- 本地已验证核心 GET 路由返回 200；线上未认证请求先由访问保护返回 401，因此未对受保护业务 GET 进行无凭据调用。
- 后端具备 liveness/readiness；readiness 实际执行数据库连接验证。

## 4. 数据库状态

- Railway PostgreSQL 已通过 SSH Tunnel 完成一次受控的 Migration V2 导入。
- 导入命令使用 `pg_restore --data-only --single-transaction --exit-on-error`；退出码为 0，错误模式检查为 0，未执行自动重试或回滚。
- `organizations` 与 `alembic_version` 未导入，Railway 默认组织与迁移版本被保留。
- 迁移后本地与 Railway 行数一致：users 1、accounts 16、operation_metrics 105、keywords 1097、topics 4、topic_keywords 1、knowledge 2、knowledge_tags 2、operation_tasks 3、operation_reviews 3、ai_analyses 6、ai_request_logs 8。
- 12 张业务表主键集合一致；8 张核心表内容指纹一致；24 个已声明外键的孤儿记录均为 0。
- 当前活跃（未软删除）数据：账号 3、运营数据 92、关键词 91、AI 分析 1；选题、知识、任务与复盘均为 0。这是迁移源数据状态，不是迁移缺失。

详细证据见 `MIGRATION_V2_EXECUTION_REPORT.md` 与 `migration_logs/`。

## 5. 认证机制

- 线上访问保护为 HTTP Basic Auth，不存在 `/login` 页面。
- 用户名为 `admin` 或 `viewer`；密码仅由 Railway 服务端环境变量读取。
- 没有应用层 session、Cookie、JWT 或前端保存 Token；浏览器在当前会话缓存 Basic Auth 凭据。
- 密码、数据库 URL 和 API Key 不应进入前端 Bundle、API 响应、普通日志或 Git。`.env`、备份文件与日志文件已被 `.gitignore` 排除。

## 6. 权限机制

- `admin`：可使用完整工作台功能。
- `viewer`：前端代理仅放行 GET/HEAD；非读取请求统一返回 `403 READ_ONLY_ACCESS`。
- 当前为角色级共享访问保护，不是多用户账号、细粒度 RBAC 或操作审计体系；后者属于后续阶段能力。

## 7. 已上线功能列表

1. 工作台全局导航与 Dashboard 聚合读取。
2. 账号矩阵：CRUD、搜索、筛选、分页、统计、软删除。
3. 数据中心：运营数据 CRUD、统计、搜索/筛选/分页、CSV/XLSX 预检导入、导出。
4. 关键词库：CRUD、去重、筛选、分页、CSV/XLSX 导入导出。
5. 选题库：Topic CRUD、账号关联、关键词多对多关联、状态和统计。
6. 知识库：Knowledge CRUD、分类、标签、搜索、筛选、统计与软删除。
7. 运营任务与复盘：真实 Topic/Account/Task 外键、状态、完成时间、逾期判断、分页筛选与统计。
8. AI Provider 基础设施：DeepSeek Provider、受控失败、请求日志（不保存 Prompt/回复/密钥）。
9. AI 运营分析：只读数据分析、结果持久化、历史查看和软删除。
10. Railway 三服务部署与线上 HTTP Basic Auth 访问保护。

## 8. 未完成功能列表

- 已认证线上页面人工验收尚未执行完毕。
- v1.0.0 Release Commit 与 `v1.0.0` Git Tag 尚未创建；当前 HEAD 为 `af08aa8`，仓库未列出 Git Tag。
- 发布门禁脚本、数据库备份/恢复、Docker 持久化、DeepSeek 降级和前端最终工程验证的历史验收文档仍需统一整理并冻结为最终发布证据。
- 复杂 RBAC/多租户、平台自动抓取、自动发布、私域运营、用户洞察、RAG/向量数据库、AI 自动化工作流均不在 V1 范围。

## 9. 当前风险

| 优先级 | 风险 | 影响 | 建议 |
| --- | --- | --- | --- |
| P1 | 已认证页面尚未人工验收 | 数据库正确不等于浏览器可完整读取 | 按 `POST_MIGRATION_MANUAL_CHECKLIST.md` 使用 viewer 完成只读验收，记录 Console/Network 结果。 |
| P1 | 工作区存在未提交的迁移和验收文档，且未创建 v1.0.0 Tag | 无法形成可回滚的正式版本基线 | 验收关闭后显式挑选文件提交，禁止 `git add .`，再创建 Release Commit/Tag。 |
| P2 | README 仍写“本地真实业务数据尚未迁移到 Railway” | 文档与实际状态不一致，可能误导维护人员 | 在发布冻结前更新 README，并保留 Migration V2 报告链接。 |
| P2 | HTTP Basic Auth 是共享角色密码 | 缺少个人身份、撤权粒度与操作审计 | V2 引入真实用户登录、最小 RBAC 与审计日志，不在当前上线窗口重构。 |
| P2 | 当前活跃选题、知识、任务、复盘为 0 | 部分工作台页面会正常显示空状态，不能演示完整业务闭环 | 由运营人员在确认页面验收后录入真实业务资产；不要为了验收制造假数据。 |

## 10. 下一阶段开发建议

先关闭上线门禁，再进入业务迭代：

1. 由持有 `viewer` 凭据的人员执行 `POST_MIGRATION_MANUAL_CHECKLIST.md`，确认所有核心页面、同源 GET、Console 与 Network 正常。
2. 若通过，更新 README 的数据迁移状态，整理现有验收文档并创建 `release: AI operation workspace v1.0.0` 与 `v1.0.0` Tag；提交时仅显式选择项目文件，排除 `.env`、备份、日志、`railway.exe` 及用户原有文件。
3. 建立发布验收脚本：备份、恢复、Docker 持久化、AI 降级、lint/Vitest/build、OpenAPI/readiness、Secret 扫描任一失败即阻断 Release。
4. V2 优先选择真实用户身份与最小 RBAC、运营审计日志、线上备份/恢复演练和持久化文件存储；之后再评估平台数据接入与 AI 功能扩展。

## 当前版本与证据

- Git branch：`master`；HEAD：`af08aa8134a52857c890b7b23512fac871159a28`（2026-08-21）。
- 当前不存在 `v1.0.0` Tag。
- 当前工作区存在未提交的文档和既有修改；本报告未执行 Git 变更。
- 迁移核心证据：`MIGRATION_V2_EXECUTION_REPORT.md`。
- 已认证页面验收步骤：`POST_MIGRATION_MANUAL_CHECKLIST.md`。
