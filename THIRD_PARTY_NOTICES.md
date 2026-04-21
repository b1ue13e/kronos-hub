# Third-Party Notices

`Kronos Hub` 当前不是从零开始的单体项目，而是一个把多个上游项目接入统一 Hub 的集成仓库。因此，在公开发布、二次分发或商业使用前，请先确认第三方代码的来源、许可证和分发方式。

## 当前包含的上游目录

| 目录 | 上游项目 | 在 Hub 中的角色 | 本地许可证文件情况 |
| --- | --- | --- | --- |
| `TradingAgents-main/` | TradingAgents | 多代理研究引擎 | 检测到 `LICENSE`，内容为 Apache License 2.0 |
| `Kronos-master/` | Kronos | OHLCV 预测引擎 | 检测到 `LICENSE`，内容为 MIT License |
| `ai-hedge-fund-main/` | ai-hedge-fund | 执行 / 回测 / 应用壳 | 当前本地快照未检测到顶层 `LICENSE` 文件，但本地 `README` 与上游仓库页面都标明为 MIT；正式发布时建议补齐并再次核对 |

## 重要说明

### 1. 根仓库许可证

根仓库现在为 Hub 自身的集成层补充了 `Apache-2.0` 许可证。

这意味着：

- 根目录下新增的 Hub 代码、文档和集成层文件默认按根许可证发布
- vendored 上游目录仍保留各自原始许可证约束
- 公开分发时，不能把根许可证理解成会覆盖子目录中的第三方许可证

### 2. 直接提交上游快照需要更谨慎

当前仓库是“直接包含目录”的形式，而不是：

- Git submodule
- Git subtree
- 独立服务部署

这种方式更方便本地集成，但对公开分发提出了更高要求：

- 需要保留上游许可证文件
- 需要保留必要的版权声明
- 需要清楚说明哪些目录来自第三方

### 3. 修改上游目录时请记录来源

如果你修改了这些目录中的代码，建议在 PR 或提交说明中写清楚：

- 修改发生在哪个目录
- 是否基于某个上游版本或快照
- 是否计划回灌上游
- 是否改变了许可证相关文件

## 发布前建议检查项

公开到 GitHub 之前，建议确认：

1. 根仓库许可证与 `NOTICE` 是否已经与你的发布意图一致
2. 是否保留并显式引用各上游项目许可证
3. 是否更适合把上游目录改成 submodule / subtree
4. `.env`、日志、压缩包、临时产物是否已经被忽略
5. README 是否已经说明第三方项目来源和角色

## 建议的最小合规动作

如果你准备把这个仓库公开：

- 保留 `TradingAgents-main/LICENSE`
- 保留 `Kronos-master/LICENSE`
- 再次确认 `ai-hedge-fund-main` 的上游授权状态
- 保留根目录的 `LICENSE` 与 `NOTICE`
- 在 README 中明确说明这是一个 integration-first 的聚合仓库
