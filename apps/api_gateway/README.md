# API Gateway

统一 API 网关的薄入口在这里：

- 应用对象：`apps.api_gateway.main:app`
- 实际实现：`kronos_hub.api.app`

推荐运行方式：

```powershell
python -m uvicorn apps.api_gateway.main:app --reload --port 8010
```
