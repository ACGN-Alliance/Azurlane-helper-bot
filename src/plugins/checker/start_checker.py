from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_driver
from nonebot.log import logger
from nonebot.matcher import MatcherManager

import os, json

from src.plugins.sync_list import sync_ls
from src.plugins.sync import GithubHook

driver = get_driver()
@driver.on_bot_connect
async def _(bot: Bot):
    cfg = driver.config
    if cfg.start_up_notify:
        for user in cfg.superusers:
            bot.send_private_msg(user_id=user, message="Bot已启动")

@driver.on_startup
async def init():
    is_inited = False
    data_path_lst = ["data/azurlane/", "data/azurlane/data/"]
    for path in data_path_lst:
        if not os.path.exists(path):
            os.makedirs(path)
            is_inited = True

    data_file = ["data/azurlane/group.json", "data/azurlane/user.json"]
    for file in data_file:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write(json.dumps({}))

    g = GithubHook()
    if is_inited:
        logger.warning("未检测到数据文件夹, 即将进入初始化")
        try: 
            await g.sync_data(sync_ls)
            with open(data_path_lst[0] + "git.json", "w", encoding="utf-8") as f:
                f.write(json.dumps({"lastest_commit": await g.get_lastest_commit()}))
            logger.info("初始化完成")
        except Exception as e:
            logger.error(e)
            logger.error("初始化失败, 请删除data/azurlane文件夹后重试")
    else:
        logger.info("检测到数据文件夹, 即将进行数据更新")
        try:
            with open(data_path_lst[0] + "git.json", "r", encoding="utf-8") as f:
                lastest_commit = json.loads(f.read())["lastest_commit"]
        except FileNotFoundError:
            lastest_commit = None

        try:
            lastest_commit = await g.get_lastest_commit()
        except Exception as e:
            logger.error(e)
            logger.error("获取最新commit失败")
            return
        
        if lastest_commit != lastest_commit:
            try: 
                await g.sync_data(sync_ls)
                with open(data_path_lst[0] + "git.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps({"lastest_commit": lastest_commit}))
                logger.info("数据更新完成")
            except Exception as e:
                logger.error(e)
                logger.error("数据更新失败, 请重试")
        else:
            logger.info("数据无需更新")