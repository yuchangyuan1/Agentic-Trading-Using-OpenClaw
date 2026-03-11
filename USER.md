目标用户：参赛开发者（Alpaca 模拟交易赛）。

默认偏好：
- 市场：US Stock
- 频率：日频/低频（1~2 次再平衡）
- 风险偏好：中性偏稳健
- 输出语言：中文

默认输出结构：
1. 市场概览
2. 信号摘要
3. 交易动作
4. 风险提示
5. 指标快照（CR/SR/MD/DV/AV）

强制字段：
- data_ts
- quality_score/source_health
- why/risk/confidence
- change_vs_last