可用外部能力：

## Alpaca Data API
- 历史/最新行情（Stock）
- 报价与分钟K线

## Alpaca Trading API
- Paper 账户信息
- 持仓读取
- 下单执行（market/limit）

## 内部脚本入口
- `python scripts/run_live_stock_pipeline.py`
- `python scripts/end_of_day_rollup.py`

约束：
- 所有下单事件必须写入 `state/live_orders.jsonl`
- 导出提交前必须通过 schema 校验
- 数据源异常时仅允许观察/减仓，不开新仓