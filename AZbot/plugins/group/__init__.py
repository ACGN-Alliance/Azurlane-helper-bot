from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    GroupIncreaseNoticeEvent,
    GroupMessageEvent
)
from nonebot import on_command, on_notice, on_message
from nonebot.permission import SUPERUSER as SU
from nonebot.typing import T_State

from AZbot.plugins.checker.rule_check import chat_handle, notice_handle
from AZbot.plugins.json_utils import JsonUtils as ju

import re, json

# 群事件监听
wel = on_notice(rule=notice_handle)
async def welcome(bot: Bot, event: GroupIncreaseNoticeEvent):
    wel_msg = await ju.get_val("./data/welcome.json", [str(event.group_id)])
    if not wel_msg:
        wel_msg = "欢迎新人入群~"
    await bot.send_group_msg(group_id=event.group_id, message=wel_msg)

set_welcome = on_command("设置欢迎语", permission=GROUP_ADMIN | GROUP_OWNER | SU)

@set_welcome.handle()
async def _():
    await set_welcome.send("接下来你输入的下一个消息将作为欢迎语，输入\"取消\"以取消操作（支持图片）")

@set_welcome.got("group_id")
async def _(event: GroupMessageEvent):
    if event.get_plaintext() == "取消":
        set_welcome.finish("操作已取消")
    else:
        msg = event.get_plaintext()
        await ju.update_or_create_val("./data/welcome.json", [str(event.group_id)], msg)

# 群消息监听
msg = on_message(rule=chat_handle, priority=99)
@msg.handle()
async def _(bot: Bot, event: MessageEvent):

    # 监测默认关键词并回复
    kw_lst = json.load(open("data/remote/work_bank/default.json", "r", encoding="utf-8"))
    for kw in kw_lst:
        if event.get_plaintext().find(kw) != -1:
            await msg.finish(kw_lst[kw])

    r = re.compile(r"[CQ:at,qq={}]".format(bot.self_id))
    if re.match(r, event.get_plaintext()):
        await msg.finish("你好~, 找我有什么事情呀")