from nonebot.adapters.onebot.v11 import (Message,
                                         PrivateMessageEvent,
                                         Bot,
                                         Event,
                                         GroupMessageEvent,
                                         MessageEvent,
                                         GROUP_ADMIN,
                                         GROUP_OWNER)
from nonebot.exception import ActionFailed
from typing import List

async def send_forward_msg_type(
        bot: Bot,
        type: str,
        name: str,
        msgs: List[Message],
        *args,
        uin: str = "",
        gid: int = 0,
        uid: int = 0
):
    """
    :说明: `send_forward_msg`
    > 发送合并转发消息
    :参数:
      * `bot: Bot`: bot 实例
      * `type: str`: 消息类型
      * `name: str`: 名字
      * `uin: str`: qq号
      * `msgs: List[Message]`: 消息列表
    """
    if not uin:
        uin = str(bot.self_id)

    def to_node(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_node(msg) for msg in msgs]
    try:
        if type == "private":
            await bot.call_api(
                "send_private_forward_msg", user_id=uid, messages=messages
            )
        elif type == "group":
            await bot.call_api(
                "send_group_forward_msg", group_id=gid, messages=messages
            )
    except ActionFailed:
        if type == "private":
            await bot.send_private_msg(user_id=uid, message="合并转发消息发送失败")
        elif type == "group":
            await bot.send_group_msg(group_id=gid, message="合并转发消息发送失败")

async def send_forward_msg(
        bot: Bot,
        event: Event,
        name: str,
        uin: str,
        msgs: List[Message]
):
    """
    :说明: `send_forward_msg`
    > 发送合并转发消息
    :参数:
      * `bot: Bot`: bot 实例
      * `event: Event`: 事件
      * `name: str`: 名字
      * `uin: str`: qq号
      * `msgs: List[Message]`: 消息列表
    """

    if isinstance(event, GroupMessageEvent):
        await send_forward_msg_type(
            bot, "group", name, msgs, gid=event.group_id, uin=uin
        )
    elif isinstance(event, PrivateMessageEvent):
        await send_forward_msg_type(
            bot, "private", name, msgs, uid=event.user_id, uin=uin
        )

async def is_in_group(event: MessageEvent):
    return isinstance(event, GroupMessageEvent)

async def is_in_private(event: MessageEvent):
    return isinstance(event, PrivateMessageEvent)