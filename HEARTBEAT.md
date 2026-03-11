定时任务建议（部署即开始评估）：

## 每个交易日 09:40 ET
- 拉取开盘后快照
- 生成首轮信号（仅观察/轻仓）

## 每个交易日 15:35 ET
- 运行主交易流水线
1) fetch_alpaca_stock_snapshot
2) build_stock_signal_report
3) risk_gate_and_position_sizing
4) execute_alpaca_orders
5) export_submission_artifacts
6) compute_eval_metrics

## 每日收盘后 16:10 ET
- end_of_day_rollup
- 刷新 daily_stock.csv 与 equity_curve

失败降级：
- 任一步失败时记录 logs 并保持可提交状态
- 数据源失败时不新增仓位