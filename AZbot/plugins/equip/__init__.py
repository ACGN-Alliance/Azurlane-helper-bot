#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : mrslouzk
@Date           : 2023/4/27
@LastEditors    : mrslouzk, 一块蒙脱石
@LastEditTime   : 2023/5/1
@Description    : 装备渲染与发送
@GitHub         : https://github.com/MRSlouzk
"""
__author__ = "mrslouzk"
__usage__ = """
装备查询功能可以查询某个装备的详细信息
用法: /装备查询 <装备名> 或 /eqif <装备名>
用例: /装备查询 三联装610mm鱼雷T3
!!!目前不支持缩写查询!!!
"""
__version__ = "0.0.3"

import json
import os
from io import BytesIO

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    MessageSegment, Message, MessageEvent, Bot
)
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot_plugin_apscheduler import scheduler

from AZbot.plugins.checker.rule_check import event_handle
from AZbot.plugins.config import cfg
from AZbot.plugins.utils import CDTime as cd
from .render import EquipAttr, tmp_dir, data_dir

def render_img(name: str):
    equip_data = json.load(open(data_dir + name + ".json", "r", encoding="utf-8"))
    io = BytesIO()
    EquipAttr(equip_data).im.save(io, format="PNG")
    img = io.getvalue()
    return img


equip_info = on_command(cmd="装备查询", aliases={"eqif"}, rule=event_handle)


@equip_info.handle()
async def _(bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    if not await cd.is_cd_down(matcher, event, bot, need_reset=False):
        await equip_info.finish("功能冷却中...")
    args = arg.extract_plain_text().split()
    if len(args) != 1:
        await equip_info.finish(__usage__)
    else:
        all_equip: dict = json.load(open(data_dir + "all.json", "r", encoding="utf-8"))
        if not all_equip.get(args[0]):
            await equip_info.finish("未查询到该装备(注意: 目前不支持缩写查询)")  # TODO 支持缩写查询
        if cfg["func"]["equip_render_mode"] == "real_time":
            msg = MessageSegment.image(render_img(str(arg[0])))
        elif cfg["func"]["equip_render_mode"] == "cache":
            local_file_lst = os.listdir(tmp_dir)
            if args[0] + ".png" in local_file_lst:
                parent_path = os.path.abspath(os.path.join(tmp_dir, ".."))
                msg = MessageSegment.image(f"file:///{parent_path + tmp_dir + args[0]}.png")
            else:
                img = render_img(str(arg[0]))
                msg = MessageSegment.image(img)
                open(tmp_dir + args[0] + ".png", "wb").write(img)
            if "equip_clean" not in [job.id for job in scheduler.get_jobs("default")]:
                if cfg["func"]["equip_render_auto_clean"] != -1:
                    scheduler.add_job(auto_clean, trigger="interval", hours=cfg["func"]["equip_render_auto_clean"], id="equip_clean")
        else:
            msg = Message("装备渲染模式配置错误, 请联系管理员")

        await cd.set_cd_time(matcher, event, bot)
        await equip_info.finish(msg)

async def auto_clean():
    for file in os.listdir(tmp_dir):
        os.remove(tmp_dir + file)