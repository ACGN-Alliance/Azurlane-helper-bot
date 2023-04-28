from src.plugins.config import cfg

from .rule_check import *
from .start_checker import *

import nonebot
from nonebot.log import logger


from nonebot import require
require("nonebot_plugin_apscheduler")
try:
    from nonebot_plugin_apscheduler import scheduler

    bili_interval = cfg["bili"]["auto_push_time"]
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

except ImportError:
    logger.error("未检测到nonebot_plugin_apscheduler, 请安装, 否则定时任务无法使用")
except Exception as e:
    logger.error(e)
        