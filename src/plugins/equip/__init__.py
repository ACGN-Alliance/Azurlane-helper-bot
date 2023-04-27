import json
import os
from typing import Annotated

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot, Event, MessageSegment, Message, GroupMessageEvent
)
from nonebot.params import CommandArg

from src.plugins.checker.rule_check import event_handle
from src.plugins.config import cfg

__usage__ = """
装备查询功能可以查询某个装备的详细信息
用法: /装备查询 <装备名> 或 /eqif <装备名>
用例: /装备查询 三联装610mm鱼雷T3
!!!目前不支持缩写查询!!!
"""

data_dir = "data/azurlane/equip/"
if not cfg["func"]["equip_tmp_dir"]: tmp_dir = data_dir + "tmp/"
else: tmp_dir = cfg["func"]["equip_tmp_dir"]
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)

equip_info = on_command("装备查询", aliases={"eqif"}, rule=event_handle)
@equip_info.handle()
async def _(arg: Annotated[Message, CommandArg()]):
    args = arg.extract_plain_text().split("")
    if len(args) != 1:
        await equip_info.finish(__usage__)
    else:
        all_equip: dict = json.load(open(data_dir + "all.json", "r", encoding="utf-8"))
        if not all_equip.get(args[0]):
            await equip_info.finish("未查询到该装备(注意: 目前不支持缩写查询)")  # TODO 支持缩写查询
        if cfg["func"]["equip_render_mode"] == "real_time":
            equip_data = json.load(open(data_dir + args[0] + ".json", "r", encoding="utf-8"))
            img: bytes = ...   # TODO 装备信息渲染
            msg = MessageSegment.image(img)
        elif cfg["func"]["equip_render_mode"] == "cache":
            local_file_lst = os.listdir(tmp_dir)
            if args[0] + ".png" in local_file_lst:
                parent_path = os.path.abspath(os.path.join(tmp_dir, ".."))
                msg = MessageSegment.image(f"file:///{parent_path + tmp_dir + args[0]}.png")
            else:
                equip_data = json.load(open(data_dir + args[0] + ".json", "r", encoding="utf-8"))
                img: bytes = ...
                msg = MessageSegment.image(img)
                open(tmp_dir + args[0] + ".png", "wb").write(img)
        else:
            msg = Message("装备渲染模式配置错误, 请联系管理员")

        await equip_info.finish(msg)