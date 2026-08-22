# 知识库搜索升级 V1.1 发布报告

- 发布日期：2026-08-22
- Git Commit：`6a4bd9a9a1a85af33a1654c7097a0669e8046db8`
- 发布方式：GitHub `master` 推送触发 Railway 已关联服务自动部署。

## 修改文件

- `backend/app/repositories/knowledge.py`：统一检索纳入分类和标签。
- `backend/tests/test_knowledge.py`：覆盖标签、分类、正文的独立命中场景。
- `frontend/src/features/knowledge/knowledge-page.tsx`：展示命中词条与解释，并提供详情入口。
- `frontend/src/features/knowledge/knowledge-entry-parser.ts`：将 Markdown 三级标题词条解析为可展示摘要。
- `frontend/src/features/knowledge/knowledge-detail-page.tsx` 与 `frontend/src/app/knowledge/[id]/page.tsx`：新增只读详情页。
- 对应前端测试、样式、变更日志、问题记录与诊断报告。

## 部署结果

| 服务 | Railway Deployment | 状态 |
| --- | --- | --- |
| `ai-ops-api` | `08817d16-2f5c-4ded-bcd6-8c60556c84c7` | SUCCESS |
| `ai-ops-workbench` | `9e0c47fd-f8a3-467a-937e-b5bde12608ae` | SUCCESS |

部署创建时间为 2026-08-22 08:07 UTC（16:07 中国标准时间）。

## 验证结果

- 线上访问保护状态：已启用；管理员与只读访问密码均已配置。未认证请求返回 401，符合预期。
- 使用工作台服务内部既有管理员认证，仅执行 GET 请求验证：
  - `search=XSC`：HTTP 200、总数 1、返回《广州小升初XSC完整黑话词典》、正文含 XSC 解释来源。
  - `search=HD`：HTTP 200、总数 1、返回同一词典、正文含 HD 解释来源。
- 本地前端专项 Vitest：3 个文件、8 个测试全部通过，包含搜索按钮、Enter 搜索、XSC/MK/HD 词条匹配及详情页词条解释。
- 本地 ESLint 与 production build 均通过；前端详情路由 `/knowledge/[id]` 已进入生产构建。

## 数据库影响

本版本未修改数据库结构、未执行 Migration、未修改环境变量、未重新导入知识数据，也未对 Railway PostgreSQL 进行任何写操作。
