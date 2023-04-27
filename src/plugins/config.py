from yaml import load, FullLoader
import os, sys
from nonebot.log import logger

if not os.path.exists("./config.yaml"):
    logger.error("未检测到配置文件, 请使用仓库的配置文件进行加载")
    sys.exit(0)
else:
    cfg: dict = load(open("./config.yaml", "r", encoding="utf-8").read(), Loader=FullLoader)

black_list = cfg["user"]["black_list"]