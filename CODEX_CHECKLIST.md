# Codex 完成检查清单

每个开发任务结束时逐项确认；不适用项须说明原因，核心项失败不得宣布完成。

- [x] 项目可以启动
- [x] 前端编译成功
- [x] 后端启动成功
- [x] 数据库连接成功
- [x] Migration 正常
- [x] 新功能正常
- [x] 原有功能正常
- [x] 数据刷新后仍然存在
- [x] 无明显前端 Console 错误
- [x] 无明显后端异常
- [x] API 请求正常
- [x] 无硬编码密码
- [x] 无硬编码 API Key
- [x] 无明显重复代码
- [x] 无无用依赖
- [x] 中文显示正常
- [x] 页面无明显布局异常
- [x] 历史 Bug 未重新出现
- [x] 自动测试通过

## 阶段 A 补充验证

- [x] `.env.example` 完整且不含真实密钥
- [x] Docker Compose 配置可解析
- [x] liveness 与 readiness 语义分离
- [x] 上传目录与源码隔离
- [x] Windows 本地配置可迁移至 Linux 容器

## 阶段 A 验收记录（2026-08-14）

- [x] 项目基础结构可以启动
- [x] 前端测试、ESLint 与生产构建成功
- [x] 后端 pytest、Ruff 与 liveness 检查成功
- [x] Docker Desktop 4.86.0 已安装
- [x] Docker Compose 配置解析成功
- [x] `.env` 已从模板创建且被 Git 忽略
- [x] Docker Linux 引擎启动成功
- [x] PostgreSQL 容器健康并通过 readiness 检查
- [x] Migration 正常（upgrade/downgrade/re-upgrade 已在独立数据库验证）

阶段 A 核心验收已于 2026-08-14 通过；Migration 在阶段 B 完成后补充验证通过。

## 阶段 C 验收记录（2026-08-14）

- [x] `20260814_0002` 已在 PostgreSQL 执行，`accounts` 表及约束/索引真实存在
- [x] 账号新增、列表、搜索、筛选、分页、详情、编辑和软删除 API 正常
- [x] 软删除后列表不可见，数据库记录保留
- [x] 账号页面从 API 读取数据，无前端写死账号数据
- [x] 前端账号页加载、新增、编辑、删除自动测试通过
- [x] 后端账号 API、模型、错误与 Migration 测试通过
- [x] 前端生产镜像 Build 成功，前后端与数据库容器健康
- [x] 历史 Bug 未复现，现有非账号模块仍保持原边界

## 阶段 D 验收记录（2026-08-14）

- [x] 运营数据持久化、账号外键、平台同步和软删除正常
- [x] 重复导入可识别，错误批次不会部分写入
- [x] 统计口径统一，所有除零结果安全返回 `0.00`
- [x] UTF-8 CSV 和 XLSX 导入测试通过，CSV 筛选导出通过
- [x] 1000 条数据分页、搜索、筛选和数据库聚合测试通过
- [x] `20260814_0003` 独立数据库往返及 Docker 生产验收通过

## 阶段 A-D P0/P1 修复验收（2026-08-14）

- [x] 独立测试数据库配置、Migration和安全护栏正常
- [x] 无 `NODE_OPTIONS` 连续前端Build成功，无残留 `.next/lock`
- [x] readiness在数据库停止时503、恢复后200
- [x] Docker重新Build/Recreate，Migration与阶段D API版本一致
- [x] 数据库异常rollback并记录安全上下文日志
- [x] 数据中心筛选Query Schema回归正常
- [ ] 创建initial stable commit（等待配置Git作者身份）
