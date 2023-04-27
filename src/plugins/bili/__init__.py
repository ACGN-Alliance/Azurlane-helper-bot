from nonebot import on_command
from typing import Annotated

from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    GROUP_ADMIN,
    GROUP_OWNER,
)
from nonebot.params import CommandArg

from src.plugins.checker.rule_check import bili_handle
from src.plugins.json_utils import read_and_add_list, read_and_remove_list
from .bili_article import *

bili_sub = on_command("bili订阅", rule=bili_handle, permission=GROUP_ADMIN | GROUP_OWNER)
@bili_sub.handle()
async def _(event: GroupMessageEvent, arg: Annotated[Message, CommandArg()]):
    args = arg.extract_plain_text().split()
    if(len(args) == 0): await bili_sub.finish("用法: bili订阅 开启|关闭")
    if(args[0] == "开启"):
        _if = await read_and_add_list("data/group_func.json", "bili", event.group_id)
        if(not _if): await bili_sub.finish("本群已启用bili订阅")
        await bili_sub.finish("开启成功")
    elif(args[0] == "关闭"):
        _if = await read_and_remove_list("data/azurlane/group_func.json", "bili", event.group_id)
        if(not _if): await bili_sub.finish("本群未启用bili订阅")
        await bili_sub.finish("关闭成功")
    else:
        await bili_sub.finish("用法: bili订阅 开启|关闭")