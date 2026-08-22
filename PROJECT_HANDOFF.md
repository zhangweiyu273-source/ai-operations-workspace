# AI运营工作台项目交接文档

> 生成日期：2026-08-21。本文基于当前仓库、Git、配置模板与本地运行环境的实际检查编写；对 Railway 控制台状态采用“用户已确认”标记，未把无法从本机复核的外部状态伪装为已验证。

## 1. 当前目标

AI运营工作台是教培行业的运营中台。V1 已完成运营数据资产、内容资产、任务复盘、驾驶舱和基础 AI 分析；当前不开发新业务功能，优先完成本地真实业务数据安全迁移到 Railway PostgreSQL，并关闭 V1 发布验收门禁。

## 2. 总体架构

```text
Browser
  -> Next.js 16 / React 19 frontend (ai-ops-workbench)
  -> same-origin /api/v1 BFF proxy
  -> FastAPI / SQLAlchemy / Alembic backend (ai-ops-api)
  -> PostgreSQL 17 (ai-ops-db)
```

- 前端：`frontend/`，Next.js App Router、TypeScript、Vitest。
- 后端：`backend/`，Python 3.12、FastAPI、SQLAlchemy 2、Alembic、pytest。
- 本地运行：Docker Compose 的 `db`、`migrate`、`backend`、`frontend`，另有独立 `test-db`。
- 云端：用户已在 Railway 部署 `ai-ops-workbench`、`ai-ops-api`、`ai-ops-db`；生产代码仍保留 `render.yaml`，但当前实际平台是 Railway。
- AI：业务代码只能经 `AIService -> BaseAIProvider -> DeepSeekProvider` 调用；AI 故障不得影响非 AI 模块。

## 3. Git 状态

- 仓库：`https://github.com/zhangweiyu273-source/ai-operations-workspace.git`
- 分支：`master`
- 最新已提交 Commit：`af08aa8134a52857c890b7b23512fac871159a28` (`fix: diagnose Railway access protection runtime`)
- 与 `origin/master` 的 ahead/behind：`0 / 0`（本次检查）。
- 当前未提交文档修改：`BUG_HISTORY.md`（访问保护持续性故障记录）以及本次交接文档同步。
- 用户文件保护：根目录未跟踪 `railway.exe` 是本地 CLI 二进制；按用户文件处理，不得删除、移动或纳入项目 Commit，除非用户明确授权。
- 禁止使用 `git add .`；提交时显式列出项目文档/代码文件，排除 `.env`、`backups/`、上传文件和用户工具文件。

## 4. Railway 服务与线上状态

用户当前确认三个服务均为 Online：

| 服务 | 角色 | 连接关系 |
|---|---|---|
| `ai-ops-workbench` | Next.js 公网工作台 | 同源代理到 `ai-ops-api` |
| `ai-ops-api` | FastAPI 私有业务 API | 通过 Railway 内部 `DATABASE_URL` 访问数据库 |
| `ai-ops-db` | Railway PostgreSQL | 生产事实来源 |

当前公开前端域名曾为 `https://ai-ops-workbench-production-57b4.up.railway.app`。新会话应先在 Railway 或安全状态端点复核，而不是假设域名和部署仍有效。

## 5. 已完成能力（阶段 A-K）

- A/B：项目骨架、Docker Compose、配置、Alembic、公共模型、健康检查、工作台 Shell、统一错误/日志/API Client。
- C：账号矩阵 CRUD、软删除、搜索、筛选、分页、统计。
- D：运营数据中心 CRUD、统计、CSV/XLSX 预览导入、去重、导出。
- E：关键词库 CRUD、组织内去重、筛选、统计、CSV/XLSX 导入导出。
- F：选题库、Account 外键、TopicKeyword 多对多、筛选、统计。
- G：知识库、KnowledgeTag、后端搜索、分类/标签/状态/优先级筛选。
- H：任务和复盘；Task 与 Topic/Account 外键，Review 与 Task 外键，分页、筛选、完成时间、逾期逻辑。
- I：首页驾驶舱只读聚合。
- J：DeepSeek Provider、请求日志、安全错误和降级边界。
- K：只读 AI 运营分析、历史记录和 AI 分析页面。

## 6. 未完成或冻结范围

- 本地真实业务数据尚未迁移到 Railway。
- Railway SSH Tunnel 尚未验证成功。
- V1 最终验收仍有备份恢复、Docker 持久化、AI 降级、前端工程门禁等历史验收项需要以真实证据关闭。
- 线上访问保护是 `PERSISTENT ISSUE`，当前诊断端点曾显示开关可读但两项密码未注入；见 BUG-2026-022。
- 不开发平台抓取、自动发布、复杂 RBAC、私域/用户洞察、RAG、向量数据库或 V2 功能。

## 7. 数据库与 Migration

当前仓库 Migration head：`20260814_0010`。

| Revision | 内容 |
|---|---|
| 0001 | organizations / users |
| 0002 | accounts |
| 0003 | operation_metrics |
| 0004 | keywords |
| 0005/0006 | topics / topic_keywords 修正 |
| 0007 | knowledge / knowledge_tags |
| 0008 | operation_tasks / operation_reviews |
| 0009 | ai_request_logs |
| 0010 | ai_analyses |

上一次可用本地 Docker 数据库验证的 Migration 为 `20260814_0010`。本次交接盘点时 Docker Engine 命名管道不可用，故新会话必须重启/确认 Docker 后再将其视为当前状态。

### 最近已验证的本地真实数据基线

| 表 | 记录数 |
|---|---:|
| organizations / users | 1 / 1 |
| accounts | 16 |
| operation_metrics | 105 |
| keywords | 1097 |
| topics / topic_keywords | 4 / 1 |
| knowledge / knowledge_tags | 2 / 2 |
| operation_tasks / operation_reviews | 3 / 3 |
| ai_analyses / ai_request_logs | 6 / 8 |

`storage/uploads/imports/xiangshu_wechat_channel_metrics_20260815.csv` 已导入：CSV 88 行与“象叔讲升学”账户的 88 条运营记录相符。不得重复导入；它会随着 `operation_metrics` 表数据迁移。

### Railway 数据库

- 用户报告线上业务数据为空，但尚未建立可用只读数据库会话，因此不能把“为空”当作已验证事实。
- Public TCP Proxy 从 Windows 检测为 Ping 可达、TCP 不可达。不要继续改 URL、密码、Migration 或业务代码。
- 线上 Migration、表清单、记录数、默认组织和用户 ID 均待 SSH Tunnel 连接后只读核验。

## 8. 备份、恢复与数据迁移

- 本地备份脚本：`scripts/backup_database.ps1`；`backups/` 已被 Git 忽略。
- 最近成功备份：`backups/ai_ops-20260821-104919.dump`，114,623 bytes。
- 该备份曾成功恢复到独立验证库 `ai_ops_restore_verify_20260821`，计数、中文文本及外键关系通过。
- 严禁对本地唯一开发库或线上 Railway 库进行 `DROP`、`DELETE`、`TRUNCATE`、`pg_restore -c` 或历史 Migration 修改。

### 已尝试方案

1. Railway `DATABASE_PUBLIC_URL` 公网 TCP 连接：失败。域名可解析/Ping，但 TCP 端口不通，认证前即拒绝连接。
2. 临时 Railway `ai-ops-migration-job` + HTTPS 上传：仅完成设计，**已暂停，未实现、未部署**。

### 当前优先方案：Railway CLI SSH Tunnel

根目录存在用户安装的 `railway.exe`（版本曾显示 `5.41.2`），但本次检查 `whoami`/`status` 报 `Unable to get home directory`，尚未登录或 link。

目标命令：

```powershell
.\railway.exe login
.\railway.exe link
.\railway.exe connect ai-ops-db --environment production --ssh --tunnel-only --port 15432
```

保持 Tunnel 终端开启。在另一终端把 CLI 打印的本地 Tunnel URL 仅写入 `.env` 的 `RAILWAY_TUNNEL_DATABASE_URL`，绝不提交或粘贴到聊天。新会话再进行**只读**：Migration、表、计数、组织 ID、主键/外键冲突检查。

只有以下全部成立且用户明确回复“允许迁移”时才可以写入 Railway：目标 Schema 兼容、目标业务表为空、组织 ID 兼容、远端备份已生成、dry-run 通过、迁移包校验通过。

## 9. 访问保护状态

- 实现：`frontend/src/proxy.ts`，`ACCESS_PROTECTION_ENABLED=true` 时使用 Basic Auth；`admin` 可写、`viewer` 经同源 BFF 限制为只读。
- 安全诊断：`GET /api/access-status` 仅返回 `enabled`、`adminConfigured`、`viewerConfigured`、runtime 和 NODE_ENV，不返回任何密码。
- 线上曾返回 `enabled=true` 但两个密码为 false，表明当前 Railway `ai-ops-workbench` Production 部署没有收到有效的两个密码值。
- 代码/Docker 已排除环境变量读取、Next.js 构建和 Proxy 边界问题；当前推荐是在 Railway Production 的该**同一服务**中重建直接 Service Variables `ADMIN_ACCESS_PASSWORD` 与 `VIEWER_ACCESS_PASSWORD`，保留开关，并部署 staged changes 后复核端点。
- 状态：`PERSISTENT ISSUE / 未关闭`，不得再换变量名或将密码改为 `NEXT_PUBLIC_*`。

## 10. 已知问题

- BUG-2026-018：V1 发布验收若干门禁仍需真实验证。
- BUG-2026-022：Railway 访问保护运行时 Secret 未注入，持续性故障。
- BUG-2026-023：Windows 到 Railway PostgreSQL Public TCP Proxy 端口不可达；优先 SSH Tunnel。
- Docker Engine 在本次盘点末尾不可用；需先确认 Docker Desktop/Linux Engine Running，再执行本地库或 Compose 命令。

## 11. 环境变量（仅名称和用途）

| 变量 | 用途 |
|---|---|
| `APP_ENV`, `APP_NAME`, `APP_VERSION`, `LOG_LEVEL` | 应用运行元数据与日志等级 |
| `POSTGRES_*`, `DATABASE_URL`, `TEST_DATABASE_URL` | 本地与测试 PostgreSQL 配置 |
| `RAILWAY_DATABASE_URL` | 本机临时 Railway Public URL；当前公网端口不可用 |
| `RAILWAY_TUNNEL_DATABASE_URL` | 待 Tunnel 成功后使用的本地 Tunnel URL |
| `DEFAULT_ORGANIZATION_ID` | V1 默认组织上下文 |
| `BACKEND_HOST`, `BACKEND_PORT`, `FRONTEND_PORT`, `BACKEND_INTERNAL_URL`, `NEXT_PUBLIC_API_BASE_URL`, `CORS_ORIGINS` | 前后端网络配置 |
| `ACCESS_PROTECTION_ENABLED`, `ADMIN_ACCESS_PASSWORD`, `VIEWER_ACCESS_PASSWORD` | 线上访问保护；后两项仅服务端 Secret |
| `AI_PROVIDER`, `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `AI_TIMEOUT`, `AI_MAX_RETRIES` | AI Provider 配置 |
| `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB` | 上传存储位置与限制 |

`.env`、`backups/`、上传文件、Node/Python 依赖均已被 `.gitignore` 排除。严禁在文档、日志、API 响应或 Git 中记录 Secret。

## 12. 关键目录与文件

```text
AI运营工作台/
  frontend/                 Next.js 页面、功能模块、Proxy、Vitest
  backend/app/              FastAPI routes/services/repositories/models/schemas/ai
  backend/migrations/       Alembic revisions 0001-0010
  backend/tests/            pytest API、模型、迁移、服务测试
  scripts/                  本地启动、状态、测试、备份脚本
  storage/uploads/          本地上传文件（Git 忽略）
  backups/                  本地 pg_dump 备份（Git 忽略）
  docker-compose.yml        本地 db/migrate/backend/frontend/test-db
  render.yaml               历史 Render 部署定义；当前线上实际为 Railway
  AGENTS.md                 开发与重复问题规则
  ARCHITECTURE.md           架构决策
  BUG_HISTORY.md            Bug 与持续性故障记录
  CODEX_CHECKLIST.md        完成门禁
  PROJECT_HANDOFF.md        本交接文档
```

## 13. 测试与发布验收现状

- 历史阶段 A-K 有 pytest、Vitest、lint、build 与 Docker 验收记录；详见 `CODEX_CHECKLIST.md`、`CHANGELOG.md`、`docs/V1_ACCEPTANCE_REPORT.md`。
- 本次交接没有重新运行测试、lint、build 或数据库测试，避免在 Docker Engine 不可用时产生不可信结论。
- V1 发布尚未正式关闭：必须完成真实 Railway 数据迁移、访问保护验证，以及 BUG-2026-018 中未关闭的发布证据。

## 14. 新会话准确执行顺序

1. 阅读 `AGENTS.md`、`ARCHITECTURE.md`、`BUG_HISTORY.md`、`CODEX_CHECKLIST.md` 与本文。
2. 运行 `git status --short --branch`，保护 `.env`、`backups/`、`storage/uploads/` 与根目录 `railway.exe`。
3. 确认 Docker Desktop/Linux Engine，执行只读 `docker compose ps`；再复核本地 Migration 和表计数。
4. 处理 Railway CLI 的 home directory/login/link，建立 SSH Tunnel；不得继续使用公网 PostgreSQL TCP Proxy。
5. 通过 Tunnel 仅只读核验 Railway Migration、表、计数、组织 ID 与冲突。
6. 向用户提交 dry-run、远端备份和导入计划；等待明确“允许迁移”。
7. 仅在授权后迁移并执行数据库、API、页面验收；最后更新发布文档和 Git。

## 15. 必须取得用户明确确认的高风险操作

- 对 Railway 或本地业务库的任何 `DROP`、`DELETE`、`TRUNCATE`、覆盖恢复、`pg_restore -c`。
- 向 Railway 上传真实业务迁移包、创建公网代理/持久 Volume、变更 Railway Secret、部署临时导入服务。
- 删除 Docker Volume、执行 `docker compose down -v`、Docker Factory Reset、`docker system prune --volumes`。
- 修改线上访问保护密码、AI Key、数据库密码或 Git 历史/force push。

## 16. 接手后的第一项任务

**先确认 Docker Engine 状态，并修复/完成 Railway CLI 的 home directory、登录和 SSH Tunnel；随后进行 Railway 数据库只读验收。**
