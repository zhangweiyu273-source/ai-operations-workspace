# Bug 历史

重要 Bug 修复后追加记录；若可能复发，必须增加自动化回归测试。

## 记录模板

- BUG编号：BUG-YYYY-NNN
- 问题表现：
- 复现方式：
- 根本原因：
- 修复方式：
- 影响范围：
- 防止再次发生规则：
- 对应测试：
- 修复日期：YYYY-MM-DD

## 当前记录

### BUG-2026-001：Windows 功能启用流程提前退出

- BUG编号：BUG-2026-001
- 问题表现：重启并安装 WSL 后，Docker Desktop 仍无法启动 Linux 引擎，WSL 提示缺少必需的虚拟化组件。
- 复现方式：在同一管理员脚本中依次启用 WSL 和 Virtual Machine Platform，并把 DISM 返回码 `3010` 按普通非零错误处理。
- 根本原因：Windows DISM 的 `3010` 表示“操作成功，需要重启”，原脚本却在收到该返回码后提前退出，因此第二个功能没有执行。
- 修复方式：单独启用 `VirtualMachinePlatform`，并将返回码 `0` 与 `3010` 都视为成功。
- 影响范围：仅影响 Windows 首次安装 Docker Desktop 的本地环境配置，不影响应用代码和数据。
- 防止再次发生规则：调用 Windows Installer/DISM 等系统安装工具时，必须按其文档识别成功但需重启的返回码，不能统一使用“非零即失败”。
- 对应测试：重启后执行 `wsl --status`、`docker desktop status` 和 `docker info`，再运行 Compose 健康检查。
- 修复日期：2026-08-14

### BUG-2026-002：Docker 子项目构建上下文未正确忽略本地产物

- BUG编号：BUG-2026-002
- 问题表现：首次前端镜像构建向 Docker 发送约 539 MB 上下文，构建明显缓慢。
- 复现方式：以 `./frontend` 为构建上下文执行 `docker compose build`，同时前端目录存在 `node_modules` 和 `.next`。
- 根本原因：Docker 只读取构建上下文根目录内的 `.dockerignore`；仓库根目录的 `.dockerignore` 不会应用到 `./frontend` 或 `./backend` 上下文。
- 修复方式：分别增加 `frontend/.dockerignore` 与 `backend/.dockerignore`。
- 影响范围：Docker 构建速度、磁盘与内存占用；不影响业务数据。
- 防止再次发生规则：新增或调整 Docker build context 时，必须验证该 context 自身存在 `.dockerignore`，并检查实际传输大小。
- 对应测试：无缓存重建验证前端上下文从约 539 MB 降至约 220 KB，后端上下文约 1.39 KB，镜像构建通过。
- 修复日期：2026-08-14

### BUG-2026-003：前端生产依赖存在高危安全漏洞

- BUG编号：BUG-2026-003
- 问题表现：`npm audit --omit=dev --audit-level=high` 报告 PostCSS 与 Sharp 共 3 个高危漏洞。
- 复现方式：在 Next.js 15.5.23 依赖锁文件下运行生产依赖审计。
- 根本原因：Next.js 15 的生产依赖链包含存在已披露漏洞的 PostCSS 与 Sharp 版本。
- 修复方式：显式升级至 Next.js 和 `eslint-config-next` 16.3.1，并迁移 ESLint flat config 与测试类型导入。
- 影响范围：前端构建和生产依赖安全；未发现已被利用的证据。
- 防止再次发生规则：依赖升级和发布验收必须运行生产依赖审计，不得用 `--force` 自动跨主版本修复后跳过回归。
- 对应测试：Vitest、ESLint、TypeScript、Next.js 生产构建全部通过；生产依赖审计为 0 漏洞；容器重建与 HTTP 健康检查通过。
- 修复日期：2026-08-14

### BUG-2026-004：移动端侧栏品牌文字发生裁切

- BUG编号：BUG-2026-004
- 问题表现：390px 视口下侧栏已缩窄为 76px，但品牌名称仍显示并被裁切。
- 复现方式：在移动端视口打开首页，观察左上角品牌区域。
- 根本原因：断点只把父级字体设为 0，子元素 `strong/small` 的显式字号覆盖了继承值。
- 修复方式：移动断点明确设置 `.brand div { display: none; }`，只保留 AI 标识。
- 影响范围：窄屏工作台导航视觉，不影响桌面端和业务数据。
- 防止再次发生规则：响应式验收必须使用实际窄屏视口，检查计算样式、水平溢出和截图，不能只依赖桌面截图。
- 对应测试：390×844 视口确认品牌详情 `display:none`、侧栏 76px、无水平溢出、浏览器控制台无 warning/error。
- 修复日期：2026-08-14

### BUG-2026-005：Migration 测试依赖当前工作目录

- BUG编号：BUG-2026-005
- 问题表现：在 `backend/` 目录执行测试通过，但从仓库根目录运行同一测试时找不到 Alembic `script_location`。
- 复现方式：在仓库根目录执行 `backend/.venv/Scripts/python -m pytest backend`。
- 根本原因：测试使用相对路径 `alembic.ini` 和 `migrations`，错误假设当前工作目录永远是 `backend/`。
- 修复方式：基于 `test_migrations.py` 的绝对位置解析后端目录，并显式设置 Alembic script location。
- 影响范围：测试入口和 CI 可移植性，不影响生产数据库。
- 防止再次发生规则：测试引用仓库文件时必须基于 `__file__` 或明确项目根目录解析，不依赖调用者当前目录。
- 对应测试：分别从仓库根目录和 `backend/` 目录运行 Migration 测试。
- 修复日期：2026-08-14

### BUG-2026-006：同源 API 代理破坏文件上传请求体

- BUG编号：BUG-2026-006
- 问题表现：CSV/XLSX 直接请求 FastAPI 可以解析，但经过 Next.js `/api/v1` 同源代理上传时返回 400。
- 复现方式：在数据中心选择标准 CSV，调用 `/api/v1/operation-metrics/import` 预览。
- 根本原因：代理使用 `request.text()` 读取所有非 GET 请求，将 multipart 和 XLSX 二进制请求体转换为字符串后再次编码，导致原始字节及 multipart 边界内容不一致。
- 修复方式：代理统一使用 `request.arrayBuffer()` 原样转发非 GET/HEAD 请求体；JSON 请求同样可安全按原始 UTF-8 字节传递。
- 影响范围：经过前端同源代理的文件上传；普通 JSON CRUD 未受影响。
- 防止再次发生规则：通用 HTTP 代理不得假设请求体是文本；文件上传必须通过浏览器同源入口完成真实端到端测试。
- 对应测试：FormData API Client 边界测试、CSV/XLSX 后端测试、Docker 重建后经 `localhost:3000/api/v1` 的 CSV 预览与确认导入闭环。
- 修复日期：2026-08-14

### BUG-2026-007：数据库集成测试缺少隔离配置

- BUG编号：BUG-2026-007（对应 ISSUE-002）
- 问题表现：未配置 `TEST_DATABASE_URL` 时集成测试跳过，临时验收可能误用开发数据库。
- 复现方式：直接从仓库根目录运行 pytest，并检查数据库测试为 skipped。
- 根本原因：Compose 只有开发数据库，环境模板和标准测试入口均未定义独立测试库。
- 修复方式：增加 Compose test profile、独立 `ai_ops_test` 数据库/卷/端口、环境模板、Windows测试入口，并拒绝非 `_test` 数据库。
- 影响范围：数据库集成测试与开发数据安全。
- 防止再次发生规则：集成测试不得复用开发或生产数据库；测试数据库名称必须显式带 `_test` 后缀。
- 对应测试：`scripts\test-backend.cmd` 实际迁移独立数据库并运行26项后端测试。
- 修复日期：2026-08-14

### BUG-2026-008：前端构建锁缺少可诊断处理

- BUG编号：BUG-2026-008（对应 ISSUE-003、ISSUE-004）
- 问题表现：并发运行 Next.js dev/build 时出现瞬时 `.next` lock 错误，容易被误判为需要特殊 `NODE_OPTIONS`。
- 复现方式：一个进程占用 `.next` 时再次执行 build。
- 根本原因：开发和构建共用 `.next`，原脚本没有前置诊断或明确的安全清理入口。
- 修复方式：增加 prebuild 锁检查和 `build:clean`；文档明确停止并发进程后再清理，项目不设置或依赖 `NODE_OPTIONS`。
- 影响范围：本地及CI前端构建稳定性。
- 防止再次发生规则：不得并发使用同一 `.next`；不得盲删活动锁；标准构建必须在空 `NODE_OPTIONS` 下验证。
- 对应测试：空 `NODE_OPTIONS` 连续两次 `npm.cmd run build` 均成功。
- 修复日期：2026-08-14

### BUG-2026-009：源码与运行容器缺少一致性流程

- BUG编号：BUG-2026-009（对应 ISSUE-006～ISSUE-010）
- 问题表现：验收报告出现宿主机已有阶段D代码，但运行API 404、Migration 0003未执行、前端仍是旧页面。
- 复现方式：修改源码后只 restart 旧容器，不重新构建镜像。
- 根本原因：生产式容器不挂载源码，restart 不会更新镜像；验收流程没有强制核对Migration和关键API。
- 修复方式：固化 `--build --force-recreate`、migrate成功门禁、容器健康、Migration head、阶段D API和真实CRUD联合验收。
- 影响范围：全部容器化运行功能，尤其阶段D数据中心。
- 防止再次发生规则：代码变化后禁止仅restart；必须重建、重建容器并检查版本/API。
- 对应测试：无缓存镜像构建、`20260814_0003`、`operation_metrics`表、数据中心CRUD/统计和前端页面联合验证。
- 修复日期：2026-08-14

### BUG-2026-010：readiness缺少真实故障恢复证据

- BUG编号：BUG-2026-010（对应 ISSUE-005）
- 问题表现：正常状态返回 connected，但未证明数据库断开时不会假报正常。
- 复现方式：停止PostgreSQL后请求 `/api/v1/health/ready`。
- 根本原因：实现已有真实查询和单元测试，但验收未覆盖实际容器故障。
- 修复方式：停止开发数据库实测返回503，恢复数据库后同一后端进程重新返回200。
- 影响范围：部署就绪判断和故障诊断。
- 防止再次发生规则：健康检查验收必须包含依赖停止与恢复，不得只测正常路径。
- 对应测试：`READINESS_WITH_DB_DOWN=503`，`READINESS_AFTER_RECOVERY=200`。
- 修复日期：2026-08-14

### BUG-2026-011：Service事务异常缺少上下文日志

- BUG编号：BUG-2026-011（对应 ISSUE-011）
- 问题表现：数据库写入失败会rollback并返回500，但日志无法定位具体业务操作和资源。
- 复现方式：让Account或OperationMetric的commit抛出异常。
- 根本原因：异常分支只有rollback和重新抛出，没有模块级logger。
- 修复方式：为创建、更新、删除、导入补充 `logger.exception`；运营数据删除也统一rollback。
- 影响范围：账号矩阵和数据中心数据库写操作排障。
- 防止再次发生规则：事务异常必须rollback并记录操作、组织和资源ID，不记录敏感正文。
- 对应测试：`test_service_logging.py` 验证rollback与ERROR日志。
- 修复日期：2026-08-14

### BUG-2026-012：数据中心Router承担筛选规范化

- BUG编号：BUG-2026-012（对应 ISSUE-012）
- 问题表现：列表、统计和导出重复调用Router内的 `filter_values` 字典函数，职责边界不明确。
- 复现方式：检查数据中心路由的筛选参数组装。
- 根本原因：初版为快速共享参数，在HTTP层保留了规范化逻辑。
- 修复方式：使用 `OperationMetricFilters` 与 `OperationMetricListQuery` Query Schema负责校验、去空格和repository参数转换。
- 影响范围：数据中心筛选API维护性，不改变接口契约。
- 防止再次发生规则：Router只负责HTTP编排；输入规范化和类型约束由Schema承担。
- 对应测试：既有搜索、平台、账号、日期、分页、统计和导出回归测试。
- 修复日期：2026-08-14
### BUG-2026-013：测试 Profile 的 Migration 容器可能使用旧镜像

- 问题表现：主服务已执行新 Migration，但 `test-migrate` 仍显示旧 revision，导致独立测试库未验证最新表结构。
- 复现方式：仅执行默认 `docker compose up -d --build` 后，再运行 test profile 的 `test-migrate`。
- 根本原因：`test-migrate` 属于 Compose profile，默认构建不包含该服务，随后 `docker compose run` 会复用旧镜像。
- 修复方式：标准 `scripts/test-backend.ps1` 在启动测试数据库后显式执行 `docker compose --profile test build test-migrate`。
- 影响范围：独立数据库 Migration 验证与 CI/本地测试可信度；不影响已运行的开发容器。
- 防止再次发生规则：包含 profile 专属镜像的验证入口必须显式构建对应服务，不能假设默认 Compose build 会覆盖它。
- 对应测试：`scripts\test-backend.cmd` 后校验 `alembic current` 为 `20260814_0004`；测试数据库 upgrade/downgrade/re-upgrade 往返。
- 修复日期：2026-08-14

### BUG-2026-014：TopicKeyword Migration 与公共时间戳模型不一致

- 问题表现：PostgreSQL 创建带关键词关联的选题时返回 500，日志显示 `topic_keywords.updated_at does not exist`。
- 复现方式：执行 `20260814_0005` 后，通过 Topic API 创建包含 `keyword_ids` 的选题。
- 根本原因：`TopicKeyword` 继承 `TimestampMixin`，ORM 写入会返回 `updated_at`，但初始关联表 Migration 漏建该字段；SQLite 单元测试未覆盖真实 PostgreSQL DDL。
- 修复方式：新增 `20260814_0006`，为 `topic_keywords` 补充非空、默认当前时间的 `updated_at` 字段。
- 影响范围：阶段 F 的 Topic-Keyword 创建、更新和关联 API；既有阶段 A-E 数据不受影响。
- 防止再次发生规则：新增模型必须在 PostgreSQL 迁移后执行真实写入验收，特别校验 Mixins 带来的全部列。
- 对应测试：`scripts\test-backend.cmd` 的独立 PostgreSQL Migration；Docker 端到端 Topic-Keyword CRUD 联调。
- 修复日期：2026-08-14

### BUG-2026-015：PowerShell 批量 API 核验路径被错误插值

- 问题表现：阶段 A-G 批量 API 核验显示多个 404，但服务、Migration 和健康检查均正常。
- 根本原因：核验脚本在双引号字符串中写作 `$p?page_size=1`，没有使用 `${p}` 包裹变量，PowerShell 将其解析为错误的变量表达式，未形成实际模块路径。
- 再次出现时间：2026-08-15（测试数据清理前的只读盘点脚本）。
- 是否属于重复问题：是，`RECURRING ISSUE`。
- 首次修复为什么未完全关闭：首次只修正了当时的核验脚本；没有把变量边界规则固化到后续一次性 PowerShell 脚本的编写模板中，导致新脚本再次使用了 `$endpoint?page_size=...`。
- 本次确认根因：PowerShell 将紧跟问号的变量名作为一个表达式解析，实际请求未带模块路径；服务端、路由和数据库均未发生变化。
- 本次修复：所有动态 URL 改为 `${endpoint}` 或 `$($endpoint)` 形式；删除请求改用 `curl.exe --write-out '%{http_code}'`，避免 PowerShell 对 204 空响应产生客户端空引用误判。
- 与首次方案的差异：除修正变量边界外，同时对无响应体的删除请求改用可验证 HTTP 状态码的客户端路径。
- 防重复规则：任何动态 API URL 均不得使用 `$variable?query`；必须使用 `${variable}?query`、`$($variable)?query` 或 URI 构造器。204 删除操作必须记录真实 HTTP 状态码后再判定结果。
- 新增回归验证：本次清理分别验证了动态列表 URL 的实际记录数，以及 13 个删除请求均返回 204；清理后再次读取默认列表。
- 状态：已关闭。
- 修复方式：改为 `".../${module}?page_size=1"` 并同时核验后端直连与 Next.js 同源代理。
- 影响范围：仅验收诊断脚本输出；未影响 FastAPI Router、Docker 镜像、数据库或前端业务调用。
- 防止再次发生规则：动态 URL 的 PowerShell 变量必须使用 `${variable}`；阶段验收必须以 OpenAPI 路由与真实 HTTP 响应交叉验证。
- 对应回归测试：五个核心模块后端直连和 `/api/v1` 同源代理 GET 均返回 200。
- 修复日期：2026-08-14

### BUG-2026-016：新增 Migration 后测试基线仍断言旧 revision

- BUG编号：BUG-2026-016
- 问题表现：数据库已正确升级到 `20260814_0008` 且任务、复盘表存在，但数据库测试仍断言 `20260814_0007`，导致回归测试错误失败。
- 复现方式：执行包含阶段 H Migration 的后端测试，而 `test_database.py` 或 `test_migrations.py` 仍使用旧 revision。
- 根本原因：新增 Alembic revision 时，Migration 状态与结构断言测试未同步维护。
- 修复方式：将 Migration 基线统一更新为 `20260814_0008`，并断言 `operation_tasks`、`operation_reviews` 表存在。
- 影响范围：仅测试验收可信度；开发数据库及已迁移数据未受影响。
- 防止再次发生规则：每增加一个 Migration，必须在同一提交中同步更新 Migration head 断言、结构断言，并执行独立 PostgreSQL upgrade 验证。
- 对应测试：`backend/tests/test_database.py`、`backend/tests/test_migrations.py` 与 `scripts/test-backend.cmd`。
- 修复日期：2026-08-14

### BUG-2026-017：任务与复盘列表固定读取前 50 条数据

- BUG编号：BUG-2026-017
- 问题表现：`/tasks` 与 `/reviews` 页面固定请求第 1 页、每页 50 条；记录超过 50 条后无法继续浏览。任务页还缺少负责人和截止日期筛选，导致阶段 H 的列表验收不完整。
- 复现方式：创建超过 50 条任务或复盘后访问对应页面；尝试按负责人或截止日期定位任务。
- 根本原因：后端列表响应未提供总页数，前端也没有页码状态和分页控件；初版接口仅实现负责人参数，未实现时间范围参数。
- 修复方式：列表响应补充 `total_pages`；Task 和 Review 页面以每页 20 条请求并支持翻页；Task API 新增 `deadline_from` / `deadline_to`，Repository 在数据库中执行截止时间范围筛选，前端补齐负责人、日期范围控件。
- 影响范围：阶段 H 任务与复盘中心的可浏览性与筛选完整性；数据库结构和既有 API 路径不受影响。
- 防止再次发生规则：所有分页列表在同一任务中必须验证超过单页上限时的翻页、总数和筛选；筛选要求必须同时在 API、数据库查询和页面交互三层验收。
- 对应测试：`backend/tests/test_operations.py`、`frontend/src/app/tasks/page.test.tsx`、`frontend/src/app/reviews/page.test.tsx`。
- 修复日期：2026-08-14
## 重复问题记录规范

重复问题或重复验收失败必须记录：BUG ID、首次/再次出现时间、表现、第一次根因与方案、首次未关闭原因、第二次确认根因与方案、长期优化、防重复规则、新增回归测试、验收方法和状态。第三次出现还必须记录时间线、方案 A/B、推荐方案、影响与风险。

### BUG-2026-018：阶段 L 发布阻塞项重复验收失败
- 首次出现时间：2026-08-15
- 再次出现时间：2026-08-15
- 问题表现：数据库恢复、Docker 持久化、DeepSeek 降级、前端最终验证在上一轮阶段 L 未关闭。
- 第一次判断根因：验收范围大、执行受到时间和受限终端环境中断。
- 第一次修复方案：实现备份/启动/状态脚本，执行部分后端测试并报告未关闭项。
- 为什么第一次没有真正解决：混淆“脚本已实现”和“真实恢复已验证”；未验证 PowerShell 对二进制归档的传输；四项没有独立证据门禁。
- 第二次确认根因：发布验收缺少逐项命令、退出码和产物证据链；备份脚本存在配置解析和二进制传输缺陷。
- 第二次修复方案：容器内 `pg_dump` 生成 + Docker 二进制复制，独立恢复库、无卷删除持久化、临时无 Key 降级、前端命令独立执行。
- 长期优化措施：发布 checklist 脚本化；任一门禁未通过禁止 Release Commit。
- 防重复规则：不得把“已实现”描述为“已验收”；二进制备份必须恢复演练；发布前必须运行前后端最终命令。
- 新增回归测试：阶段 L 关闭后补充备份文件、恢复计数、持久化、AI 降级及前端门禁。
- 验收方法：独立恢复库计数比对、stop/start 后读取测试记录、无 Key 非 AI API 读取、lint/Vitest/build 退出码。
- 状态：仍需验证

### BUG-2026-019：关键词 CSV 缺少可选状态列时导入全部失败

- 问题表现：包含“关键词”但未包含“状态”列的关键词 CSV 在预检时所有行均报 `status=None` 校验错误，无法导入。
- 复现方式：上传 `关键词、平台、城市、学段、年级、学科、搜索意图、商业意图` 等列、但不含“状态”列的 UTF-8 CSV。
- 根本原因：导入归一化函数为所有映射字段生成键；当“状态”缺失或为空时仍向 `KeywordCreate` 传入 `status=None`，覆盖了 Schema 的“启用”默认值。
- 修复方式：状态值为空时移除 `status` 键，让 `KeywordCreate` 使用默认状态“启用”。
- 影响范围：关键词 CSV/XLSX 批量导入；不影响已有关键词记录、数据库结构或 API 路径。
- 防止再次发生规则：导入适配层不得以 `None` 覆盖 Schema 的业务默认值；可选导入列需要覆盖“缺列”和“空值”场景。
- 对应测试：`test_keyword_csv_import_without_optional_status_uses_default`，验证预检、真实导入、数据库保存的默认状态。
- 修复日期：2026-08-15

### BUG-2026-020：生产访问保护的 Basic Auth realm 使用中文

- 问题表现：访问保护启用且未提供凭据时，Next.js 在构造 `WWW-Authenticate` 响应头时抛出 ByteString 编码错误，未登录用户不能获得正常的 401 认证挑战。
- 复现方式：设置 `ACCESS_PROTECTION_ENABLED=true` 和两个访问密码后，请求未附带 Authorization 头的页面。
- 根本原因：HTTP 响应头只能包含 ByteString；`WWW-Authenticate` 的 realm 使用了中文名称。
- 修复方式：将 realm 改为 ASCII 值 `ai-ops-workbench`，保留中文响应体提示。
- 影响范围：仅生产访问保护的未认证响应；业务 API、数据库及本地开发模式不受影响。
- 防止再次发生规则：HTTP header 的动态或常量值必须使用 ASCII/标准允许字符；中文提示仅放在响应体。
- 对应测试：`frontend/src/proxy.test.ts`。
- 修复日期：2026-08-20
