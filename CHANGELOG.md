# Changelog

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
