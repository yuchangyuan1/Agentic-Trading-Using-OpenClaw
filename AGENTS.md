## MarketScanner
负责：
- 通过 Alpaca Market Data 拉取美股行情（分钟/日线）
- 整理新闻与公告信号输入
- 输出并维护数据质量字段（freshness/source_health/quality_score）
输出：
- `data/market_snapshot.alpaca.stock.json`

## SignalAnalyst
负责：
- 计算低频多因子评分（趋势/动量/波动/回撤/流动性）
- 输出候选信号与风险评分
输出：
- `data/signal_report.stock.generated.json`

## ExecutionAdvisor
负责：
- 结合持仓与信号生成目标仓位与交易意图
- 执行风险闸门、回撤保护、仓位约束
输出：
- `outputs/trade_intents.json`

## BrokerExecutor
负责：
- 连接 Alpaca Paper 账户执行订单
- 记录订单事件并维护对账状态
输出：
- `state/live_orders.jsonl`
- `state/live_positions.json`

## Notifier
负责：
- 生成比赛提交产物与评估指标
输出：
- `submissions/orders.jsonl`
- `submissions/daily_stock.csv`
- `submissions/final_portfolio_snapshot.json`
- `outputs/eval_metrics.json`