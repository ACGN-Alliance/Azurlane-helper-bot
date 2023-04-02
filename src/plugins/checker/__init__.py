from .rule_check import *
from .start_checker import *

import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot

from src.plugins.config import config

# async def start_ala(bot: Bot):
#     from src.plugins.base.sync import data_sync
#     await data_sync()

#     for user in get_driver().config.superusers:
#         await bot.send_private_msg(user_id=user, message="Bot已启动")

# async def bili_notice(bot: Bot):
#     from src.plugins.bili.bili_article import bili_article_pic
#     from base64 import b64encode
#     res = await bili_article_pic()
#     if(res is None):
#         return
#     cid = res[1]
#     img = f"base64://{b64encode(res[0]).decode()}"
#     data = json.load(open("data/group_func.json", "r", encoding="utf-8").read())
#     if(data.get("bili") is not None):
#         for group in data["bili"]:
#             await bot.send_group_msg(group_id=group, message=f"碧蓝航线官方更新专栏({cid}):")
#             await bot.send_group_msg(group_id=group, message=f"[CQ:image,file={img}]]")

from nonebot import require
require("nonebot_plugin_apscheduler")
try:
    from nonebot_plugin_apscheduler import scheduler
    
    # if(config.regular_update):
    #     import json
    #     cfg = json.load(open("data/config.json", "r", encoding="utf-8").read())
    #     if(cfg.get("regular_update") is None or cfg.get("regular_update")): #TODO 优化此处代码，config.json默认为True
    #         scheduler.add_job(start_ala, "interval", hour=24, minute=0)

    bili_interval = config.bili_sub_time
    if(not isinstance(bili_interval, int)):
        pass
    else:
        if(bili_interval < 3 or bili_interval > 1440):
            logger.info(f"bili_sub_time参数为{bili_interval}, 正常范围为3~1440, 定时推送将不会生效")
        else:
            @scheduler.scheduled_job("interval", minutes=bili_interval)
            async def bili_notice():
                from src.plugins.bili.bili_article import bili_article_pic
                from base64 import b64encode
                res = await bili_article_pic()
                if(res is None):
                    return
                cid = res[1]
                img = f"base64://{b64encode(res[0]).decode()}"
                data = json.load(open("data/group_func.json", "r", encoding="utf-8"))
                if(data.get("bili") is not None):
                    (bot, ) = nonebot.get_bots().values()
                    for group in data["bili"]:
                        await bot.send_group_msg(group_id=group, message=f"碧蓝航线官方更新专栏({cid}):")
                        await bot.send_group_msg(group_id=group, message=f"[CQ:image,file={img}]]")
            # scheduler.add_job(bili_notice, "interval", minute=bili_interval)

except ImportError:
    logger.error("未检测到nonebot_plugin_apscheduler, 请安装, 否则定时任务无法使用")
except Exception as e:
    logger.error(e)
        