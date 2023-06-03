import os.path, sys

from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver
from nonebot.log import logger, default_format
from src.plugins.sync.operation import *

from src.plugins.server_status import check
from src.plugins.config import cfg
from nonebot_plugin_apscheduler import scheduler

driver = get_driver()
@driver.on_bot_connect
async def _(bot: Bot):
    if cfg["base"]["startup_notify"]:
        for user in get_driver().config.superusers:
            await bot.send_private_msg(user_id=int(user), message="Bot已启动")

@driver.on_startup
async def init():
    logger.add("error.log", level="ERROR", format=default_format)
    # 文件检查
    proxy = cfg["base"]["network_proxy"]
    if proxy:
        set_proxy(proxy)

    if not (cfg.get("user") or cfg.get("user").get("super_admin")):
        logger.error("未找到正确配置，请初始化config")
        sys.exit(0)
    elif len(cfg["user"]["super_admin"]) == 0:
        logger.error("未配置必须项 super_admin ，请配置完成后重新启动")
        sys.exit(0)

    if cfg["base"]["startup_update"]:
        await local_file_check()
        if (await sync_repo()):
            logger.info("数据更新成功")
    else:
        logger.info("config.yaml中\"startup_update\"选项已关闭, 将不会更新数据")
        if not os.path.exists("data"):
            logger.warning("data文件夹不存在，使用时会报错，请将\"startup_update\"选项打开后重新启动")
            sys.exit(0)

    # 需要读取文件无法直接预加载
    auto_check = cfg["func"]["server_status_monitor_refresh_time"]
    if (not isinstance(auto_check, int)):
        pass
    else:
        if auto_check < 30 or auto_check > 6000:
            logger.info(f"server_status_monitor_refresh_time{auto_check}, 正常范围为1~1440, 定时检查将不会生效")
        else:
            scheduler.add_job(check, "interval", seconds=auto_check)

    for user in cfg["user"]["super_admin"]:
        # TODO ccg群成员加入超管
        get_driver().config.superusers.add(user)