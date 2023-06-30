from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (MessageEvent, 
                                        GroupMessageEvent,
                                        PrivateMessageEvent, 
                                        GroupIncreaseNoticeEvent,
                                        NoticeEvent,
                                        Event,
                                        Bot)
from nonebot import get_driver
import json

from AZbot.plugins.config import black_list
from AZbot.plugins.sync.operation import local_file_check

async def event_handle(event: Event, bot: Bot, state: T_State) -> bool:
    """
    事件处理器

    """
    async def user_check(user_id: int) -> bool:
        if str(user_id) in get_driver().config.superusers:
            return True
        if user_id in black_list:
            return False
        try:
            text_ = json.load(open("data/user.json", "r", encoding="utf-8"))
            cmd_ = state["_prefix"]["command"][0]
        except TypeError:
            return False
        except FileNotFoundError:
            local_file_check()
            return False
        if text_.get(cmd_) is None:
            text_.update({cmd_: []})
            open("data/user.json", "w", encoding="utf-8").write(json.dumps(text_))
            return True
        if user_id not in text_[cmd_]:
            return True
        elif user_id not in text_["global"]:
            return True
        else:
            return False

    if isinstance(event, GroupMessageEvent):
        try:
            text = json.load(open("data/group.json", "r", encoding="utf-8"))
            cmd = state["_prefix"]["command"][0]
        except TypeError:
            return False
        except FileNotFoundError:
            local_file_check()
            return False
        if text.get(cmd) is None:
            text.update({cmd: []})
            try:
                open("data/group.json", "w", encoding="utf-8").write(json.dumps(text))
            except FileNotFoundError:
                local_file_check()
                return False
            if(await user_check(event.user_id)):
                return True
            else:
                await bot.send_group_msg(group_id=event.group_id, message="您没有权限使用此命令")
                return False
        if event.group_id not in text[cmd]:
            if(await user_check(event.user_id)):
                return True
            else:
                await bot.send_group_msg(group_id=event.group_id, message="您没有权限使用此命令")
                return False
        else:
            await bot.send_group_msg(group_id=event.group_id, message="本群没有权限使用此命令")
            return False
    elif(isinstance(event, PrivateMessageEvent)):
        if (await user_check(event.user_id)):
            return True
        else:
            await bot.send_private_msg(user_id=event.user_id, message="您没有权限使用此命令")
            return False
        
    else:
        return True

async def _if_exist_func(data: dict, file: str, key: str):
    if(data.get(key) is None):
        data.update({key: []})
        open(file, "w", encoding="utf-8").write(json.dumps(data))
        return False
    else:
        return True

async def notice_handle(event: NoticeEvent):
    if(isinstance(event, GroupIncreaseNoticeEvent)):
        try:
            text = json.load(open("data/group_func.json", "r", encoding="utf-8"))
        except FileNotFoundError:
            local_file_check()
            return False
        _if = await _if_exist_func(text, "data/group_func.json", "group_welcome")
        if not _if: return False
        if(event.group_id in text["group_welcome"]): return True
        else: return False
    else:
        return False

async def chat_handle(event: MessageEvent):
    if(not isinstance(event, GroupMessageEvent)): return False
    try:
        text = json.load(open("data/group_func.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        local_file_check()
        return False
    _if = await _if_exist_func(text, "data/group_func.json", "group_chat")
    if not _if: return False
    if(event.group_id in text["group_chat"]): return True
    else: return False

async def bili_handle(event: GroupMessageEvent):
    try:
        text = json.load(open("data/group_func.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        local_file_check()
        return False
    _if = await _if_exist_func(text, "data/group_func.json", "bili")
    if not _if: return False
    if(event.group_id in text["bili"]): return True
    else: return False