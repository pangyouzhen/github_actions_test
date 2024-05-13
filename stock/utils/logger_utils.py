from loguru import logger

logger.add("/data/project/stock/log/runtime_{time}.log", rotation="1 week")
