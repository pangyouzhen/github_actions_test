import json
from datetime import datetime,timedelta
from utils.date_utils import get_time_offset

import pandas as pd
import requests

"""
Date: 2021/5/29
Desc: 财联社今日快讯
https://www.cls.cn/searchPage?keyword=%E5%BF%AB%E8%AE%AF&type=all
"""

cls_url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=7.5.5"
get_time_offset = get_time_offset()

cls_headers = {
    "Host": "www.cls.cn",
    "Connection": "keep-alive",
    "Content-Length": "112",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.cls.cn",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

def stock_zh_a_roll_cls(td=2) -> pd.DataFrame:
    """
    财联社电报加红
    https://www.cls.cn/telegraph/
    :return: 时间,标题,简讯
    :rtype: pandas.DataFrame
    只抓取当天的，td是时区相关问题设置
    """

    url = "https://www.cls.cn/v1/roll/get_roll_list?app=CailianpressWeb&category=red&os=web&refresh_type=1&rn=100&sv=7.7.5"

    payload={}
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json;charset=utf-8',
    'Connection': 'keep-alive',
    'Referer': 'https://www.cls.cn/telegraph',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    today = datetime.today()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    # 修复时区
    tdelta = timedelta(hours=td)
    today_start = today_start - tdelta
    js = response.json()
    roll_data = js["data"]["roll_data"]
    df = pd.DataFrame(roll_data)
    df = df[["ctime","title","brief"]]
    df["ctime"] = df["ctime"].apply(datetime.fromtimestamp)
    df = df[df["ctime"] > today_start]
    df.columns = ["时间","标题","简讯"]
    # 默认东八区
    df["ctime"] = df["ctime"] + timedelta(hours=8-get_time_offset)
    # 线上跑的和线下跑的时区(东8区)不一致，得到的csv文件默认会从0到9点数据
    return df


if __name__ == "__main__":
    print(stock_zh_a_roll_cls())
