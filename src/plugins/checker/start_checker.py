from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver

from src.plugins.base.sync import data_sync
from src.plugins.config import config

driver = get_driver()
@driver.on_bot_connect
async def _(bot: Bot):
    if config.start_up_notify:
        for user in get_driver().config.superusers:
            await bot.send_private_msg(user_id=int(user), message="Bot已启动")

@driver.on_startup
async def init():
    await data_sync()