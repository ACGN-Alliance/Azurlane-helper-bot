from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER,
    GroupIncreaseNoticeEvent
)
from nonebot import on_command, on_keyword, on_notice, on_message

from src.plugins.checker.rule_check import event_handle, chat_handle, notice_handle

import re

# 群事件监听
wel = on_notice(rule=notice_handle)
async def welcome(bot: Bot, event: GroupIncreaseNoticeEvent):
    await bot.send_group_msg(group_id=event.group_id, message="欢迎新人入群~")
    # TODO: 定制欢迎语

# 群消息监听
msg = on_message(rule=chat_handle, priority=99)
@msg.handle()
async def _(bot: Bot, event: MessageEvent):
    kw_lst = open("data")

    r = re.compile(r"[CQ:at,qq={}]".format(bot.self_id))
    if(re.match(r, event.get_plaintext()) is not None):
        await msg.finish("你好~, 找我有什么事情呀")