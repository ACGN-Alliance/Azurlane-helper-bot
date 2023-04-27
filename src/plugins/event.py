from nonebot.message import run_postprocessor
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.exception import ActionFailed, WebSocketClosed
from nonebot import get_driver
from nonebot.log import logger

from yaml.error import YAMLError

@run_postprocessor
async def _(bot: Bot, event: MessageEvent, e: Exception):
    if isinstance(e, ActionFailed):
        extra_msg = f"消息发送失败，账号可能被风控，请参看gocq输出\n"
        logger.error(extra_msg + str(e))
    elif isinstance(e, WebSocketClosed):
        extra_msg = f"消息发送失败，WebSocket连接已关闭，请检查运行状态\n"
        logger.error(extra_msg + str(e))
    elif isinstance(e, YAMLError):
        extra_msg = f"config.yaml格式错误\n"
        logger.error(extra_msg + str(e))
    elif isinstance(e, OSError):
        extra_msg = f"路径出现错误\n"
        logger.error(extra_msg + str(e))
    else:
        extra_msg = ""
        logger.error(str(e))

    # msg = f"事件处理出现错误: {type(e)}---{e}" + extra_msg
    # await bot.send_private_msg(user_id=int(get_driver().config.superusers.pop()), message=msg)