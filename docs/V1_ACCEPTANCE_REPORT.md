# AI运营工作台 V1.0 最终验收记录

阶段 A-K 已完成，阶段 L 负责冻结验收。核心范围包括账号、运营数据、关键词、选题、知识库、任务、复盘、驾驶舱、AI Provider 与只读 AI 分析。

## 部署与恢复

- 启动：`scripts/start.ps1`
- 停止：`scripts/stop.ps1`（仅停止，不删除卷）
- 状态：`scripts/status.ps1`
- 逻辑备份：`scripts/backup_database.ps1`，产物位于被 Git 忽略的 `backups/`。
- 恢复必须在独立测试数据库执行：`pg_restore -c -d <test_database> <backup_file>`；严禁对唯一开发库执行破坏性恢复。

## 已知问题

- P2：知识库页面仍有既有 ESLint Hook dependency warning；不影响构建或功能，后续在独立维护任务处理。

## 云端迁移准备

系统通过 Docker Compose、环境变量、命名卷和相对路径运行。云端需补充 TLS/反向代理、受管密钥、数据库备份保留策略、对象存储和监控告警；主体业务代码无需重写。
