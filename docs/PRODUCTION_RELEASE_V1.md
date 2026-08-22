# AI运营工作台 V1 生产上线问题记录

最后更新：2026-08-22  
适用环境：Railway `production` / 项目 `peaceful-achievement`

本文记录 V1 上线过程中的问题、根因、处置与验证证据。敏感信息（数据库 URL、密码、API Key、访问保护密码）不写入本文档。

## 已解决

### 1. 本机无法访问 Railway PostgreSQL 公网 TCP Proxy

- **现象**：Windows 本机可以解析 Railway 数据库公网域名，但 TCP Proxy 端口无法建立连接；不能安全执行远程数据库核验或迁移。
- **根因**：本机到 Railway PostgreSQL 公网端口的 TCP 网络路径不可达，非应用、Migration 或数据库密码问题。
- **处理**：停止重复公网连接尝试，改用 Railway CLI SSH Tunnel，在 Tunnel 上完成只读 preflight、备份、迁移与验收。
- **验证**：Tunnel 只读连接成功；Railway `alembic_version`、表结构、行数和组织数据均可读取。
- **防复发**：公网数据库端口失败时先确认 DNS/TCP，再切换官方 Tunnel；禁止反复替换 URL、密码或业务代码。

### 2. 第一次数据恢复未确认提交

- **现象**：首次 native `pg_restore` 后，Railway 业务表仍为空，不能把命令无报错视为迁移成功。
- **根因**：此前迁移流程没有持久化足够的 stdout、stderr、退出码和事务完成证据；Tunnel 中断后无法证明事务是否提交。
- **处理**：建立 Migration V2：固定已验证 dump、SHA256、受控表选择列表、`--single-transaction --exit-on-error`、开始/结束时间、stdout、stderr、退出码与后续只读验收。
- **验证**：第二次正式恢复退出码为 0；本地与 Railway 的行数、主键集合、核心内容指纹一致，24 个外键孤儿检查均为 0。详见根目录 `MIGRATION_V2_EXECUTION_REPORT.md` 与 `migration_logs/`。
- **防复发**：禁止无审计日志的恢复；恢复成功必须同时满足退出码、错误日志、行数、主键、内容指纹和 FK 验收。

### 3. Railway HTTP Basic Auth 变量在运行时不可见

- **现象**：Railway 显示访问保护变量存在，但线上页面曾返回“访问保护尚未完成服务器配置”。
- **根因**：需要区分 Next.js Proxy 和 Node Route Handler 两个运行边界；仅凭变量列表不能证明密码已注入实际进程。
- **处理**：服务端改为动态读取 `process.env["..."]`，并增加不泄露 Secret 的 `/api/access-status` 诊断端点；在 Railway 的 Workbench 服务中重建两项密码变量。
- **验证**：`/api/access-status` 返回 `enabled=true`、`adminConfigured=true`、`viewerConfigured=true`；无凭据页面返回预期 401。
- **防复发**：每次生产发布同时验收根路径 401 与安全布尔诊断端点；禁止输出 Secret 或长度。

### 4. HTTP Basic Auth 响应头使用中文导致认证挑战失败

- **现象**：未认证请求无法获得正确的浏览器认证挑战。
- **根因**：HTTP `WWW-Authenticate` response header 仅支持合法 ByteString；中文 realm 不合法。
- **处理**：realm 使用 ASCII 值 `ai-ops-workbench`，中文保留在响应体。
- **验证**：前端代理测试覆盖未认证 401 响应；线上入口可触发浏览器 Basic Auth。
- **防复发**：HTTP Header 内容使用 ASCII/标准允许字符。

## 当前未关闭问题

### 5. Workbench 到 API 的上游 URL 缺少 `/api/v1` 前缀

- **优先级**：P1。
- **现象**：线上首页显示“首页数据加载失败，请稍后重试。”
- **当前证据**：Workbench 收到 `GET /api/v1/dashboard`，但向 API 实际转发 `GET /dashboard`；API 正确返回 404。Workbench 容器内直接请求 `/api/v1/health/ready` 与 `/api/v1/dashboard` 均为 200。
- **根因**：`BACKEND_INTERNAL_URL` 已存在，但值为裸 `http://ai-ops-api:8000`，没有 API 前缀。前端 Route Handler 会把资源路径直接拼接到该值之后。
- **待执行最小修复**：在 Railway `production → ai-ops-workbench → Variables` 中编辑现有变量为：

  ```text
  BACKEND_INTERNAL_URL=http://${{ai-ops-api.RAILWAY_PRIVATE_DOMAIN}}:${{ai-ops-api.PORT}}/api/v1
  ```

- **不得修改**：`NEXT_PUBLIC_API_BASE_URL`、`DATABASE_URL`、数据库数据、Migration、访问保护密码或业务代码。
- **关闭验收**：Workbench `/api/v1/dashboard` 为 200；API 日志收到 `/api/v1/dashboard` 并为 200；首页可读取数据；账号、数据中心与关键词核心读取接口无 404/502。
- **证据文件**：根目录 `ONLINE_DASHBOARD_SECOND_DIAGNOSTIC.md`。

## 发布安全基线

- 数据库导入、恢复或 Schema 变更必须经过单独授权；禁止以修复页面问题为由重新迁移数据库。
- Railway 服务间通信应使用私网域名的引用变量；不要通过公网域名、数据库 URL 或 `NEXT_PUBLIC_*` 变量连接后端。
- 变量保存会触发相应服务的新部署；变更前仅应包含必要变量，部署后必须检查 HTTP 日志与 API 日志。
- `.env`、数据库备份、恢复日志与本地 `railway.exe` 不得提交 Git。
- V1 正式 Release Commit 和 `v1.0.0` Tag 只能在 P0/P1 为 0、已认证页面验收完成后创建。

## 关联文档

- `MIGRATION_V2_EXECUTION_REPORT.md`：数据库迁移完整审计与一致性验证。
- `POST_MIGRATION_MANUAL_CHECKLIST.md`：已认证页面人工验收步骤。
- `ONLINE_API_PROXY_FIX_PLAN.md`：首次代理问题的配置方案。
- `ONLINE_DASHBOARD_SECOND_DIAGNOSTIC.md`：当前 P1 的容器内取证和关闭条件。
- `BUG_HISTORY.md`：项目长期 Bug 与重复问题规则。
