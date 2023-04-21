from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver
from nonebot.log import logger

from src.plugins.base.sync import data_sync
from src.plugins.config import cfg

import os, sys
from yaml import load, FullLoader

driver = get_driver()
@driver.on_bot_connect
async def _(bot: Bot):
    if cfg["base"]["startup_notify"]:
        for user in get_driver().config.superusers:
            await bot.send_private_msg(user_id=int(user), message="Bot已启动")

@driver.on_startup
async def init():
    # config.yaml解析

    if cfg["base"]["startup_update"]:
        await data_sync()

    for user in cfg["user"]["super_admin"]:
        get_driver().config.superusers.add(user)

    else:
        logger.info("config.yaml中\"startup_update\"选项已关闭, 将不会更新数据")