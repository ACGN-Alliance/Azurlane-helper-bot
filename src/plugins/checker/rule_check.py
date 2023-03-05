from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (MessageEvent, 
                                         GroupMessageEvent, 
                                         PrivateMessageEvent, 
                                         GroupIncreaseNoticeEvent,
                                         NoticeEvent,
                                         Event,
                                         Bot)
import json

async def event_handle(event: Event, bot: Bot, state: T_State) -> bool:
    """
    事件处理器

    """
    def user_check(user_id: int) -> bool:
        text = json.load(open("data/azurlane/user.json", "r", encoding="utf-8"))
        cmd = state["_prefix"]["command"][0]
        if text.get(cmd) is None:
            text.update({cmd: []})
            open("data/azurlane/user.json", "w", encoding="utf-8").write(json.dumps(text))
            return True
        if user_id not in text[cmd]:
            return True
        else:
            return False

    if isinstance(event, GroupMessageEvent):
        text = json.load(open("data/azurlane/group.json", "r", encoding="utf-8"))
        cmd = state["_prefix"]["command"][0]
        if text.get(cmd) is None:
            text.update({cmd: []})
            open("data/azurlane/group.json", "w", encoding="utf-8").write(json.dumps(text))
            if(user_check(event.user_id)):
                return True
            else:
                await bot.send_group_msg(group_id=event.group_id, message="您没有权限使用此命令")
                return False
        if event.group_id not in text[cmd]:
            if(user_check(event.user_id)):
                return True
            else:
                await bot.send_group_msg(group_id=event.group_id, message="您没有权限使用此命令")
                return False
        else:
            await bot.send_group_msg(group_id=event.group_id, message="本群没有权限使用此命令")
            return False
    elif(isinstance(event, PrivateMessageEvent)):
        if user_check(event.user_id):
            return True
        else:
            await bot.send_private_msg(user_id=event.user_id, message="您没有权限使用此命令")
            return False
        
    else:
        return True

async def notice_handle(event: NoticeEvent):
    if(isinstance(event, GroupIncreaseNoticeEvent)):
        text = json.load(open("data/azurlane/group_func.json", "r", encoding="utf-8"))
        if(event.group_id in text["group_welcome"]): return True
        else: return False
    else:
        return True

async def chat_handle(event: MessageEvent):
    text = json.load(open("data/azurlane/group_func.json", "r", encoding="utf-8"))
    if(event.group_id in text["group_chat"]): return True
    else: return False