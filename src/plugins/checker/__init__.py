from .rule_check import *
from .start_checker import *

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot
if(get_driver().config.dict().get("regular_update") is not None and not get_driver().config.dict().get("regular_update")):
    from nonebot import require
    require("nonebot_plugin_apscheduler")
    try:
        from nonebot_plugin_apscheduler import scheduler
        @scheduler.scheduled_job("interval", hour=12, minute=0)
        async def _(bot: Bot):
            from src.plugins.sync import data_sync
            await data_sync()

            cfg = get_driver().config
            for user in cfg.superusers:
                await bot.send_private_msg(user_id=user, message="Bot已启动")

    except Exception:
        logger.error("未检测到nonebot_plugin_apscheduler, 请安装")