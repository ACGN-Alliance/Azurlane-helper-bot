from httpx import get
import time, nonebot

from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.log import logger

from src.plugins.json_utils import JsonUtils as ju
from src.plugins.utils import send_forward_msg_type
from src.plugins._error import report_error
from src.plugins.config import cfg

data_dir = "./data/server/server_status.json"
user_data_dir = "./data/server/server_status_user.json"
interval_time = cfg["func"]["server_status_monitor_refresh_time"]
all_available_server_name = ["日服", "官服", "渠道服", "ios"]
all_server_name = ["日服", "官服", "渠道服", "ios", "B服", "bilibili"]

async def get_server_ip(server_name: str):
    if server_name == "日服":
        return "http://18.179.191.97/?cmd=load_server?"
    elif server_name in ["官服", "B服", "bilibili"]:
        return "http://118.178.152.242/?cmd=load_server?"
    elif server_name == "渠道服":
        return "http://203.107.54.70/?cmd=load_server?"
    elif server_name in ["ios", "苹果"]:
        return "http://101.37.104.227/?cmd=load_server?"
    else:
        msg = "不存在该服务器， 目前支持的服务器有：日服、官服(B服/bilibili)、渠道服、ios(苹果)"
        await report_error(msg)
        raise Exception(msg)

async def get_server_state(name: str):
    all_status = {
        0: "已开启",
        1: "未开启",
        2: "爆满",
        3: "已满",
    }
    is_updated = False

    ip = await get_server_ip(name)
    resp = get(ip)
    if resp.status_code != 200:
        return Message("服务器状态推送出错")

    msg = Message(f"{name}服务器状态：\n")
    ori_data = await ju.get_val(data_dir, [])
    if not ori_data:
        write_data = ori_data
        for server in resp.json():
            write_data[name] = {server["name"]: server["state"]}
        await ju.update_whole_file(data_dir, write_data)

    for server in resp.json():
        server_name = server["name"]
        status = server["state"]
        if ori_data.get(name):
            if not ori_data[name].get(server_name):
                ori_data[name].update({server["name"]: server["state"]})
                continue
            if ori_data[name][server_name] == status:
                continue

        is_updated = True
        ori_data[name] = {server["name"]: server["state"]}
        msg += Message(f"{server['name']}：{all_status[server['state']]}, 状态码：{server['state']}\n")

    if is_updated:
        await ju.update_whole_file(data_dir, ori_data)
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return msg + Message(f"\n更新时间：{t}")
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

async def check():
    (bot,) = nonebot.get_bots().values()
    await push_msg(bot)
    logger.info(f"[自动检查]已检查服务器状态")