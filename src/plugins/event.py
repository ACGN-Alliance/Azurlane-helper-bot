from nonebot.message import run_postprocessor
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.exception import ActionFailed, WebSocketClosed
from nonebot import get_driver

@run_postprocessor
async def _(bot: Bot, event: MessageEvent, e: Exception):
    if isinstance(e, ActionFailed):
        extra_msg = f"\n\n消息发送失败，账号可能被风控，请参看gocq输出"
    elif isinstance(e, WebSocketClosed):
        extra_msg = f"\n\n消息发送失败，WebSocket连接已关闭，请检查运行状态"

    msg = f"事件处理出现错误: {type(e)}---{e}" + extra_msg
    await bot.send_private_msg(user_id=get_driver().config.superusers[0], message=msg)