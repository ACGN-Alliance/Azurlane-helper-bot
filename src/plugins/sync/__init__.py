from typing import Annotated

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot_plugin_apscheduler import scheduler

from src.plugins.config import cfg
from src.plugins._error import *

from .operation import sync_repo

update_data = on_command("更新数据", permission=SUPERUSER)
@update_data.handle()
async def _():
    await update_data.send("正在更新数据...")
    try:
        if await sync_repo():
            await update_data.send("更新完成")
    except Exception as e:
        await report_error(format_exc(), update_data)
        await update_data.send("更新失败, 请检查后台输出")

update_data_on = on_command("自动更新", permission=SUPERUSER)
@update_data_on.handle()
async def _(args: Annotated[Message, CommandArg()]):
    arg = args.extract_plain_text().split()
    if len(arg) == 0:
        await update_data_on.finish("使用方法: %自动更新 [开启/关闭]")
    elif arg[0] == "开启":
        interval = cfg["base"]["auto_update_time"]
        if interval == -1:
            await update_data_on.finish("config.yml中未设置自动更新时间, 无法开启自动更新")
        elif interval <= 5:
            await update_data_on.finish("自动更新时间过短, 请设置大于5的值")
        scheduler.add_job(sync_repo, "interval", minute=interval, id="sync_repo")
    elif arg[0] == "关闭":
        try:
            scheduler.remove_job("sync_repo")
            await update_data_on.finish("自动更新已关闭")
        except KeyError:
            await update_data_on.finish("自动更新已处于关闭状态")