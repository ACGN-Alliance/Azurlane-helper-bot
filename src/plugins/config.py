# from typing import Optional
# from nonebot import get_driver
# from pydantic import BaseModel
#
# from .exception import ConfigFileParseException
#
# class Config(BaseModel):
#     start_up_notify: Optional[bool] = False
#     # regular_update: Optional[bool] = False
#     bili_sub_time: Optional[int] = 30
#     download_source: Optional[str] = "github"
#     PROXY: Optional[dict] = None
#
# config = Config.parse_obj(get_driver().config.dict())

from yaml import load, FullLoader
import os, sys
from nonebot.log import logger
if not os.path.exists("./config.yaml"):
    logger.error("未检测到配置文件, 请使用仓库的配置文件进行加载")
    sys.exit(0)
else:
    cfg: dict = load(open("./config.yaml", "r", encoding="utf-8").read(), Loader=FullLoader)