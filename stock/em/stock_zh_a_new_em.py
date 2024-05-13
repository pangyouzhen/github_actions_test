import pandas as pd
import requests


# 重写新股，主要更改点：数据增加上市日期一列，便于过滤
def stock_zh_a_new_em() -> pd.DataFrame:
    """
    东方财富网-行情中心-沪深个股-新股
    http://quote.eastmoney.com/center/gridlist.html#newshares
    :return: 新股
    :rtype: pandas.DataFrame
    """

    url = "http://43.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=40&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f26&fs=m:0+f:8,m:1+f:8&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f11,f62,f128,f136,f115,f152&_=1691211909117"

    payload={}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    }

    r = requests.request("GET", url, headers=headers, data=payload)
    print(r)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json['data']['diff'])
    temp_df.reset_index(inplace=True)
    temp_df['index'] = range(1, len(temp_df)+1)
    temp_df.columns = [
        '序号',
        '_',
        '最新价',
        '涨跌幅',
        '涨跌额',
        '成交量',
        '成交额',
        '振幅',
        '换手率',
        '市盈率-动态',
        '量比',
        '_',
        '代码',
        '_',
        '名称',
        '最高',
        '最低',
        '今开',
        '昨收',
        '_',
        '_',
        '_',
        '市净率',
        '_',
        '_',
        '上市日期',
        '_',
        '_',
        '_',
        '_',
        '_',
        '_',
        '_',
    ]
    temp_df = temp_df[[
        '序号',
        '代码',
        '名称',
        '最新价',
        '涨跌幅',
        '涨跌额',
        '成交量',
        '成交额',
        '振幅',
        '最高',
        '最低',
        '今开',
        '昨收',
        '量比',
        '换手率',
        '市盈率-动态',
        '市净率',
        '上市日期',
    ]]
    temp_df['最新价'] = pd.to_numeric(temp_df['最新价'], errors="coerce")
    temp_df['涨跌幅'] = pd.to_numeric(temp_df['涨跌幅'], errors="coerce")
    temp_df['涨跌额'] = pd.to_numeric(temp_df['涨跌额'], errors="coerce")
    temp_df['成交量'] = pd.to_numeric(temp_df['成交量'], errors="coerce")
    temp_df['成交额'] = pd.to_numeric(temp_df['成交额'], errors="coerce")
    temp_df['振幅'] = pd.to_numeric(temp_df['振幅'], errors="coerce")
    temp_df['最高'] = pd.to_numeric(temp_df['最高'], errors="coerce")
    temp_df['最低'] = pd.to_numeric(temp_df['最低'], errors="coerce")
    temp_df['今开'] = pd.to_numeric(temp_df['今开'], errors="coerce")
    temp_df['量比'] = pd.to_numeric(temp_df['量比'], errors="coerce")
    temp_df['换手率'] = pd.to_numeric(temp_df['换手率'], errors="coerce")
    temp_df["上市日期"] = pd.to_datetime(temp_df["上市日期"],format="%Y%m%d")
    return temp_df

if __name__ == "__main__":
    res = stock_zh_a_new_em()
    print(res)
#     res.to_csv("stock_zh_a_new_em.csv")