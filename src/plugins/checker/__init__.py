from src.plugins.equip.render import tmp_dir

from .rule_check import *
from .start_checker import *

import nonebot, os

from nonebot.log import logger
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

auto_clean = cfg["func"]["equip_render_auto_clean"]
if(not isinstance(auto_clean, int)):
    pass
else:
    if auto_clean < 1 or auto_clean > 72:
        logger.info(f"equip_render_auto_clean参数为{auto_clean}, 正常范围为1~72, 定时清理将不会生效")
    else:
        @scheduler.scheduled_job("interval", hours=auto_clean)
        async def clean():
            if os.path.exists(tmp_dir):
                os.rmdir(tmp_dir)
                logger.info(f"[自动清理]已清理{tmp_dir}下的所有文件")
            else:
                logger.info(f"[自动清理]未找到{tmp_dir}, 无需清理")
