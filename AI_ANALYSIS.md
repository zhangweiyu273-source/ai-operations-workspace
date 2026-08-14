# AI 运营分析中心 V1

## 分析类型

- `operation`：综合运营分析
- `content`：内容表现分析
- `keyword`：关键词分析
- `topic`：选题分析
- `task_review`：任务与复盘分析

## 数据边界与计算口径

`AnalysisContextBuilder` 只读取已软删除过滤后的业务数据，并先在后端聚合：曝光、播放、互动、有效线索、试听、成交、成交金额和转换率。互动率以互动/播放计算；线索率以有效线索/播放计算；试听率以试听/有效线索计算；成交率以成交/试听计算。分母为零时返回 `0`。

发送给模型的是受限的结构化上下文：汇总指标、最多 5 条高表现内容、最多 5 条低表现内容、平台汇总和资产计数；不会发送整个数据库、API Key、密码、Token 或用户联系方式。

## 输出规则

Prompt `v1` 要求输出 JSON，并区分：数据事实、分析解释、待验证假设、可执行建议与数据局限。模型格式异常会返回可诊断的 `AI_ANALYSIS_INVALID_RESPONSE` 错误，不会保存伪造结果。分析记录保存 `prompt_version`、`context_version`、Provider 和模型，便于追溯。

## Token 控制

单次请求最多 20 个账号筛选条件；内容样本均限制为前 5 条；`AIService` 的分析输出上限为 1200 tokens。`AIRequestLog` 只记录功能标识、状态、Token 与耗时，不保存 Prompt、回复正文或 API Key。
