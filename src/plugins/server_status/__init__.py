#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : mrslouzk
@Date           : 2023/5/27
@LastEditors    : mrslouzk
@LastEditTime   : 2023/5/27
@Description    : 服务器状态查询
@GitHub         : https://github.com/MRSlouzk
"""
__author__ = "mrslouzk"
__usage__ = """服务器状态监测
%服务器状态监测 开启/关闭 [服务器名]
%服务器状态监测 查询 [服务器名]
服务器名可选参数：日服、官服(B服/bilibili)、渠道服、ios(苹果)
"""
__version__ = "0.0.1"

from .if_on import *
from nonebot import logger
from nonebot_plugin_apscheduler import scheduler
import nonebot

auto_check = cfg["func"]["server_status_monitor_refresh_time"]
if(not isinstance(auto_check, int)):
    pass
else:
    if auto_check < 30 or auto_check > 6000:
        logger.info(f"server_status_monitor_refresh_time{auto_check}, 正常范围为1~1440, 定时检查将不会生效")
    else:
        @scheduler.scheduled_job("interval", seconds=auto_check)
        async def check():
            (bot,) = nonebot.get_bots().values()
            await push_msg(bot)
            logger.info(f"[自动检查]已检查服务器状态")