from yaml import load, FullLoader
from yaml.error import YAMLError
import os, sys
from nonebot.log import logger

if not os.path.exists("./config.yaml"):
    logger.error("未检测到配置文件, 请初始化config")
    sys.exit(0)
else:
    try:
        cfg: dict = load(open("./config.yaml", "r", encoding="utf-8").read(), Loader=FullLoader)
    except YAMLError:
        logger.error("config.yaml文件解析出错，请初始化config")
        sys.exit(0)

black_list = cfg["user"]["black_list"]