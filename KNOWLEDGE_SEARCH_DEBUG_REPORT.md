# 知识库搜索诊断报告

日期：2026-08-22  
范围：仅诊断；未修改代码、数据库、知识数据、Migration 或部署。

## 结论

本地知识库对 `HD` 的搜索**实际已生效**：`GET /api/v1/knowledge?search=HD&page=1&page_size=20` 返回 HTTP 200、`total=1`，且命中《广州小升初XSC完整黑话词典》的正文内容。

页面看起来“没有变化”的直接原因是本地当前只有这一条知识：未筛选列表与 `HD` 搜索列表均返回同一条记录（均为 `total=1`）。这不是按钮未触发或 `HD` 未命中。

同时发现一项尚未实现的搜索范围缺口：现有全文搜索未包含知识标签和分类；分类仅可通过独立 `category` 筛选参数过滤，标签仅可通过独立 `tag` 筛选参数过滤。

## 前端请求链路

文件：`frontend/src/features/knowledge/knowledge-page.tsx`

- 搜索按钮是 `type="submit"`，表单 `onSubmit` 调用 `applySearch()`。
- 输入框 `onKeyDown` 在 `Enter` 时调用同一个 `applySearch()`。
- `applySearch()` 将输入值写入 `filters.search`。
- `load()` 使用 `URLSearchParams` 将该字段拼入 `GET /knowledge?...&search=HD`。
- 统一 API Client 将请求发送至 `${NEXT_PUBLIC_API_BASE_URL}/knowledge`；本地默认路径为 `/api/v1/knowledge`。

因此前端不使用 `keyword` 参数，而使用 `search` 参数。

## API 参数与后端查询逻辑

文件：

- `backend/app/schemas/knowledge.py`
- `backend/app/api/routes/knowledge.py`
- `backend/app/repositories/knowledge.py`

`KnowledgeQuery` 声明的全文检索参数为 `search: str | None`。后端没有 `keyword` 参数。

Repository 在 `search` 有值时的 SQLAlchemy 条件等价于：

```text
title CONTAINS :search
OR content CONTAINS :search
OR summary CONTAINS :search
```

并始终附加组织范围和 `is_deleted = false` 条件。

标签筛选是独立的 `tag` 参数，通过 `knowledge_tags.tag_name` 子查询执行；分类筛选是独立的 `category` 精确匹配。

## 只读实际请求证据

| 请求 | HTTP | total | 说明 |
| --- | ---: | ---: | --- |
| `search=HD` | 200 | 1 | 正确命中词典正文中的 HD 解释。 |
| 未带搜索条件 | 200 | 1 | 本地当前唯一知识也是该词典，因此视觉上相同。 |
| `search=NOT_A_REAL_KNOWLEDGE_TERM` | 200 | 0 | 证明 `search` 参数会实际过滤数据库结果。 |
| `keyword=HD` | 200 | 1 | `keyword` 不是已定义参数，被后端忽略；结果退回未筛选列表。 |
| `search=行业资料` | 200 | 0 | 证明当前全文搜索不覆盖 `category` 字段。 |

## 实际失败位置

本次输入 `HD` 的场景不存在请求或 SQL 执行失败。失败感知发生在页面呈现层：结果数量与未筛选数量相同，页面没有显示“当前搜索词”或“已筛选 X 条”的上下文，用户难以区分“搜索命中全部记录”和“搜索没有执行”。

## 最小修复方案（未执行）

1. 后端：在 `KnowledgeRepository.filters()` 的 `search` 条件中增加：
   - `Knowledge.category.contains(search, autoescape=True)`；
   - 关联 `KnowledgeTag.tag_name` 的 `EXISTS` 或子查询条件。
2. 前端：搜索成功后在列表上方显示“搜索：HD，结果：1 条”；无搜索词时显示“全部 1 条”。
3. 测试：
   - 新建两条差异化知识，验证 `HD` 只返回正文含 HD 的记录；
   - 验证标题、正文、摘要、分类和标签五个范围；
   - 验证 `keyword` 不再被 UI 使用，且前端只发送 `search`。

以上为建议，当前未做任何修改。
