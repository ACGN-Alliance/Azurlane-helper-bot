from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent, Bot, Event, GroupMessageEvent
from typing import List

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

    def to_node(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_node(msg) for msg in msgs]
    if(isinstance(event, PrivateMessageEvent)):
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )
    elif(isinstance(event, GroupMessageEvent)):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
