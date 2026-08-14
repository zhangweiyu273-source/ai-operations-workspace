# Changelog

## 2026-08-14 - Stage I 首页运营驾驶舱

- 新增只读 `/api/v1/dashboard` 聚合 API 与 Router → Service → Repository 分层，不新增业务表或 AI 调用。
- 首页展示任务、内容、关键词、账号、知识资产概览，以及今日任务与问题复盘提醒；前端通过单一 Dashboard API 加载和刷新数据。
- 增加空数据、部分数据、大量关键词数据、列表截断、详情跳转与单请求加载的后端/前端回归测试。

## 2026-08-14 - Stage H 任务与复盘验收缺口修复

- Task 与 Review 列表新增完整分页元数据和前端分页交互，不再固定只显示前 50 条记录。
- Task 新增负责人和截止日期范围筛选；后端在数据库查询层执行筛选，前端不会只筛当前页。
- 补充任务、复盘分页和任务筛选的后端与 Vitest 回归测试。

## 2026-08-14 - Stage H 运营任务与复盘中心

- 新增 `operation_tasks`、`operation_reviews` 及 Alembic revision `20260814_0008`，任务可真实关联 Account 与 Topic，复盘可真实关联 Task。
- 新增版本化 Task / Review CRUD、分页、搜索、筛选与统计 API；任务支持完成时间和逾期状态计算。
- 新增 `/tasks`、`/reviews` 工作台页面及其新增、编辑、删除、筛选、关联选择和状态修改交互。
- 将任务、复盘业务严格分层为 Router → Service → Repository → Model / Database，并补充服务、仓储和前端专项回归测试。

## 2026-08-14 - Stage F 选题库验收完成

- 新增 Topic 与 TopicKeyword 多对多数据模型、版本化 CRUD、筛选、分页、统计及软删除。
- 选题页面接入真实账号与关键词 API，支持新增、编辑、删除、关键词多选和基础筛选。
- 增加 Topic 后端专项测试、前端交互测试及 PostgreSQL 联调回归。
- 修复 TopicKeyword Migration 缺失 `updated_at` 字段的问题，新增 `20260814_0006`。

## 2026-08-14 - Stage G 知识库

- 新增组织级知识资产、标签关联与 `20260814_0007` Migration。
- 提供知识 CRUD、数据库搜索、分类/标签/状态/优先级筛选、统计及软删除。
- 新增知识库页面与前后端专项自动测试；不包含 AI、RAG 或向量检索能力。

本项目遵循 Keep a Changelog 的结构，并使用语义化版本。

## [Unreleased]

### Phase E - Keyword Library

- Added keyword CRUD, normalized organization-scoped deduplication, soft deletion, filtering, statistics, CSV/XLSX preview import and UTF-8 BOM CSV export.
- Added the `/keywords` production workbench page and API/frontend regression tests.

### Added

- 初始化 Next.js + TypeScript 前端骨架与基础页面测试。
- 初始化 FastAPI + SQLAlchemy 后端骨架、存活与数据库就绪检查。
- 增加 PostgreSQL、前后端 Dockerfile 与 Docker Compose 编排。
- 增加环境变量模板、上传目录隔离和项目治理文档。
- 增加 pytest、Vitest、ESLint、Ruff 基础测试与质量配置。
- 完成 Docker Compose 离线配置校验，并记录 Windows WSL 首次启用与阶段 A 验收状态。
- 修正 Windows Docker 初始化流程对 DISM `3010` 返回码的处理，并补记环境安装回归规则。
- 将 Next.js 升级至 16.3.1，修复生产依赖链中的 PostCSS 与 Sharp 高危漏洞。
- 增加前端容器健康检查和子项目 `.dockerignore`，避免把本地依赖与构建产物发送到 Docker 构建上下文。
- 完成 Windows Docker Desktop、WSL 2、PostgreSQL 17、FastAPI 与 Next.js 三容器完整部署验收及数据库持久卷重启测试。
- 增加 Organization、User 以及 UUID、时间戳、组织范围、审计人和软删除公共模型 Mixins。
- 配置 Alembic，增加首个身份基础表 Migration、默认组织和 Compose 一次性迁移服务。
- 增加 `/api/v1/system`、统一 API 错误结构、request ID、访问日志与服务端异常日志。
- 增加正式工作台 Shell、9 个一级导航路由、当前页面高亮和建设中空状态。
- 增加 PageHeader、EmptyState、Card、TableContainer、LoadingState、ErrorState 与统一 API Client。
- 增加模型、数据库、Migration、错误响应、导航和 API Client 自动测试。
- 增加 Account 领域模型和 `20260814_0002` Migration，统一使用组织范围、审计字段和软删除。
- 增加账号矩阵分层 CRUD API，支持分页、搜索、平台/类型/状态筛选和真实统计。
- 增加账号矩阵页面、新增编辑表单、详情、删除确认、筛选与分页交互。
- 增加 Next.js 同源 API 代理，容器内后端地址由 `BACKEND_INTERNAL_URL` 配置。
- 增加账号 API、持久化、软删除、分页及前端关键交互回归测试。
- 增加 OperationMetric 数据模型、精确金额字段、非负约束、软删除和活动记录防重索引。
- 增加数据中心 CRUD、筛选排序、统一统计、CSV/XLSX 预览确认导入及 CSV 导出 API。
- 增加数据中心指标卡、筛选表格、新增编辑、详情、删除、导入预览和筛选导出页面。
- 增加统一指标口径文档，并完成 1000 条数据分页、筛选和统计测试。

### Fixed

- 修复移动端窄侧栏品牌文字未隐藏导致的裁切问题。
- 完成阶段A-D稳定性修复：增加独立测试数据库、测试库安全护栏及Windows测试入口。
- 增加前端构建锁预检和安全缓存清理命令，确认构建不依赖 `NODE_OPTIONS`。
- 统一账号与运营数据事务异常的回滚日志，补齐运营数据删除失败回滚。
- 将数据中心筛选参数规范化移入Pydantic Query Schema，收窄Router职责。
- 固化Docker `build + force-recreate + migrate + health/API` 运行版本一致性流程。
