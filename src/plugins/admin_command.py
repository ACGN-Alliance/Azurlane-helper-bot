from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, Bot, Message

from src.plugins.checker.start_checker import init
from src.plugins.func_helper import *
from src.plugins.utils import send_forward_msg

import json

# 数据操作部分 #
update_data = on_command("更新数据", permission=SUPERUSER)
@update_data.handle()
async def _(matcher: Matcher):
    await update_data.send("正在更新数据...")
    await matcher.append_handler(init)
    await matcher.append_handler(await update_data.finish("更新完成"))

# 黑名单管理 #
async def clear_blacklist() -> Message:
    group_data = json.load(open("data/azurlane/group.json", "r", encoding="utf-8"))
    user_data = json.load(open("data/azurlane/user.json", "r", encoding="utf-8"))
    for k in group_data.keys():
        group_data[k] = []
    for k in user_data.keys():
        user_data[k] = []

    return Message("清空完成")

async def add_blacklist(type: str, id: str, func: str = None) -> Message:
    if(not id.isdigit()): return Message("号码必须为数字")
    if(type == "群"): data = json.load(open("data/azurlane/group.json", "r", encoding="utf-8"))
    elif(type == "人"): data = json.load(open("data/azurlane/user.json", "r", encoding="utf-8"))
    else: return Message("参数错误")

    if(not func):
        for k in data.keys():
            data[k].append(int(id))
    else:
        if(func in data.keys()):
            data[func].append(int(id))
        else:
            data[func] = [int(id)]
    json.dump(data, open("data/azurlane/group.json" if(type == "群") else "data/azurlane/user.json", "w", encoding="utf-8"))    
    return Message("添加完成")

async def del_blacklist(type: str, id: str, func: str = None) -> Message:
    if(not id.isdigit()): return Message("号码必须为数字")
    if(type == "群"): data = json.load(open("data/azurlane/group.json", "r", encoding="utf-8"))
    elif(type == "人"): data = json.load(open("data/azurlane/user.json", "r", encoding="utf-8"))
    else: return Message("参数错误")

    if(not func):
        for k in data.keys():
            if(int(id) in data[k]):
                data[k].remove(int(id))
    else:
        if(func in data.keys()):
            if(int(id) in data[func]):
                data[func].remove(int(id))
        else:
            return Message("不存在参数名")
    json.dump(data, open("data/azurlane/group.json" if(type == "群") else "data/azurlane/user.json", "w", encoding="utf-8"))    
    return Message("删除完成")

async def check_blacklist(type: str, id: str, func: str = None) -> Message:
    if(not id.isdigit()): return Message("号码必须为数字")
    if(type == "群"): data = json.load(open("data/azurlane/group.json", "r", encoding="utf-8"))
    elif(type == "人"): data = json.load(open("data/azurlane/user.json", "r", encoding="utf-8"))
    else: return Message("参数错误")

    banned_list = []
    if(not func):
        for k in data.keys():
            if(int(id) in data[k]):
                banned_list.append(Message(f"{type}{id}的{k}功能被禁用"))
        return Message("不存在")
    else:
        if(func in data.keys()):
            if(int(id) in data[func]):
                return banned_list.append(Message(f"{type}{id}的{k}功能被禁用"))
            else:
                return Message("不存在")
        else:
            return Message("不存在参数名")

blacklist = on_command("黑名单", permission=SUPERUSER)
@blacklist.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if len(arg) == 0:
        await matcher.finish(black_list)
    elif len(arg) == 1:
        if arg[0] == "清空":
            await matcher.finish(await clear_blacklist())
        else:
            await matcher.finish("参数不足")
    elif len(arg) == 2:
        await matcher.finish("参数不足")
    elif len(arg) == 3:
        if arg[0] == "添加":
            await matcher.finish(await add_blacklist(arg[1], arg[2]))
        elif arg[0] == "删除":
            await matcher.finish(await del_blacklist(arg[1], arg[2]))
        elif arg[0] == "查询":
            await send_forward_msg(bot, event, "封禁查询", event.user_id, await check_blacklist(arg[1], arg[2]))
        else:
            await matcher.finish("参数错误")
    elif(len(arg) == 4):
        if arg[0] == "添加":
            await matcher.finish(await add_blacklist(arg[1], arg[2], arg[3]))
        elif arg[0] == "删除":
            await matcher.finish(await del_blacklist(arg[1], arg[2], arg[3]))
        elif arg[0] == "查询":
            await send_forward_msg(bot, event, "封禁查询", event.user_id, await check_blacklist(arg[1], arg[2], arg[3]))
        else:
            await matcher.finish("参数错误")
    else:
        await matcher.finish("参数错误")