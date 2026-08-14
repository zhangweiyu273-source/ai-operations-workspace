# AI Provider 配置

阶段 J 只提供 Provider 基础设施和连接验证，不会自动读取业务数据或执行 AI 运营功能。

## 配置 DeepSeek

在仓库根目录 `.env` 中配置：

```dotenv
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
AI_TIMEOUT=30
AI_MAX_RETRIES=2
```

`DEEPSEEK_API_KEY` 只能保留在本机/服务器环境变量中，不能提交、写入前端或粘贴到日志。修改后执行：

```powershell
docker compose up -d --build --force-recreate
```

访问 `/ai/settings`：页面只显示“已配置/未配置”，可发送固定连接测试语句。服务端测试 API 为 `POST /api/v1/ai/test`。

## 常见问题

- 未配置：`GET /api/v1/ai/status` 返回 `not_configured`；其他运营模块仍可正常使用。
- 认证失败：检查 API Key 是否有效，服务只返回安全错误码，不会返回上游原始响应。
- 限流、5xx 或网络故障：Provider 按 `AI_MAX_RETRIES` 进行有限退避重试。
- 超时：调整 `AI_TIMEOUT`，默认 30 秒；不会无限等待。

未来增加其他厂商时实现 `BaseAIProvider`，由 `AIService` 选择；业务模块不得直接调用厂商 SDK 或 HTTP 接口。
