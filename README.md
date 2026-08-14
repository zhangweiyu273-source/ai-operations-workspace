# AI运营工作台

面向教培行业的 AI 运营中台。当前已完成数据底座、全局工作台、账号矩阵和数据中心。数据中心支持手动 CRUD、统一统计、CSV/XLSX 预览导入和筛选导出。

## 技术栈

## 关键词库

关键词库位于 <http://localhost:3000/keywords>，支持单条录入、组合筛选、组织内去重、CSV/XLSX 预览导入和筛选结果导出。导入必填列为“关键词”。

- Frontend: Next.js 16、React 19、TypeScript
- Backend: Python 3.12、FastAPI、SQLAlchemy 2、Alembic
- Database: PostgreSQL 17
- Runtime: Docker Compose
- Tests: pytest、Vitest、Testing Library

## 快速启动（推荐）

先安装 Git、Docker Desktop（含 Compose），然后：

```powershell
Copy-Item .env.example .env
docker compose up -d --build --force-recreate
docker compose ps
```

访问：

- 前端：<http://localhost:3000>
- API 文档：<http://localhost:8000/docs>
- 存活检查：<http://localhost:8000/api/v1/health/live>
- 数据库就绪检查：<http://localhost:8000/api/v1/health/ready>
- 系统状态：<http://localhost:8000/api/v1/system>
- 账号矩阵：<http://localhost:3000/accounts>
- 数据中心：<http://localhost:3000/data>

首次运行前请修改 `.env` 中的数据库密码。`.env` 已被 Git 忽略。

## 不使用 Docker 的开发方式

需要本地 PostgreSQL，并将 `.env` 的 `DATABASE_URL` 主机改为可访问地址。

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

## 前端构建

项目不依赖 `NODE_OPTIONS`。Windows PowerShell 禁止执行 `npm.ps1` 时使用 `npm.cmd`：

```powershell
cd frontend
npm.cmd run build
```

不要并发运行 `next dev` 和 `next build`，两者共用 `.next`。构建前置检查发现 `.next/lock` 时会明确终止；先停止占用进程，确认没有并发 Next.js 进程后才可执行：

```powershell
npm.cmd run build:clean
```

`build:clean` 会删除可再生成的 `.next` 缓存，不会删除源码或业务数据。

## 测试

普通单元和API测试：

```powershell
cd backend
pytest
ruff check .

cd ..\frontend
npm test
npm run lint
npm run build
```

PostgreSQL 集成测试必须使用独立的 `ai_ops_test` 数据库，禁止指向开发库。Windows 推荐入口：

```powershell
scripts\test-backend.cmd
```

该入口会先构建 test profile 的 Migration 镜像，确保新增 Migration 不会因复用旧镜像而被遗漏。

该命令启动 Compose `test` profile 中的独立 PostgreSQL（默认端口5433）、执行 Migration，再把 `.env` 的 `TEST_DATABASE_URL` 注入 pytest。测试代码会拒绝数据库名不以 `_test` 结尾的地址。

Docker 可用时再执行：

```powershell
docker compose config
docker compose up -d --build --force-recreate
docker compose ps
docker compose logs migrate --tail 50
Invoke-WebRequest http://localhost:8000/api/v1/health/ready -UseBasicParsing
Invoke-WebRequest http://localhost:8000/api/v1/operation-metrics?page_size=1 -UseBasicParsing
```

代码或依赖变化后必须重新 build 并 recreate，不能只执行 `docker compose restart`；restart 不会把宿主机新代码复制进既有镜像。后端只有在 `migrate` 成功执行到 head 后才会启动。

Compose 会先运行一次性 `migrate` 服务执行 `alembic upgrade head`，成功后才启动后端。手动查看或执行 Migration：

```powershell
docker compose run --rm migrate alembic current
docker compose run --rm migrate alembic upgrade head
```

禁止在应用启动代码中使用 `create_all` 代替 Migration。

### Windows 首次启用 Docker

Docker Desktop 的 Linux 容器后端依赖 WSL 2。若 `wsl --status` 提示未安装，请在“以管理员身份运行”的 PowerShell 中执行：

```powershell
wsl --install --no-distribution
```

按系统提示重启 Windows，启动 Docker Desktop，等待引擎显示 Running 后再执行上面的 Compose 验证。Docker Desktop 的授权条款应由实际使用组织结合规模和用途确认。

## 开发流程

开始任何任务前阅读 `AGENTS.md`、`ARCHITECTURE.md`、`BUG_HISTORY.md` 并检查 Git 状态。每个 Task 必须定义目标、范围、数据库影响、验收和测试；测试通过后再提交。

## 当前能力与边界

当前已提供 Organization/User 公共模型、账号矩阵和运营数据中心。数据中心的标准导入列、重复策略和统计公式见 `METRICS.md` 与 `ARCHITECTURE.md`。其他业务页仍为空状态，不接入平台自动抓取、复杂权限、AI 调用或 RAG。
