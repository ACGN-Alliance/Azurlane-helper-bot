from typing import Annotated

from httpx import get
from time import time
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from src.plugins.config import cfg
from src.plugins.json_utils import JsonUtils as ju
from src.plugins.checker.rule_check import event_handle
from src.plugins.utils import send_forward_msg_type

data_dir = "./data/azurlane/server/server_status.json"
user_data_dir = "./data/azurlane/server/server_status_user.json"
interval_time = cfg["func"]["server_status_monitor_refresh_time"]

__usage__ = """服务器状态监测
%服务器状态监测 开启/关闭 [服务器名]
%服务器状态监测 查询 [服务器名]
服务器名可选参数：日服、官服(B服/bilibili)、渠道服、ios(苹果)
"""

all_available_server_name = ["日服", "官服", "渠道服", "ios"]
all_server_name = ["日服", "官服", "渠道服", "ios", "B服", "bilibili"]

def get_server_ip(server_name: str):
    if server_name == "日服":
        return "http://18.179.191.97/?cmd=load_server?"
    elif server_name in ["官服", "B服", "bilibili"]:
        return "http://118.178.152.242/?cmd=load_server?"
    elif server_name == "渠道服":
        return "http://203.107.54.70/?cmd=load_server?"
    elif server_name in ["ios", "苹果"]:
        return "http://101.37.104.227/?cmd=load_server?"
    else:
        raise Exception("不存在该服务器， 目前支持的服务器有：日服、官服(B服/bilibili)、渠道服、ios(苹果)")

async def get_server_state(name: str):
    all_status = {
        0: "已开启",
        1: "未开启",
        2: "爆满",
        3: "已满",
    }
    is_update = False

    msg = Message(f"{name}服务器状态：\n")
    ip = get_server_ip(name)
    resp = get(ip)
    if resp.status_code != 200:
        return Message("服务器状态推送出错")

    ori_data = await ju.get_val(data_dir, [])

    for server in resp.json():
        status = server["state"]
        if ori_data[server["name"]]["state"] == status:
            continue

        is_update = True
        msg += Message(f"{server['name']}：{all_status[server['state']]}, 状态码：{server['state']}\n")
    if is_update:
        await ju.update_whole_file(data_dir, resp.json())
        return msg + Message(f"\n更新时间：{time()}")
    else:
        return None

async def push_msg(bot: Bot):
    all_data = {}
    r: dict = await ju.get_val(user_data_dir, [])
    for server in all_available_server_name:
        status = await get_server_state(server)
        all_data[server] = status
    for id_, v in r.items():
        server_lst = r[id_]
        if len(server_lst) == 0:
            continue
        elif len(server_lst) == 1:
            if v["type"] == "group":
                await bot.send_group_msg(group_id=int(id_), message=all_data[server_lst[0]])
            elif v["type"] == "private":
                await bot.send_private_msg(user_id=int(id_), message=all_data[server_lst[0]])
        else:
            msg = []
            for server in server_lst:
                msg.append(all_data[server])
            if v["type"] == "group":
                await send_forward_msg_type(bot=bot, type="group", name="服务器状态", gid=int(id_), msgs=msg)
            elif v["type"] == "private":
                await send_forward_msg_type(bot=bot, type="private", name="服务器状态", uid=int(id_), msgs=msg)


monitor = on_command("服务器状态监测", priority=5, rule=event_handle, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
@monitor.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Annotated[Message, CommandArg()]):
    def turn_on(matcher_: Matcher, *args, server_name_=None):
        if server_name_ is None:
            server_name_ = all_available_server_name
        dic_ = {
            "type": type_,
            "server": server_name_
        }
        await ju.update_or_create_val(user_data_dir, [id_], dic_)
        await matcher_.finish("服务器状态监测已开启")

    def turn_off(matcher_: Matcher, *args, server_name_=None):

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
            turn_on(matcher, server_name_=all_available_server_name)
        elif arg_lst[0] == "关闭":
            turn_off(matcher)
        elif arg_lst[0] == "查询":
            msg = await get_server_state("官服")
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
            turn_on(matcher, server_name_=server_name)
        elif arg_lst[0] == "关闭":
            turn_off(matcher, server_name_=server_name)
        elif arg_lst[0] == "查询":
            msg = await get_server_state(arg_lst[1])
            if msg:
                await monitor.send(msg)
            else:
                await monitor.send("服务器状态未更新")
        else:
            await monitor.finish(__usage__)
    else:
        await monitor.finish(__usage__)