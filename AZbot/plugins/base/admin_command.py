import random

from nonebot import on_command, get_driver
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.log import logger

from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message

from AZbot.plugins.utils import send_forward_msg
from AZbot.plugins.json_utils import JsonUtils as ju

from typing import List, Annotated
import json, asyncio

__version__ = "0.0.1-dev"

__usage__ = Message(Message("黑名单功能: \n")
+ Message("1. 添加黑名单[SU]: /黑名单 添加 [群/人] 号码 *功能名\n")
+ Message("2. 删除黑名单[SU]: /黑名单 删除 [群/人] 号码 *功能名\n")
+ Message("3. 清空黑名单[SU]: /黑名单 清空\n")
+ Message("4. 是否在黑名单: /黑名单 查询 [群/人] 号码 *功能名\n"))

reboot = on_command("重启", permission=SUPERUSER)
@reboot.handle()
async def _():
    await reboot.finish("正在重启...(注意: 请确保之前是使用nb run --reload启动的bot，否则此功能无法正常使用)")
    with open("AZbot/plugins/_tmp.py", "w") as f:
        f.write(str(random.random()))

# 黑名单管理 #
async def clear_blacklist():
    await ju.del_val("data/group.json", [])

    return Message("清空完成")

async def get_data(type_: str):
    if(type_ == "群"): data = await ju.get_val("data/group.json", [])
    elif(type_ == "人"): data = await ju.get_val("data/user.json", [])
    else: return Message("参数错误")
    if data is None:
        return Message("数据初始化出错，请重启bot")
    return data

async def add_blacklist(type_: str, id_: str, func: str = "") -> Message:
    data = await get_data(type_)
    if(isinstance(data, Message)): return data

    if(not func):
        data["global"].append(int(id_))
    else:
        if(func in data.keys()):
            data[func].append(int(id_))
        else:
            data[func] = [int(id_)]
    
    json.dump(data, open("data/group.json" if(type_ == "群") else "data/user.json", "w", encoding="utf-8"))
    return Message("添加完成")

async def del_blacklist(type_: str, id_: str, func: str = "") -> Message:
    data = await get_data(type_)
    if(isinstance(data, Message)): return data
    
    if(not func):
        for k in data.keys():
            if(int(id_) in data[k]):
                data[k].remove(int(id_))
    else:
        if(func in data.keys()):
            if(int(id_) in data[func]):
                data[func].remove(int(id_))
        else:
            return Message("不存在参数名")
    json.dump(data, open("data/group.json" if(type_ == "群") else "data/azurlane/user.json", "w", encoding="utf-8"))
    return Message("删除完成")

async def check_blacklist(type_: str, id_: str, func: str = "") -> List[Message] | Message | None:
    data = await get_data(type_)
    if(isinstance(data, Message)): return data

    banned_list = []
    if(not func):
        for k in data.keys():
            if(int(id_) in data[k]):
                banned_list.append(Message(f"{type_}{id_}的{k}功能被禁用"))
        if(len(banned_list) == 0):
            return Message("不存在")
    else:
        if(func in data.keys()):
            if(int(id_) in data[func]):
                banned_list.append(Message(f"{type_}{id_}的{func}功能被禁用"))
            else:
                return Message("不存在")
        else:
            return Message("不存在参数名")
    return banned_list

blacklist = on_command("黑名单", permission=SUPERUSER)
@blacklist.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if len(arg) == 0:
        await matcher.finish(__usage__)
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
            lst = await check_blacklist(arg[1], arg[2])
            if(isinstance(lst, Message)):
                await matcher.finish(lst)
            elif(isinstance(lst, list)):
                await send_forward_msg(bot, event, "封禁查询", str(event.user_id), lst)
        else:
            await matcher.finish("参数错误")
    elif(len(arg) == 4):
        if arg[0] == "添加":
            await matcher.finish(await add_blacklist(arg[1], arg[2], arg[3]))
        elif arg[0] == "删除":
            await matcher.finish(await del_blacklist(arg[1], arg[2], arg[3]))
        elif arg[0] == "查询":
            lst = await check_blacklist(arg[1], arg[2])
            if(isinstance(lst, Message)):
                await matcher.finish(lst)
            elif(isinstance(lst, list)):
                await send_forward_msg(bot, event, "封禁查询", str(event.user_id), lst)
        else:
            await matcher.finish("参数错误")
    else:
        await matcher.finish("参数错误")

ver = on_command("版本", permission=SUPERUSER)
@ver.handle()
async def _():
    await ver.finish(f"当前版本：{__version__}")

su_list = on_command("su-list")
@su_list.handle()
async def _():
    logger.info(get_driver().config.superusers)