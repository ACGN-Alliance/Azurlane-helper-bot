#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : mrslouzk
@Date           : 2023/6/3
@LastEditors    : mrslouzk
@LastEditTime   : 2023/6/3
@Description    : 机器人自检
@GitHub         : https://github.com/MRSlouzk
"""
__author__ = "mrslouzk"
__usage__ = ""
__version__ = "0.0.1"

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot, GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.exception import ActionFailed
import os, httpx, asyncio

from src.plugins.config import cfg
from src.plugins.utils import send_forward_msg

self_check = on_command("自检", permission=SUPERUSER)
async def _(bot: Bot, event: MessageEvent):
    (ccg, su, proxy, ) = cfg["user"]["ccg"], cfg["user"]["super_admin"][0], cfg["base"]["network_proxy"]
    if isinstance(event, GroupMessageEvent):
        await self_check.send("[自检]WARN: 为防止风控造成的影响，推荐在私聊中使用此命令")
    await self_check.send("[自检]INFO: 开始自检...")
    if ccg != -1:
        try:
            await bot.send_group_msg(group_id=ccg, message="[自检]INFO: 群消息验证完成")
            await self_check.send(f"[自检]INFO: 群消息功能正常")
        except ActionFailed as e:
            logger.error(e)
            await bot.send_private_msg(user_id=su, message=f"[自检]ERROR: 群消息无法正常发送")
    else:
        await self_check.send(f"[自检]INFO: 未配置ccg群号, 群消息验证跳过")

    await asyncio.sleep(1)

    try:
        await send_forward_msg(bot, event, "自检", bot.self_id, [Message("自检测试"), Message("自检测试")])
        await self_check.send(f"[自检]INFO: 合并转发消息功能正常")
    except ActionFailed as e:
        logger.error(e)
        await self_check.send(f"[自检]ERROR: 合并转发消息无法正常发送")

    await asyncio.sleep(1)

    if proxy:
        try:
            status = httpx.get("https://httpbin.org/get", proxies=proxy).status_code
            if status != 200:
                raise Exception(f"返回值不正确: {status}")
            await self_check.send(f"[自检]INFO: 代理功能正常")
        except Exception as e:
            logger.error(e)
            await self_check.send(f"[自检]ERROR: 代理配置错误, 请检查配置")
    else:
        await self_check.send(f"[自检]INFO: 未配置代理, 代理测试跳过")