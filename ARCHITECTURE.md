# AI运营工作台架构

## 阶段 F：选题库

- `Topic` 是组织范围内的内容生产资产，使用 UUID 主键、审计字段和软删除；通过 `account_id` 关联启用的账号矩阵记录，并校验选题平台与账号平台一致。
- `TopicKeyword` 是 Topic 与 Keyword 的显式多对多关联表；关联表包含 UUID、创建/更新时间，物理关联删除只用于解除关系，Topic 本体删除采用软删除。
- `/api/v1/topics` 提供 CRUD、搜索、分页、平台/账号/状态/内容类型/学科/优先级筛选和统计；关键词只能从关键词库的未删除记录中关联。
- `content_id` 仅作为未来数据中心发布内容关联预留，阶段 F 不实现发布或自动化流程。

## 阶段 G：知识库

- `Knowledge` 是组织范围内的企业知识资产，采用 UUID、审计字段及软删除；正文、摘要、来源、优先级和状态均保存于 PostgreSQL。
- `KnowledgeTag` 为一对多标签表，禁止把多个标签拼接为业务字段；列表标签筛选在数据库完成，避免只筛选当前分页数据。
- `/api/v1/knowledge` 提供 CRUD、分类、标签、统计、搜索、筛选与按更新时间排序。分类由后端配置端点提供，前端不维护独立分类常量。
- 本阶段不包含任何 AI 调用、RAG、Embedding、向量数据库、文件解析或 AI 问答；未来 AI 能力仅通过稳定的 `knowledge_id` 引用知识资产。

## 阶段 H：运营任务与复盘

- `OperationTask` 是组织范围内的执行任务，复用公共 UUID、审计字段和软删除字段；`related_topic_id` 与 `related_account_id` 分别是真实外键，引用 `topics.id` 与 `accounts.id`，不保存名称副本。
- `OperationReview` 通过非空 `task_id` 外键关联一个任务；一个任务可有多条复盘。任务和复盘的删除均为软删除，默认查询排除已删除记录。
- API 层仅承担 HTTP 编排；`OperationTaskService` 与 `OperationReviewService` 负责关联校验、状态转换、完成时间、逾期判断和事务错误处理；Repository 负责 CRUD、分页、筛选和统计查询。
- 任务被改为“已完成”时写入 `completed_at`；改为其他状态时清空该字段。截止时间早于当前 UTC 时间且状态不为“已完成/已取消”时，响应中的 `is_overdue` 为真。
- `/api/v1/tasks` 和 `/api/v1/reviews` 提供 CRUD、分页、搜索、筛选和统计；前端 `/tasks` 与 `/reviews` 使用统一 API Client。该阶段不包含 AI、自动化工作流或首页改造。
- Task 与 Review 列表响应统一包含 `items`、`total`、`page`、`page_size`、`total_pages`，前端每页读取 20 条并提供上一页/下一页导航，避免把固定 50 条误当作全量数据。Task 列表支持 `assignee` 精确筛选，以及 `deadline_from` / `deadline_to` 的截止时间范围筛选；日期范围由前端按本地日期边界转换为 UTC ISO 时间后传入 API。

## 阶段 I：首页运营驾驶舱

- `/api/v1/dashboard` 是只读聚合端点；Router 只负责 HTTP 编排，`DashboardService` 返回稳定响应契约，`DashboardRepository` 负责跨 Task、Topic、Keyword、Account、Knowledge、Review 的只读数据库聚合。
- Dashboard 不新增业务表、不调用 AI。单次前端请求获得任务、内容、关键词、账号、知识、今日任务和复盘提醒，避免首页扇出请求多个业务 API。
- “今日任务”以任务开始日期或截止日期为当天计算；待复盘为已完成且没有未删除复盘记录的任务；逾期排除已完成和已取消状态。列表展示最多 8 条今日任务和 5 条带问题摘要的近期复盘，限制首页负载。

## 1. 架构目标

采用前后端分离的模块化单体。V1 优先保证数据一致性、低运维复杂度和清晰边界；未来可在不重写业务模型的前提下扩展多组织、权限、异步任务、对象存储与独立 AI 服务。

## 2. 系统拓扑

```text
Browser
  │ HTTP/JSON
  ▼
Next.js frontend ──────► same-origin API proxy ──────► FastAPI /api/v1
                            │
                   service / repository
                    ┌───────┴────────┐
                    ▼                ▼
              PostgreSQL       AI Provider Layer
                                      │
                             DeepSeek / OpenAI / other
```

外部平台接入不属于阶段 A。未来适配器应位于独立 integration 边界，不把平台字段扩散到核心领域模型。

## 3. 目录结构

- `frontend/`：Next.js App Router、TypeScript、页面与组件、前端测试。
- `backend/app/api/`：版本化 HTTP 路由，只负责协议、校验和响应。
- `backend/app/core/`：配置、日志、安全等横切能力。
- `backend/app/db/`：数据库引擎、会话、模型基础设施。
- `backend/app/models/`：SQLAlchemy 领域模型。
- `backend/app/schemas/`：Pydantic API 契约。
- `backend/app/services/`：业务用例和跨资源编排。
- `backend/app/repositories/`：后续领域数据库访问边界。
- `backend/migrations/`：Alembic 版本历史；应用启动不调用 `create_all`。
- `backend/tests/`：后端单元与 API 测试。
- `frontend/src/components/layout/`：全局工作台 Shell 与导航。
- `frontend/src/components/ui/`：克制的复用 UI 基础组件。
- `frontend/src/lib/api/`：环境变量驱动的统一 API Client。
- `frontend/src/features/accounts/`：账号矩阵页面、API 契约与交互组件。
- `frontend/src/features/data-center/`：运营数据列表、表单、统计、导入导出交互。
- `storage/uploads/`：本地开发上传挂载点；生产可替换对象存储。
- `docker-compose.yml`：本地及单机部署编排。

随着业务实现，后端在既有分层内按领域扩展；前端按功能路由和共享组件扩展。API 层只负责协议与校验，service 负责用例，repository 负责持久化细节。

## 4. 数据设计原则

PostgreSQL 是事实来源。核心实体采用 UUID 主键、时区感知时间，预留 `organization_id`、`created_by`、`updated_by`；重要业务表使用 `is_deleted`/`deleted_at` 软删除。金额使用定点数，枚举在数据库兼容与演进成本之间选择字符串约束。所有结构变化由 Alembic 管理。

统一 ID 策略为 UUID。阶段 B 建立：

- `organizations`：组织身份边界，V1 migration 写入一个默认组织，但业务代码不得假设系统永远只有一个组织。
- `users`：隶属组织的基础用户，角色限制为 `admin/operator/sales/owner/member`，V1 不实现复杂 RBAC。
- `accounts`：组织范围内的公域账号档案，revision `20260814_0002` 创建；使用公共审计字段和 `is_deleted` 软删除，默认查询不返回已删除记录。
- `operation_metrics`：revision `20260814_0003` 创建，保存账号在日期/内容维度的运营指标；计数使用 `BigInteger`，金额使用 `Numeric(14,2)`。
- `UUIDPrimaryKeyMixin`、`TimestampMixin`、`OrganizationScopeMixin`、`AuditActorMixin`、`SoftDeleteMixin` 和组合后的 `BusinessModelMixin`，供后续业务表复用。

计划领域包括组织与用户、账号、运营数据、关键词、选题、线索与跟进、知识条目、任务、每日复盘、AI 分析记录。跨领域引用优先使用稳定 ID，并为高频筛选字段建立可验证索引。

## 5. API 关系

- 公共前缀：`/api/v1`。
- `GET /health/live`：仅验证应用进程，可用于容器存活检查。
- `GET /health/ready`：执行 `SELECT 1`，验证 PostgreSQL 就绪状态。
- `GET /system`：返回应用版本、环境和真实数据库状态。
- `/accounts`：账号列表与新增；列表支持分页、账号名称/定位/目标用户搜索，以及平台、账号类型、状态筛选。
- `/accounts/{id}`：账号详情、全量更新与软删除。
- `/operation-metrics`：运营数据 CRUD、分页、日期/平台/账号/内容类型筛选、搜索和排序。
- `/operation-metrics/statistics`：按同一组筛选条件聚合基础指标，计算口径见 `METRICS.md`。
- `/operation-metrics/import`：CSV/XLSX 预览与确认导入；`confirm=false` 只校验，`confirm=true` 才写入。
- `/operation-metrics/export`：按当前筛选条件导出 UTF-8 BOM CSV。
- 业务 API 后续按资源划分，统一分页、筛选、错误结构和审计字段。

错误响应统一为 `{ "error": { "code", "message", "request_id", "details?" } }`。请求中间件生成或透传 `X-Request-ID` 并记录方法、路径、状态码与耗时。400、404、422、500 分层处理，500 仅在服务端记录堆栈。

浏览器默认通过同源 `/api/v1` 访问 Next.js 代理；代理通过 `BACKEND_INTERNAL_URL` 访问 FastAPI。开发者也可用 `NEXT_PUBLIC_API_BASE_URL` 切换 API 入口，代码不写死容器网络地址。V1 的组织上下文由可配置的 `DEFAULT_ORGANIZATION_ID` 提供，并允许 `X-Organization-ID` 覆盖，为后续登录态和多组织鉴权保留替换边界。

## 6. AI 调用关系

后续在 `backend/app/ai/` 建立 provider 接口、厂商实现、schemas 和 prompts。业务服务只调用 `AIService.generate/analyze/extract`。密钥由环境变量注入；未配置或厂商故障时只影响 AI 请求，分析结果持久化后可审计。

## 7. 配置与文件

配置由环境变量统一注入，`.env.example` 仅包含安全占位值。容器内上传路径为 `/app/storage/uploads`，通过 volume 与源码隔离。云端可替换为对象存储而不改变业务 API。

## 8. 部署

本地 Windows 使用 Docker Compose 启动 PostgreSQL、FastAPI 和 Next.js。Linux 云服务器沿用相同镜像和环境变量；生产环境应增加 TLS 反向代理、备份、监控、密钥管理和独立持久卷。

Compose 中 `migrate` 是一次性服务：等待 PostgreSQL healthy 后执行 `alembic upgrade head`；只有 migration 成功退出，backend 才启动。该顺序避免应用副本自行建表和并发迁移。

测试数据库使用 Compose `test` profile 中独立的 `test-db` 服务、`postgres_test_data` 卷和默认5433端口。`TEST_DATABASE_URL` 必须指向名称以 `_test` 结尾的数据库，禁止复用开发数据库。

镜像内代码来自 build context，不挂载源码。任何代码变化后必须执行 `docker compose up -d --build --force-recreate`；单纯 restart 只重启旧镜像。运行版本通过 Migration head、健康检查和关键API联合确认。

## 9. 阶段 A 决策记录

- 模块化单体，避免 V1 微服务运维成本。
- 前后端分别构建为非 root 容器。
- 健康检查拆分 liveness/readiness，数据库异常可被准确识别。
- Next.js 使用 standalone 输出以缩小生产镜像。
- 阶段 A 当时仅建立数据库连接基础设施；业务模型和首个 migration 已在阶段 B 实施。

## 10. 阶段 B 决策记录

- 首个 revision `20260814_0001` 创建 `organizations` 与 `users`，并写入默认组织。
- 软删除仅由后续重要业务表通过公共 Mixin 使用；身份基础表不提前叠加不确定字段。
- 前端工作台提供 9 个一级导航；私域运营中心和用户洞察中心不启用。
- 不引入 Redux 等全局状态库；HTTP 访问统一经过轻量 API Client。
- AI 目录只建立边界占位，不调用任何模型提供商。

## 11. 阶段 C 决策记录

- 账号矩阵采用 Model、Repository、Service、Schema、Router 分层，页面不保存业务事实数据。
- 平台与账号类型保留字符串扩展能力；状态限制为“启用 / 停用 / 测试中”，并由 API Schema 与数据库约束双重校验。
- 账号统计基于组织下未删除的全量数据计算，不受当前列表筛选和分页影响。
- 删除仅设置 `is_deleted=true`；详情、列表、搜索均默认隔离软删除记录。

## 12. 阶段 D 决策记录

- `platform` 是账号平台的历史快照，API 和导入模板不接受独立平台输入；新增或更换账号时后端从 Account 同步，账号日后改平台不会篡改历史数据。
- 活动记录重复键为 `organization_id + account_id + metric_date + SHA256(content_url 或 content_title)`；软删除后允许重新录入同一内容。
- 导入采用整批原子策略：任何校验错误都会阻止全批写入；已存在及文件内重复行计入 `duplicate_count` 并跳过，不视为格式错误。
- Excel 解析使用 MIT License 的 `openpyxl`，文件上传使用 Apache-2.0 License 的 `python-multipart`；两者仅位于后端导入边界。
- 列表最大单页 100 条，统计在 PostgreSQL 聚合，不把全量数据加载到浏览器；已用 1000 条数据验证分页、筛选和统计。

## 13. 阶段 A-D 稳定性修复

- 数据库事务异常必须先 rollback，再以组织ID和资源ID记录服务端异常；响应仍由统一错误处理器隐藏堆栈。
- 数据中心查询参数由 Pydantic Query Schema 负责规范化，Router 只做HTTP协议编排。
- readiness 必须真实执行 PostgreSQL `SELECT 1`；实测数据库停止时返回503，恢复后返回200。
- 前端构建不依赖 `NODE_OPTIONS`；`.next/lock` 表示并发进程，禁止通过盲删锁文件掩盖正在运行的进程。
## Phase E: Keyword Library

- `keywords` is organization-scoped. `keyword` preserves the entered text; `normalized_keyword` is used only for deduplication.
- Normalization applies Unicode NFKC, trims outer whitespace, collapses repeated whitespace, and case-folds. It does not apply semantic/NLP merging.
- Active records are unique on `(organization_id, normalized_keyword)`; soft-deleted records may be re-entered.
- Future Topic-to-Keyword relationships must use a many-to-many association table, not a copied text field.
