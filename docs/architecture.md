# Architecture

## 设计目标

`Kronos Hub` 的目标不是把三个项目直接糊成一个 Python 包，而是构建一个可持续演进的总平台：

- 保留上游项目原有的产品形态和运行边界
- 在上层建立统一 API、统一引擎抽象和统一请求契约
- 让 `Kronos`、`TradingAgents`、`ai-hedge-fund` 既能独立运行，也能被统一调度

这种方式比“源码硬合并”更容易上线、维护和逐步重构。

## 三个子项目的职责

### `Kronos-master`

- 角色：预测引擎
- 核心能力：OHLCV 时间序列预测、批量预测、模型加载
- 在 Hub 中的定位：统一预测服务

### `TradingAgents-main`

- 角色：研究与决策引擎
- 核心能力：多代理分析、研究辩论、交易结论生成
- 在 Hub 中的定位：统一研究引擎

### `ai-hedge-fund-main`

- 角色：执行 / 回测 / 应用外壳
- 核心能力：组合分析、回测、后端和前端壳
- 在 Hub 中的定位：执行与展示壳

## 分层结构

### `apps/api_gateway`

对外暴露的 FastAPI 启动入口，当前入口非常薄：

- `apps.api_gateway.main:app`
- 实际应用对象由 `kronos_hub.api.app.create_app()` 创建

### `kronos_hub.api`

API 网关层，负责：

- 路由注册
- 请求模型定义
- 异常转译
- 把 HTTP 请求下沉到领域层或服务层

当前已暴露：

- 健康检查
- 引擎列表
- 子项目发现状态
- 统一运行入口
- 预测 / 研究 / 执行 / 回测专用路由

### `kronos_hub.engines`

引擎抽象层，负责：

- 统一适配器接口 `BaseEngineAdapter`
- 注册具体引擎
- 对 `kronos`、`tradingagents`、`ai_hedge_fund`、`hybrid` 做统一发现和调度

这是 Hub 对“能力”的抽象层，而不是对“目录”的抽象层。

### `kronos_hub.services`

服务层的职责是把 Hub 请求翻译成 worker 能理解的 payload。

它本身尽量保持轻量，不处理复杂业务逻辑：

- `KronosPredictionService`
- `TradingResearchService`
- `AiHedgeFundService`

### `kronos_hub.workers`

worker 层是整个 Hub 的关键桥接点。它们通过独立 Python 进程直接进入上游子项目代码：

- `kronos_worker.py`
- `tradingagents_worker.py`
- `ai_hedge_fund_worker.py`

worker 负责：

- 接收 JSON payload
- 引导 `sys.path`
- 加载子项目环境变量
- 调用真实函数 / 类
- 捕获 stdout / stderr
- 把结果重新标准化为 JSON

### `kronos_hub.shared`

放的是所有层都会依赖的公共能力：

- `contracts.py`: 枚举和状态契约
- `models.py`: 统一领域模型
- `project_paths.py`: 子项目路径发现
- `worker_client.py`: `subprocess` worker 调度封装

## 为什么使用独立 worker 进程

这是工程取舍，不是形式主义：

- `TradingAgents` 与 `ai-hedge-fund` 的 LangGraph 依赖不一致
- `Kronos` 的模型依赖更偏 PyTorch / Hugging Face
- 不同子项目对环境变量、入口函数、导入路径的假设并不相同

如果硬塞进一个进程，短期可能“能跑”，但中长期会带来更高维护成本：

- 解释器冲突更难排查
- 依赖升级互相影响
- 子项目升级时更容易把整个 Hub 拖坏

因此当前方案是：

- 上层统一协议
- 下层保留隔离
- 由 Hub 负责编排和结果标准化

## 真实调用链

### Kronos 调用链

`HTTP -> Router -> KronosPredictionService -> run_json_worker -> kronos_worker.py -> Kronos-master/model/*`

当前 worker 会：

- 把原始 OHLCV 记录构造成 DataFrame
- 推断或验证未来时间戳
- 加载 `KronosTokenizer` 和 `Kronos`
- 执行 `predict` 或 `predict_batch`
- 把预测结果序列化成统一 JSON

### TradingAgents 调用链

`HTTP -> Router -> TradingResearchService -> run_json_worker -> tradingagents_worker.py -> TradingAgentsGraph.propagate(...)`

当前 worker 会：

- 加载 `TradingAgents` 默认配置
- 合并 API 请求里的配置覆盖项
- 根据供应商与模型设置注入环境变量
- 调用真实图执行流程
- 返回决策结果与主要报告字段

### AI Hedge Fund 调用链

`HTTP -> Router -> AiHedgeFundService -> run_json_worker -> ai_hedge_fund_worker.py -> run_hedge_fund / BacktestEngine`

当前 worker 会：

- 构造组合与初始持仓
- 屏蔽进度条输出，避免污染 JSON
- 支持分析模式和回测模式
- 输出结果、绩效指标与组合价值轨迹

## 请求生命周期

下面是一次典型请求的生命周期：

1. 客户端调用 `/predictions/*`、`/research/*`、`/execution/*` 或 `/runs`。
2. Pydantic 请求模型完成参数校验。
3. API 层调用对应 service 或 adapter。
4. service 把参数整理为 worker payload。
5. `run_json_worker(...)` 用指定解释器启动 worker。
6. worker 进入子项目并执行真实逻辑。
7. worker 结果转为 JSON。
8. Hub 再把结果封装成统一响应体返回给客户端。

## 路径与解释器发现

当前支持通过环境变量覆盖默认路径和解释器：

### 路径

- `KRONOS_HUB_AI_HEDGE_FUND_PATH`
- `KRONOS_HUB_TRADINGAGENTS_PATH`
- `KRONOS_HUB_KRONOS_PATH`

### 解释器

- `KRONOS_HUB_AI_HEDGE_FUND_PYTHON`
- `KRONOS_HUB_TRADINGAGENTS_PYTHON`
- `KRONOS_HUB_KRONOS_PYTHON`

如果不配置路径，Hub 默认会在仓库根目录查找对应子项目目录。

## `hybrid` 模式的设计意图

`hybrid` 目前还是“定义了编排边界，但未完成真实串联”的阶段。它计划把三者组织成一条完整流水线：

1. `Kronos` 生成预测结果
2. 预测结果转为共享信号或特征
3. `TradingAgents` 把信号纳入研究与辩论过程
4. 研究结论进入 `ai-hedge-fund` 的执行或回测壳
5. Hub 统一返回结果并为未来 UI 做准备

## 当前最重要的技术边界

- Hub 现在已经能真实调度三个引擎，但还没有统一结果持久化层
- `hybrid` 的跨引擎 schema 还没有最终定型
- 前端尚未真正收敛为统一产品入口
- 仓库仍保留了上游项目快照形态，未来可能改为 submodule 或独立服务部署
