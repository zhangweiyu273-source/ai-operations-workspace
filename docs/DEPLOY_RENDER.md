# Render 生产部署

## 架构

生产环境使用三个 Render 资源，位于同一 `singapore` 区域：

1. `ai-ops-workbench`：公开 Next.js Web Service，唯一对老板开放的 URL。
2. `ai-ops-api`：FastAPI Private Service，没有公网 URL，只能由前端通过 Render 私网访问。
3. `ai-ops-db`：Render PostgreSQL；后端使用其内部连接字符串。

这比仅部署到 Vercel 更适合当前项目：Vercel 可承载 Next.js，但不能作为持续运行的 FastAPI 与 PostgreSQL 的完整替代。Netlify 和 Cloudflare 同样不能直接承载此组合。Render Blueprint 可同时编排现有 Dockerfile、私有 API 与托管 PostgreSQL。

## 首次部署

1. 将当前仓库推送到一个私有 GitHub 仓库；不要提交 `.env`、备份文件或 `storage/uploads/` 的真实上传文件。
2. 登录 Render，选择 **New +** → **Blueprint**，连接 GitHub 并选择该仓库。
3. Render 会读取根目录的 `render.yaml`，确认三个资源后继续。
4. 在 Render 要求填写机密变量时，填写下表中的值；不要把这些值写回仓库。
5. 部署完成后，打开 `ai-ops-workbench` 的公开 `onrender.com` 地址，并把该地址和 `viewer` 账号密码提供给老板。

## 必填生产环境变量

| 资源 | 变量 | 说明 |
| --- | --- | --- |
| `ai-ops-api` | `CORS_ORIGINS` | 前端公开 URL，例如 `https://ai-ops-workbench.onrender.com`。后续绑定自定义域名后同步更新。 |
| `ai-ops-api` | `DEEPSEEK_API_KEY` | DeepSeek 真实密钥，仅服务器保存。未填时 AI 功能降级，其他模块仍可用。 |
| `ai-ops-workbench` | `ADMIN_ACCESS_PASSWORD` | 管理员访问密码；浏览器 Basic Auth 用户名固定为 `admin`。 |
| `ai-ops-workbench` | `VIEWER_ACCESS_PASSWORD` | 老板只读访问密码；浏览器 Basic Auth 用户名固定为 `viewer`。 |

`DATABASE_URL` 由 `render.yaml` 从 Render PostgreSQL 内部连接自动注入。不要手工复制数据库密码到代码、前端环境变量或 GitHub。

## 只读访问规则

- 使用 `viewer` / `VIEWER_ACCESS_PASSWORD` 登录时，前端显示只读提示，并隐藏写入操作入口。
- 同源 API 代理会拒绝该角色的所有非 `GET`/`HEAD` 请求，返回 `403 READ_ONLY_ACCESS`。
- 后端是 Render Private Service，不对公网开放，外部无法绕过前端代理直接调用写入 API。
- `admin` / `ADMIN_ACCESS_PASSWORD` 保留完整管理能力。

## 后续更新

推送到与 Blueprint 关联的分支会自动重新部署。每次部署中，`ai-ops-api` 会在启动前执行 `alembic upgrade head`。不要手工修改生产数据库结构或跳过 Migration。

## 数据与备份

生产数据库必须单独部署，不能使用本机 Docker Volume。首次上线前请执行本地逻辑备份，并按阶段 L 的恢复演练流程验证备份。Render PostgreSQL 的备份、保留策略与恢复能力取决于所选数据库套餐，应在购买前确认。

当前上传文件仅在导入过程中读取，不作为长期文件资产保存；未来若启用长期附件，应接入对象存储，不应依赖服务容器本地磁盘。

## 发布前安全检查

```powershell
git ls-files .env
git grep -n "DEEPSEEK_API_KEY=" -- ':!.env.example'
cd frontend; npm run lint; npm test; npm run build
cd ..\backend; pytest
```

以上命令应不显示真实 `.env`，并且所有测试与构建成功后再创建 Release Commit。
