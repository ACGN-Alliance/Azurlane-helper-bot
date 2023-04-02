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
        @scheduler.scheduled_job("interval", hour=24, minute=0)
        async def _(bot: Bot):
            from src.plugins.base.sync import data_sync
            await data_sync()

            cfg = get_driver().config
            for user in cfg.superusers:
                await bot.send_private_msg(user_id=user, message="Bot已启动")

        bili_interval = get_driver().config.dict().get("bili_sub_time")
        if(bili_handle < 3 or bili_handle > 1440):
            pass
        else:
            @scheduler.scheduled_job("interval", minute=get_driver().config.dict().get("bili_sub_time"))
            async def _(bot: Bot):
                from src.plugins.bili.bili_article import bili_article_pic
                from base64 import b64encode
                res = await bili_article_pic()
                if(res is None):
                    return
                cid = res[1]
                img = f"base64://{b64encode(res[0]).decode()}"
                data = json.load(open("data/group_func.json", "r", encoding="utf-8"))
                if(data.get("bili") is not None):
                    for group in data["bili"]:
                        await bot.send_group_msg(group_id=group, message=f"碧蓝航线官方更新专栏({cid}):")
                        await bot.send_group_msg(group_id=group, message=f"[CQ:image,file={img}]]")

    except ImportError:
        logger.error("未检测到nonebot_plugin_apscheduler, 请安装")
    except Exception as e:
        logger.error(e)
    