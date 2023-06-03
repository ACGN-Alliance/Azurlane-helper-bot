from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER,
    GroupIncreaseNoticeEvent
)
from nonebot import on_command, on_keyword, on_notice, on_message

from AZbot.plugins.checker.rule_check import event_handle, chat_handle, notice_handle
# __version__ = "0.0.1-dev"

import re, json

# 群事件监听
wel = on_notice(rule=notice_handle)
async def welcome(bot: Bot, event: GroupIncreaseNoticeEvent):
    await bot.send_group_msg(group_id=event.group_id, message="欢迎新人入群~")
    # TODO: 定制欢迎语

# 群消息监听
msg = on_message(rule=chat_handle, priority=99)
@msg.handle()
async def _(bot: Bot, event: MessageEvent):

    # 监测默认关键词并回复
    kw_lst = json.load(open("data/remote/work_bank/default.json", "r", encoding="utf-8"))
    for kw in kw_lst:
        if(event.get_plaintext().find(kw) != -1):
            await msg.finish(kw_lst[kw])

    r = re.compile(r"[CQ:at,qq={}]".format(bot.self_id))
    if(re.match(r, event.get_plaintext()) is not None):
        await msg.finish("你好~, 找我有什么事情呀")
#
# ver = on_command("版本")
# @ver.handle()
# async def _():
#     data = json.load(open("data/git.json", "r", encoding="utf-8"))
#     com = data["lastest_commit"]
#     await ver.finish(f"当前版本: {__version__}\n数据版本: {com[:6]}")