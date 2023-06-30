#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : mrslouzk
@Date           : 2023/3/5
@LastEditors    : mrslouzk
@LastEditTime   : 2023/6/3
@Description    : 大建模拟器
@GitHub         : https://github.com/MRSlouzk
"""
__author__ = "mrslouzk"
__usage__ = "https://acgn-alliance.github.io/AZbot-docs/#/usage/utility/%E6%A8%A1%E6%8B%9F%E5%BB%BA%E9%80%A0"
__version__ = "0.0.2"

from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Message,
    MessageEvent,
    Bot
)
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.matcher import Matcher

from AZbot.plugins.checker.rule_check import event_handle
from AZbot.plugins.utils import send_forward_msg
from AZbot.plugins.utils import CDTime as cd
from .simulator import build_simulator

bsm = on_command("模拟建造", rule=event_handle)
@bsm.handle()
async def build_sim(bot: Bot, event: MessageEvent, matcher: Matcher, arg: Message = CommandArg()):
    if not await cd.is_cd_down(matcher, event, bot, need_reset=False):
        await bsm.finish("功能冷却中...")
    build_type = ["qx", "zx", "tx", "xd"]
    args = arg.extract_plain_text().split()
    if len(args) == 0:
        await bsm.finish("请输入建造池类型")
    elif len(args) == 1:
        if(args[0] not in build_type):
            await bsm.finish("建造池类型错误")
        num = 1
    elif len(args) == 2:
        if(args[0] not in build_type):
            await bsm.finish("建造池类型错误")
        if(not args[1].isdigit()):
            await bsm.finish("抽取次数错误")
        else:
            num = int(args[1])
            if(num > 10):
                await bsm.finish("抽取次数过多")
            elif(num < 1):
                await bsm.finish("抽取次数过少")
    else:
        await bsm.finish("参数过多")
    
    result = await build_simulator(args[0], num)
    msg_lst = []
    for data in result:
        ship_name = data["ship"]
        prob = data["probability"]
        img_url = data["img_url"]
        try:
            msg = Message(f"舰娘: {ship_name}\n稀有度: {prob}") + MessageSegment.image(img_url)
        except:
            await bsm.finish("获取舰船图标失败, 取消本次抽取")
        msg_lst.append(msg)
    await send_forward_msg(bot, event, "建造模拟器", str(bot.self_id), msg_lst)
    await cd.set_cd_time(matcher, event, bot)