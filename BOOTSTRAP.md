启动步骤：
1. 设置环境变量：ALPACA_API_KEY / ALPACA_API_SECRET / ALPACA_BASE_URL
2. 安装依赖：pip install -r requirements.txt
3. 初始化状态文件：python scripts/end_of_day_rollup.py --init
4. 试运行：python scripts/run_live_stock_pipeline.py
5. 检查提交产物：submissions/orders.jsonl / daily_stock.csv / final_portfolio_snapshot.json
