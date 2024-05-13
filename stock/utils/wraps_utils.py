import functools
from loguru import logger
from retry import retry


@retry(Exception, tries=3, delay=2)
def func_utils(csv_path, csv_name, *args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            logger.info(f"{func.__name__}的参数{csv_path=},{csv_name=}")
            result = func(*args, **kw)
            date = kw["date"]
            result["date"] = date
            result.to_csv(
                f"{csv_path}/{csv_name}_{date}.csv", index=False, encoding="utf-8"
            )
            logger.info(f"{func.__name__}_{date}存储csv数据成功")
            return result

        return wrapper

    return decorator
