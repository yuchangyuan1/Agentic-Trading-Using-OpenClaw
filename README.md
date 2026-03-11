# Agentic Trading Using OpenClaw (Alpaca Stock MVP)

本仓库用于承载比赛版改造：将 OpenClaw 量化项目从“建议系统”升级为“可执行的 Alpaca Paper 股票交易智能体”。

## 参赛 OpenClaw Agent 配置文件（已补齐）

- `IDENTITY.md`
- `SOUL.md`
- `AGENTS.md`
- `USER.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `MEMORY.md`
- `BOOTSTRAP.md`

## 主要代码结构

- 配置：`config/alpaca.yaml`, `config/strategy_stock.yaml`
- Adapter：`adapters/alpaca_data_adapter.py`, `adapters/alpaca_trade_adapter.py`, `adapters/news_adapter.py`
- Core：`core/order_logger.py`, `core/portfolio_state.py`, `core/decision_engine.py`
- 提交 schema：`schemas/*.schema.json`
- 脚本：
  - `scripts/fetch_alpaca_stock_snapshot.py`
  - `scripts/build_stock_signal_report.py`
  - `scripts/risk_gate_and_position_sizing.py`
  - `scripts/execute_alpaca_orders.py`（按目标仓位-当前持仓做 delta 下单）
  - `scripts/export_submission_artifacts.py`（含 schema 校验）
  - `scripts/compute_eval_metrics.py`
  - `scripts/end_of_day_rollup.py`
  - `scripts/run_live_stock_pipeline.py`
- 状态/产物：`state/*`, `submissions/*`, `outputs/*`
- 改造清单：`ALPACA_STOCK_COMPETITION_REFACTOR_CHECKLIST.md`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPACA_BASE_URL`（默认 `https://paper-api.alpaca.markets`）

## 运行

```bash
python scripts/end_of_day_rollup.py --init
python scripts/run_live_stock_pipeline.py
python scripts/end_of_day_rollup.py
```

## 比赛提交文件

- `submissions/orders.jsonl`
- `submissions/daily_stock.csv`
- `submissions/final_portfolio_snapshot.json`

> 当前版本已具备“可执行 + 可留痕 + 可导出提交”的参赛骨架，可继续迭代策略与风控参数。