# 获取交易日数据 原则上每年的1月1日进行更新
import akshare as ak

trade_date = ak.tool_trade_date_hist_sina()
trade_date.to_csv("tool_trade_date_hist_sina_df.csv", index=False)
