from httpx import get
import time, nonebot

from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from src.plugins.config import cfg
from src.plugins.json_utils import JsonUtils as ju
from src.plugins.checker.rule_check import event_handle
from .uti import get_server_state, all_available_server_name, user_data_dir

__usage__ = """服务器状态监测
%服务器状态监测 开启/关闭 [服务器名]
%服务器状态监测 查询 [服务器名]
服务器名可选参数：日服、官服(B服/bilibili)、渠道服、ios(苹果)
"""

monitor = on_command("服务器状态监测", priority=5, rule=event_handle, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
@monitor.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    async def turn_on(matcher_: Matcher, *args, server_name_=None):
        if server_name_ is None:
            server_name_ = all_available_server_name
        dic_ = {
            "type": type_,
            "server": server_name_
        }
        await ju.update_or_create_val(user_data_dir, [id_], dic_)
        await matcher_.finish("服务器状态监测已开启")

    async def turn_off(matcher_: Matcher, *args, server_name_=None):

        res = await ju.get_val(user_data_dir, [id_])
        if server_name_ is None:
            res[id_]["server"] = []
        else:
            res[id_]["server"] = list(set(res[id_]["server"]) - set(server_name_))
        if len(res[id_]["server"]) == 0:
            await ju.del_val(user_data_dir, [id_])
            await matcher_.finish("服务器状态监测已关闭")
        else:
            await ju.update_or_create_val(user_data_dir, [id_], res)
            await matcher_.finish(f"对应服务器状态监测已关闭")

    arg_lst = arg.extract_plain_text().split()
    if isinstance(event, GroupMessageEvent):
        id_ = event.group_id
        type_ = "group"
    else:
        id_ = event.user_id
        type_ = "private"
    if len(arg_lst) == 0:
        await monitor.finish(__usage__)
    elif len(arg_lst) == 1:
        if arg_lst[0] == "开启":
            await turn_on(matcher, server_name_=all_available_server_name)
        elif arg_lst[0] == "关闭":
            await turn_off(matcher)
        elif arg_lst[0] == "查询":
            msg = await get_server_state("官服", need_to_check=False)
            if msg:
                await monitor.send(msg)
            else:
                await monitor.send("服务器状态未更新")
        else:
            await monitor.finish(__usage__)
    elif len(arg_lst) == 2:
        server_name = arg_lst[1:]
        for server in server_name:
            if server not in all_available_server_name:
                await monitor.finish(f"服务器{server}不存在")
        if arg_lst[0] == "开启":
            await turn_on(matcher, server_name_=server_name)
        elif arg_lst[0] == "关闭":
            await turn_off(matcher, server_name_=server_name)
        elif arg_lst[0] == "查询":
            msg = await get_server_state(arg_lst[1], need_to_check=False)
            if msg:
                await monitor.send(msg)
            else:
                await monitor.send("服务器状态未更新")
        else:
            await monitor.finish(__usage__)
    else:
        await monitor.finish(__usage__)