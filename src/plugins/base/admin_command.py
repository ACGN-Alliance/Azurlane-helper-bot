from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, Bot, Message

from src.plugins.checker.start_checker import init
from src.plugins.base.func_helper import *
from src.plugins.utils import send_forward_msg
from src.plugins.json_utils import JsonUtils as ju
from src.plugins.base.sync import data_sync

from typing import List, Annotated
import json

# 数据操作部分 #
update_data = on_command("更新数据", permission=SUPERUSER)
@update_data.handle()
async def _():
    await update_data.send("正在更新数据...")
    if(await data_sync()):
        await update_data.send("更新完成")
    else:
        await update_data.send("更新失败, 请检查后台输出")

update_data_on = on_command("自动更新", permission=SUPERUSER)
@update_data_on.handle()
async def _(args: Annotated[Message, CommandArg()]):
    arg = args.extract_plain_text().split()
    if(len(arg) == 0):
        await update_data_on.finish("使用方法: 更新设置 [开启/关闭]")
    elif(arg[0] in ["开启", "on"]):
        await ju.update_val("data/config.json", "regular_update", True)

        try:
            from nonebot_plugin_apscheduler import scheduler
            scheduler.add_job(data_sync, "interval", hour=24)
        except ImportError:
            await update_data_on.finish("未检测到nonebot_plugin_apscheduler, 请安装, 否则自动更新无法使用")
        except Exception as e:
            await update_data_on.finish(str(e))
        await update_data_on.finish("自动更新已开启")
    elif(arg[0] in ["关闭", "off"]):
        await ju.update_val("data/config.json", "regular_update", False)
        await update_data_on.finish("自动更新已关闭")

# 黑名单管理 #
async def clear_blacklist():
    # group_data = json.load(open("data/group.json", "r", encoding="utf-8"))
    # user_data = json.load(open("data/user.json", "r", encoding="utf-8"))
    # for k in group_data.keys():
    #     group_data[k] = []
    # for k in user_data.keys():
    #     user_data[k] = []
    await ju.del_val("data/group.json", [])

    return Message("清空完成")

async def add_blacklist(type: str, id: str, func: str = "") -> Message:
    if(not id.isdigit()): return Message("号码必须为数字")
    # if(type == "群"): data = json.load(open("data/group.json", "r", encoding="utf-8"))
    # elif(type == "人"): data = json.load(open("data/user.json", "r", encoding="utf-8"))
    # else: return Message("参数错误")

    if(type == "群"): data = await ju.get_val("data/group.json", [])
    elif(type == "人"): data = await ju.get_val("data/user.json", [])
    else: return Message("参数错误")

    if data is None:
        return Message("数据初始化出错，请重启bot")
    if(not func):
        data["global"].append(int(id))
    else:
        if(func in data.keys()):
            data[func].append(int(id))
        else:
            data[func] = [int(id)]
    
    json.dump(data, open("data/group.json" if(type == "群") else "data/user.json", "w", encoding="utf-8"))    
    return Message("添加完成")

async def del_blacklist(type: str, id: str, func: str = "") -> Message:
    if(not id.isdigit()): return Message("号码必须为数字")
    if(type == "群"): data = await ju.get_val("data/group.json", [])
    elif(type == "人"): data = await ju.get_val("data/user.json", [])
    else: return Message("参数错误")
    if data is None:
            return Message("数据初始化出错，请重启bot")
    
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
    json.dump(data, open("data/group.json" if(type == "群") else "data/azurlane/user.json", "w", encoding="utf-8"))    
    return Message("删除完成")

async def check_blacklist(type: str, id: str, func: str = "") -> List[Message] | Message | None:
    if(not id.isdigit()): return Message("号码必须为数字")
    if(type == "群"): data = await ju.get_val("data/group.json", [])
    elif(type == "人"): data = await ju.get_val("data/user.json", [])
    else: return Message("参数错误")
    if data is None:
        return Message("数据初始化出错，请重启bot")

    banned_list = []
    if(not func):
        for k in data.keys():
            if(int(id) in data[k]):
                banned_list.append(Message(f"{type}{id}的{k}功能被禁用"))
        if(len(banned_list) == 0):
            return Message("不存在")
    else:
        if(func in data.keys()):
            if(int(id) in data[func]):
                banned_list.append(Message(f"{type}{id}的{func}功能被禁用"))
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
            lst = await check_blacklist(arg[1], arg[2])
            if(isinstance(lst, Message)):
                await matcher.finish(lst)
            elif(isinstance(lst, list)):
                await send_forward_msg(bot, event, "封禁查询", str(event.user_id), lst)
            else:
                await matcher.finish()
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
                await matcher.finish()
        else:
            await matcher.finish("参数错误")
    else:
        await matcher.finish("参数错误")

ver = on_command("版本", permission=SUPERUSER)
@ver.handle()
async def _():
    await ver.finish(f"当前版本：{__version__}")