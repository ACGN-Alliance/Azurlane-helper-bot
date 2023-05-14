from nonebot.adapters.onebot.v11 import (GroupRequestEvent,
                                         FriendRequestEvent,
                                         Message,
                                         RequestEvent,
                                         GroupMessageEvent,
                                         Bot)
from nonebot import on_request, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GROUP_ADMIN

from src.plugins.json_utils import JsonUtils
from src.plugins.config import cfg
from src.plugins.utils import is_in_group

rq = on_request()

__usage__ = '''
用法: 
/处理加群请求 num [1/0]
1为同意，0为拒绝
也可以 /处理加群请求 num [1/0] 理由
'''

@rq.handle()
async def _(bot: Bot, event: RequestEvent):
    user = cfg["user"]["super_admin"][0]
    if isinstance(event, FriendRequestEvent):
        if cfg["user"]["can_invited_to_friend"]:
            num = await JsonUtils.get_val("./data/invite.json", ["friends", "max"])
            nname = (await bot.call_api("get_stranger_info", user_id=event.user_id))["nickname"]
            data = {
                "num": num + 1,
                "applicant": event.user_id,
                "info": event.comment,
                "flag": event.flag,
                "nickname": nname
            }
            await JsonUtils.update_many_vals(["./data/invite.json", "./data/invite.json"],
                                             [["friends", num + 1], ["friends", "max"]],
                                             [data, num + 1])
            msg = Message(f"收到了好友请求：\n来自{event.user_id}({nname})\n申请信息:{event.comment}")
            await bot.send_private_msg(user_id=int(user), message=msg)
    elif isinstance(event, GroupRequestEvent):
        if cfg["user"]["can_invited_to_group"]:
            nname = (await bot.call_api("get_stranger_info", user_id=event.user_id))["nickname"]
            data = {
                "num": None,
                "sub_type": event.sub_type,
                "applicant": event.user_id,
                "info": event.comment,
                "flag": event.flag,
                "nickname": nname
            }
            if event.sub_type == "add":
                num = await JsonUtils.get_val("./data/invite.json", ["groups", event.group_id, "max"])
                data["num"] = num + 1
                await JsonUtils.update_many_vals(["./data/invite.json", "./data/invite.json"],
                                                 [["groups", event.group_id, num + 1], ["groups", event.group_id, "max"]],
                                                 [data, num + 1])
                msg = Message(f"收到了加群请求：\n来自{event.user_id}({nname})\n申请信息:{event.comment}")
                await bot.send_group_msg(group_id=int(event.group_id), message=msg)
            elif event.sub_type == "invite":
                num = await JsonUtils.get_val("./data/invite.json", ["groups", "invite", "max"])
                data["num"] = num + 1
                await JsonUtils.update_many_vals(["./data/invite.json", "./data/invite.json"],
                                                 [["groups", "invite", num + 1],
                                                  ["groups", "invite", "max"]],
                                                 [data, num + 1])
                msg = Message(f"收到了好友请求：\n来自{event.user_id}({nname})\n申请信息:{event.comment}")
                await bot.send_private_msg(user_id=int(user), message=msg)

approve_group = on_command("处理加群请求", permission=GROUP_ADMIN, rule=is_in_group)

@approve_group.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if len(arg) == 0 or len(arg) == 1:
        await approve_group.finish(__usage__)
    elif len(arg) == 2:
        req = await JsonUtils.get_val("./data/invite.json", ["groups", event.group_id, arg[0]])
        if not req:
            await approve_group.finish("不存在该请求")
        await bot.set_group_add_request(flag=req["flag"], sub_type=req["sub_type"], approve=True if arg[1] else False,
                                        reason="None")
        await JsonUtils.del_val("./data/invite.json", ["groups", event.group_id, arg[0]])
        (nickname, qq) = req["nickname"], req["applicant"]
        await approve_group.send(f"已处理{nickname}({qq})的加群申请")
    elif len(arg) >= 3:
        req = await JsonUtils.get_val("./data/invite.json", ["groups", event.group_id, arg[0]])
        if not req:
            await approve_group.finish("不存在该请求")
        await bot.set_group_add_request(flag=req["flag"], sub_type=req["sub_type"], approve=True if arg[1] else False,
                                        reason=arg[2])
        await JsonUtils.del_val("./data/invite.json", ["groups", event.group_id, arg[0]])
        (nickname, qq) = req["nickname"], req["applicant"]
        await approve_group.send(f"已处理{nickname}({qq})的加群申请")


group_approve_list = on_command("查看群申请列表", permission=GROUP_ADMIN, rule=is_in_group)
@group_approve_list.handle()
async def _(event: GroupMessageEvent):
    req = await JsonUtils.get_val("./data/invite.json", ["groups", event.group_id])
    if len(req) == 0:
        await group_approve_list.finish("目前没有未处理的加群申请~")

    # TODO 测试JsonUtils功能([]属性)