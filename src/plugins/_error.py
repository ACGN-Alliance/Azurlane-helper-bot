import os.path
import time

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot import get_bots
from traceback import format_exc

from src.plugins.config import cfg

ccg = cfg["user"]["ccg"]
log_max_cache_size = cfg["develop"]["log_max_cache_size"]
log_max_cache_num = cfg["develop"]["log_max_cache_num"]

def error_handler(func):
    """
    错误处理装饰器

    :description: 用于捕获函数内部的错误并打印到日志中, 并保存至error.log

    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"在执行{func.__name__}时发生错误: {e}")
            logger.error(format_exc())
            with open("logs/error.log", "a", encoding="utf-8") as f:
                f.write(f"在执行{func.__name__}时发生错误: {e}\n")
                f.write(format_exc())
    return wrapper

async def report_error(err: str, *args, matcher: Matcher = None, func: str = ""):
    """
    错误上报函数, 并保存至error.log
    """
    if not os.path.exists("logs"):
        os.mkdir("logs")
    if matcher:
        name = matcher.__name__
    elif func:
        name = func
    else:
        name = "未知函数"
    (bot, ) = get_bots().values()
    logger.error(f"在执行{name}时发生错误: {err}")
    await matcher.send(err)
    if ccg != -1:
        await bot.send_group_msg(group_id=ccg, message=f"在执行{name}时发生错误: {err}")

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    err_info = f"[{t}] 运行{name}时发生错误 | {err}\n"
    e_lst = os.listdir("logs")
    if os.path.getsize(f"logs/error-{len(e_lst)}.log") > (1024 * log_max_cache_size):
        if (len(e_lst) >= log_max_cache_num):
            os.remove(f"logs/error-{log_max_cache_size}.log")
            for file in e_lst:
                index = int(file.split("-")[1].split(".")[0])
                os.rename(f"logs/{file}", f"logs/error-{index-1}.log")
            with open(f"logs/error-{log_max_cache_num}.log", "w", encoding="utf-8") as f:
                f.write(err_info)
        else:
            with open(f"logs/error-{len(e_lst) + 1}.log", "w", encoding="utf-8") as f:
                f.write(err_info)
    else:
        with open(f"logs/error-{len(e_lst)}.log", "w", encoding="utf-8") as f:
            f.write(err_info)