# 知识库统一搜索 V2 报告

日期：2026-08-22

## 完成内容

保留既有 `search` 参数、搜索按钮、Enter 搜索、标签筛选和分类筛选逻辑不变，将知识库统一检索范围扩展为：

1. 标题（`title`）
2. 摘要（`summary`）
3. 正文（`content`）
4. 分类（`category`）
5. 标签（`knowledge_tags.tag_name`）

实现位置：`backend/app/repositories/knowledge.py`。

标签匹配采用 `knowledge.id IN (SELECT knowledge_id ...)` 子查询，而未采用会造成重复行的直接 join；因此分页、统计、独立标签筛选和软删除过滤保持原有语义。

## 未修改范围

- 未修改数据库结构、Migration 或知识数据。
- 未修改 API 路径或参数名；仍使用 `GET /api/v1/knowledge?search=...`。
- 未修改前端搜索按钮、Enter、标签筛选、分类筛选或部署配置。
- 未部署 Railway。

## 自动测试

新增 `test_unified_knowledge_search_covers_tags_category_and_content`：

| 输入 | 仅命中来源 | 结果 |
| --- | --- | --- |
| `search=XSC` | 标签 | 通过 |
| `search=行业资料` | 分类 | 通过 |
| `search=HD` | 正文 | 通过 |

执行命令：

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_knowledge.py -q
```

结果：2 passed。

## 本地运行环境验收

为使实际运行容器包含已验证代码，仅重建本地 `backend` 服务；未重建数据库、未执行 Migration、未删除 Volume，也未部署线上环境。

| 搜索词 | 本地 API | 结果 |
| --- | ---: | --- |
| `XSC` | HTTP 200，total=1 | 命中词典标题/标签 |
| `行业资料` | HTTP 200，total=1 | 命中词典分类 |
| `HD` | HTTP 200，total=1 | 命中词典正文 |

backend 容器最终状态：healthy。

## 代码质量说明

执行相关 Ruff 检查时发现该 Repository 与既有 `test_knowledge.py` 存在 6 项历史导入/风格基线告警（如未使用导入、未排序导入、`timezone.utc` 建议）。本次未改变这些既有行，也未进行无关格式化或重构；本次新增统一检索的 API 测试已通过。

## 验收状态

本地实现与三项真实 API 验收通过，等待人工页面验收；未部署 Railway。
