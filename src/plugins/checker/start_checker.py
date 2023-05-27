import os.path, sys

from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver
from nonebot.log import logger
from src.plugins.sync.operation import *

# from src.plugins.base.sync import data_sync
from src.plugins.config import cfg

driver = get_driver()
@driver.on_bot_connect
async def _(bot: Bot):
    if cfg["base"]["startup_notify"]:
        for user in get_driver().config.superusers:
            await bot.send_private_msg(user_id=int(user), message="Bot已启动")

@driver.on_startup
async def init():
    # 文件检查
    proxy = cfg["base"]["network_proxy"]
    if proxy:
        set_proxy(proxy)

    if not (cfg.get("user") or cfg.get("user").get("super_admin")):
        logger.error("未找到正确配置，请初始化config")
        sys.exit(0)
    elif len(cfg["user"]["super_admin"]) == 0:
        logger.error("未配置必须项 super_admin ，请配置完成后重新启动")
        sys.exit(0)

    if cfg["base"]["startup_update"]:
        await sync_repo()
    else:
        logger.info("config.yaml中\"startup_update\"选项已关闭, 将不会更新数据")
        if not os.path.exists("data"):
            logger.warning("data文件夹不存在，使用时会报错，请将\"startup_update\"选项打开后重新启动")
            sys.exit(0)

    for user in cfg["user"]["super_admin"]:
        get_driver().config.superusers.add(user)
