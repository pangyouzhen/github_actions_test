import argparse
import datetime
import sys
import time
from argparse import Namespace
from pathlib import Path

import akshare as ak
import pandas as pd
from loguru import logger
from retry import retry

from stock.cls.stock_cls_alerts import stock_zh_a_roll_cls
from stock.cls.stock_cls_zt_analyse import stock_zh_a_zt_analyse_cls
from stock.em.stock_zh_a_new_em import stock_zh_a_new_em
from stock.utils.wraps_utils import func_utils

print('start------')
path = Path("./log")
logger.info(f"{path.absolute()}")
global trade_df
trade_df = pd.read_csv("./stock/tool_trade_date_hist_sina_df.csv")


# 今天的原始数据
@func_utils(
    csv_path="./data/raw_data", csv_name="raw_data")
def get_raw_data(*args, **kwargs):
    date = kwargs["date"]
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    print(stock_zh_a_spot_df[:5])
    return stock_zh_a_spot_df


@func_utils(
    csv_path="./data/cls_roll", csv_name="cls_roll")
def get_stock_zh_a_roll_cls(*args, **kwargs):
    stock_zh_a_roll_cls_df = stock_zh_a_roll_cls()
    print(stock_zh_a_roll_cls_df[:5])
    return stock_zh_a_roll_cls_df


# 今天的cls zt分析数据
@retry(Exception, tries=3, delay=2)
def zt_analyse_df(*args, **kwargs):
    date = kwargs["date"]
    date = date.replace("-", "")
    return stock_zh_a_zt_analyse_cls(date, img_path="./data/cls_zt")


# zt 数据
@func_utils(csv_path="./data/zt", csv_name="zt")
def get_zt_data(*args, **kwargs):
    date = kwargs["date"]
    date = date.replace("-", "")
    stock_em_zt_pool_df = ak.stock_zt_pool_em(date)
    stock_em_zt_pool_df = stock_em_zt_pool_df.sort_values("所属行业")
    return stock_em_zt_pool_df


# zb数据
@func_utils(csv_path="./data/zb", csv_name="zb")
def get_zb_data(*args, **kwargs):
    date = kwargs["date"]
    date = date.replace("-", "")
    stock_em_zt_pool_zbgc_df = ak.stock_zt_pool_zbgc_em(date)
    return stock_em_zt_pool_zbgc_df


# dt数据
@func_utils(csv_path="./data/dt", csv_name="dt")
def get_dt_data(*args, **kwargs):
    date = kwargs["date"]
    date = date.replace("-", "")
    stock_em_zt_pool_dtgc_df = ak.stock_zt_pool_dtgc_em(date)
    return stock_em_zt_pool_dtgc_df


# 新股
# 新股改成1个月之内上市的
@func_utils(csv_path="./data/new", csv_name="new", )
def get_new(*args, **kwargs) -> pd.DataFrame:
    date = kwargs["date"]
    stock_zh_a_new_em_df = stock_zh_a_new_em()
    stock_zh_a_new_em_df["date"] = pd.to_datetime(date)
    stock_zh_a_new_em_df["date_diff"] = (stock_zh_a_new_em_df["date"] - stock_zh_a_new_em_df["上市日期"]).dt.days
    stock_zh_a_new_em_df = stock_zh_a_new_em_df[stock_zh_a_new_em_df["date_diff"]<31]
    stock_zh_a_new_em_df.drop(columns=["上市日期","date","date_diff"],axis=1,inplace=True)
    return stock_zh_a_new_em_df


@func_utils(csv_path="./sentiment/strong", csv_name="strong")
def get_strong(*args, **kwargs) -> pd.DataFrame:
    date = kwargs["date"]
    date = date.replace("-", "")
    stock_zt_pool_strong_em = ak.stock_zt_pool_strong_em(date)
    stock_zt_pool_strong_em = stock_zt_pool_strong_em.sort_values("所属行业")
    return stock_zt_pool_strong_em


def read_data(path: str | Path) -> pd.DataFrame:
    if isinstance(path, str):
        path = Path(path)
    if path.exists():
        data = pd.read_csv(path)
    else:
        data = pd.DataFrame()
    return data


def merge_data(*args, **kwargs):
    date = kwargs["date"]
    df = pd.read_csv("sentiment/stock.csv")
    raw_data = pd.read_csv(f"data/raw_data/raw_data_{date}.csv")
    zt_data = pd.read_csv(f"data/zt/zt_{date}.csv")
    dt_data_path = Path(f"data/dt/dt_{date}.csv")
    new_data_path = Path(f"data/new/new_{date}.csv")
    if dt_data_path.exists():
        dt_data = pd.read_csv(f"data/dt/dt_{date}.csv")
    else:
        dt_data = pd.DataFrame()
    zb_data = pd.read_csv(f"data/zb/zb_{date}.csv")
    increase = raw_data[raw_data["涨跌幅"] > 0]
    decrease = raw_data[raw_data["涨跌幅"] < 0]

    if new_data_path.exists():
        new_df = pd.read_csv(f"./data/new/new_{date}.csv")
    else:
        new_df = pd.DataFrame()
        new_df["代码"]=None
    
    zt_data = zt_data[~zt_data["代码"].isin(new_df["代码"].tolist())]

    zt_num = zt_data.shape[0]

    above_three = zt_data[zt_data["连板数"] > 3].sort_values("连板数", ascending=False)
    above_three["连板数"] = above_three["连板数"].astype(str)
    above_three["val"] = above_three["名称"] + above_three["连板数"]

    three = zt_data[zt_data["连板数"] == 3]
    two = zt_data[zt_data["连板数"] == 2]
    one = zt_data[zt_data["连板数"] == 1]
    today_df = pd.DataFrame(
        [{
            "日期": date,
            "红盘": increase.shape[0],
            "绿盘": decrease.shape[0],
            "涨停": zt_num,
            "跌停": dt_data.shape[0],
            "炸板": zb_data.shape[0],
            "3连板以上个股数": above_three.shape[0],
            "3连板以上个股": ";".join(above_three["val"].tolist()),
            "3连板": three.shape[0],
            "3连板个股": ";".join(three["名称"].tolist()),
            "2连板": two.shape[0],
            "2连板个股": ";".join(two["名称"].tolist()),
            "首板": one.shape[0],
        }]
    )
    # 防止最新的重复
    df = df.loc[df["日期"] != date,:]
    final_df = pd.concat([df,today_df])
    final_df["日期"] = pd.to_datetime(final_df["日期"])
    final_df = final_df.sort_values("日期")
    final_df.to_csv("sentiment/stock.csv", index=False)


def main(*args, **kwargs):
    if kwargs['date'] in trade_df["trade_date"].tolist():
        # alerts_cls()
        # date = kwargs["date"]

        # get_stock_zh_a_roll_cls(date=kwargs["date"])
        # time.sleep(5)

        merge_data(date = kwargs["date"])
    else:
        logger.info("今天不是交易日")


FUNCTION_MAP = {
    "zt": get_zt_data,
    "dt": get_dt_data,
    "zt_analyse": zt_analyse_df,
    "zb": get_zb_data,
    "raw": get_raw_data,
    "all": main,
    "sentiment": merge_data,
    # "cls": alerts_cls,
    "new":get_new,

}


def parse_para():
    parser = argparse.ArgumentParser(description="获取市场情绪")
    parser.add_argument("--func", choices=FUNCTION_MAP.keys(), help="获取涨停数据")
    # 输入日期格式 2023-08-04
    parser.add_argument("--date", default=str(datetime.datetime.today().date()))
    args = parser.parse_args()
    print(args)
    func = FUNCTION_MAP[args.func]
    func(date=args.date)


if __name__ == "__main__":
    sys.exit(parse_para())
