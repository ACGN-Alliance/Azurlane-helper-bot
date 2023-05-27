from git import Repo, RefLogEntry, GitConfigParser
import os, sys
from subprocess import Popen, DEVNULL, call, PIPE

from nonebot import logger

# TODO 数据文件路径重写

def set_proxy(url: str):
    std = Popen("git config http.proxy", shell=True, stdout=PIPE, stderr=PIPE)
    if not std.returncode:
        out = std.stdout.read().decode("utf-8")
    else:
        out = ""
    if out.__eq__(url):
        return
    else:
        Popen(f"git config http.proxy {url}", shell=True, stdout=DEVNULL)

async def sync_repo():
    if os.path.exists("./data/remote"):
        repo = Repo("./data/remote")
        remote = repo.remote()
        try:
            remote.fetch(kill_after_timeout=20)
        except Exception as e:
            logger.error(f"同步数据仓库失败: {e}")
            raise e

        if str(next(repo.iter_commits()))[:7] == str(next(remote.repo.iter_commits(remote.repo.heads[0].name)))[:7]:
            logger.info("数据仓库已是最新版本")
            return None
        else:
            repo.remote().update()
            return True

    else:
        os.makedirs("./data/remote")
        logger.info("未检测到数据文件夹, 即将开始克隆数据仓库。若出现下载缓慢的情况，请在config.yml中配置代理")
        try:
            Repo.clone_from("https://github.com/ACGN-Alliance/nonebot-plugin-azurlane-assistant-data", "./data/remote")
            return True
        except Exception as e:
            logger.error(f"克隆数据仓库失败: {e}")
            raise e
