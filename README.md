# Agentic Trading Using OpenClaw (Alpaca Stock MVP)

本仓库用于承载比赛版改造：将 OpenClaw 量化项目从“建议系统”升级为“可执行的 Alpaca Paper 股票交易智能体”。

## 已同步的首批文件

- 配置：`config/alpaca.yaml`, `config/strategy_stock.yaml`
- Adapter：`adapters/alpaca_data_adapter.py`, `adapters/alpaca_trade_adapter.py`
- Core：`core/order_logger.py`
- 脚本：
  - `scripts/fetch_alpaca_stock_snapshot.py`
  - `scripts/build_stock_signal_report.py`
  - `scripts/risk_gate_and_position_sizing.py`
  - `scripts/execute_alpaca_orders.py`
  - `scripts/export_submission_artifacts.py`
  - `scripts/compute_eval_metrics.py`
  - `scripts/run_live_stock_pipeline.py`
- 样例状态/提交：`state/*`, `submissions/*`
- 改造清单：`ALPACA_STOCK_COMPETITION_REFACTOR_CHECKLIST.md`

## 运行

```bash
python scripts/run_live_stock_pipeline.py
```

## 环境变量

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPACA_BASE_URL`（默认 paper）

> 当前为可运行 MVP 骨架，后续将继续补齐真实持仓 delta、成交回报对账、schema 校验和完整评估口径。
