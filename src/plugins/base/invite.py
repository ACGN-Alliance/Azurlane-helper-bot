from nonebot.adapters.onebot.v11 import (GroupRequestEvent,
                                         FriendRequestEvent,
                                         Message,
                                         RequestEvent,
                                         Bot)
from nonebot import on_request

from src.plugins.json_utils import JsonUtils
from src.plugins.config import cfg

rq = on_request()
@rq.handle()
async def _(bot: Bot, event: RequestEvent):
    user = cfg["user"]["super_admin"][0]
    if isinstance(event, FriendRequestEvent):
        if cfg["user"]["can_invited_to_group"]:
            num = await JsonUtils.get_val("./data/invite.json", ["friends", "max"])
            event: FriendRequestEvent
            data = {
                "num": num + 1,
                "applicant": event.user_id,
                "info": event.comment,
                "flag": event.flag
            }
            nname = (await bot.call_api("get_stranger_info", user_id=event.user_id))["nickname"]
            await JsonUtils.update_val("./data/invite.json", ["friends", num+1], data)
            msg = Message(f"收到了好友请求：\n来自{event.user_id}({nname})\n申请信息{event.comment}")
            await bot.send_private_msg(user_id=int(user), message=msg)
    elif isinstance(event, GroupRequestEvent):
        pass