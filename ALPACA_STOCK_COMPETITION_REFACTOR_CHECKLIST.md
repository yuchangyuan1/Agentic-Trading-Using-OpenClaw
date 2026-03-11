# OpenClaw 股票赛道（Alpaca）改造清单（可执行）

> 目标：将 `openclaw-based-quant-trading-agent` 从“低频建议系统”改造为“可执行的 Alpaca Paper 股票交易智能体”，并满足比赛提交要求。

## 0. 范围与目标
- 市场：仅美股（Stock）
- 账户：Alpaca Paper（初始资金 100,000 USD）
- 评估期：4/20–5/1
- 提交产物：
  - `submissions/orders.jsonl`
  - `submissions/daily_stock.csv`
  - `submissions/final_portfolio_snapshot.json`

---

## 1. 项目结构改造
新增目录/文件：

```text
config/
  alpaca.yaml
  strategy_stock.yaml
adapters/
  alpaca_data_adapter.py
  alpaca_trade_adapter.py
  news_adapter.py
core/
  decision_engine.py
  portfolio_state.py
  order_logger.py
scripts/
  run_live_stock_pipeline.py
  fetch_alpaca_stock_snapshot.py
  build_stock_signal_report.py
  risk_gate_and_position_sizing.py
  execute_alpaca_orders.py
  export_submission_artifacts.py
  compute_eval_metrics.py
  end_of_day_rollup.py
schemas/
  order_event.schema.json
  daily_stock.schema.json
  final_snapshot.schema.json
state/
  live_positions.json
  live_orders.jsonl
  equity_curve.csv
submissions/
logs/
tests/
```

---

## 2. 配置层改造
### `config/alpaca.yaml`
必填：
- `market_type: stock`
- `timezone: America/New_York`
- `base_url: https://paper-api.alpaca.markets`
- `data_feed: iex`（按权限可切 sip）
- `symbols`（10–20 只高流动性股票）

### `config/strategy_stock.yaml`
必填：
- 信号参数：`ret_1d/5d/20d`, `volatility_20d`, `volume_ratio_5d`
- 仓位限制：`max_pos_pct`, `max_gross_exposure`, `max_daily_turnover`
- 风控：`max_drawdown_day`, `max_drawdown_total`
- 执行：`order_type`, `time_in_force`, `rebalance_times`

---

## 3. 数据接入（Alpaca）
### `adapters/alpaca_data_adapter.py`
- `get_bars(symbols, timeframe, start, end)`
- `get_latest_quotes(symbols)`
- `build_market_snapshot(...)`

输出为统一的 `market_snapshot` 结构，包含：
- `data_ts`, `market`, `symbols`
- 各标的 OHLCV 与派生因子输入
- `quality_score`, `source_health`, `freshness`

---

## 4. 信号与决策
### `scripts/build_stock_signal_report.py`
- 从 `market_snapshot` 计算多因子分数
- 输出：`data/signal_report.stock.generated.json`
- 每个 symbol 必含：
  - `signal`, `score`, `confidence`, `risk_level`, `reasons`

### `core/decision_engine.py`
- 将 `signal` 转为目标仓位与动作：`buy/sell/hold`
- 保留理由、风险、置信度以支持可解释性

---

## 5. 风控与仓位
### `scripts/risk_gate_and_position_sizing.py`
规则（首版硬约束）：
1. 单票权重上限（建议 10%）
2. 总仓位上限（建议 90%）
3. 当日回撤超过阈值只允许减仓
4. 数据质量 < 60 禁止开新仓
5. 流动性不足标的不交易

输出：`outputs/trade_intents.json`

---

## 6. 交易执行（Alpaca Paper）
### `adapters/alpaca_trade_adapter.py`
- `get_account()`, `get_positions()`, `list_orders()`
- `submit_order(...)`, `cancel_open_orders()`

### `scripts/execute_alpaca_orders.py`
- 读取 `trade_intents`
- 计算持仓 delta 并下单
- 落盘 `state/live_orders.jsonl`（严格时间序）

### `core/order_logger.py`
每条订单日志字段：
- `ts`, `symbol`, `side`, `qty`, `order_type`, `status`, `filled_avg_price`, `reason`, `signal_score`

---

## 7. 比赛提交工件
### `scripts/export_submission_artifacts.py`
每天/每轮后生成：
1. `submissions/orders.jsonl`
2. `submissions/daily_stock.csv`
3. 评估结束生成 `submissions/final_portfolio_snapshot.json`

并基于 schema 做格式校验。

---

## 8. 指标计算
### `scripts/compute_eval_metrics.py`
从 `state/equity_curve.csv` 计算：
- CR（累计收益）
- SR（夏普）
- MD（最大回撤）
- DV（日波动）
- AV（年化波动）

输出：`outputs/eval_metrics.json`

---

## 9. 一键主流程
### `scripts/run_live_stock_pipeline.py`
顺序：
1. 拉取快照
2. 生成信号
3. 风控与仓位
4. 下单执行
5. 更新账户/持仓状态
6. 导出提交产物
7. 计算评估指标

---

## 10. 环境与依赖
环境变量：
- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPACA_BASE_URL`

依赖：
- `alpaca-py`, `pandas`, `numpy`, `PyYAML`, `jsonschema`

---

## 11. 验收标准（最低）
- [ ] 能连接 Alpaca Paper 并读取账户
- [ ] 能跑通一轮完整 pipeline
- [ ] 能生成三类提交文件
- [ ] `orders.jsonl` 时间严格递增
- [ ] 指标脚本输出 CR/SR/MD/DV/AV
- [ ] 数据异常时不进行开新仓

---

## 12. 推荐实施节奏（2周）
- D1-D2：Adapter 接入与配置
- D3-D4：信号到交易意图
- D5-D6：风控与执行落盘
- D7：提交工件导出 + schema
- D8-D9：指标脚本 + 回放校验
- D10-D14：Paper 稳定性跑测与参数收敛
