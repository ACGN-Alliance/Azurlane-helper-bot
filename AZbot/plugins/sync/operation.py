from git import Repo
import os, sys, json, pathlib
from subprocess import Popen, DEVNULL, call, PIPE

# from AZbot.plugins.json_utils import JsonUtils as ju
from AZbot.plugins.config import cfg

from nonebot import logger

def set_proxy(url: str):
    mode = cfg["base"]["git_proxy"]
    std = Popen(f"git config --{mode} http.proxy", shell=True, stdout=PIPE, stderr=PIPE)
    if not std.returncode:
        out = std.stdout.read().decode("utf-8")
    else:
        out = ""
    if out.__eq__(url):
        return
    else:
        Popen(f"git config --{mode} http.proxy {url}", shell=True, stdout=DEVNULL)

def checkout_branch(
        name: str,
        repo: Repo,
        *args,
        force: bool = False,
        **kwargs):
    if name in repo.heads:
        branchs = [x for x in repo.heads if name in x.name]
        if len(branchs) == 0:
            raise Exception("未找到指定分支")
        branch = branchs[0]
        repo.heads[branch.name].checkout(force=True)
    else:
        repo.create_head(name)
        repo.heads[name].checkout(force=True)

def local_and_remote_ver():
    if os.path.exists("./data/remote"):
        repo = Repo("./data/remote")
        checkout_branch("data", repo, force=True)
        remote = [x for x in repo.remote().repo.heads if "data" in x.name][0]
        return str(next(repo.iter_commits()))[:7], str(next(remote.repo.iter_commits(remote.repo.heads[0].name)))[:7]
    else:
        return None, None

def sync_repo():
    force = cfg["develop"]["force_clone_repo"]
    path = pathlib.Path("./data/remote")
    if path.is_dir() and not force:
        if os.listdir(path) != 0:
            repo = Repo("./data/remote")
            checkout_branch("data", repo, force=True)
            remote = [x for x in repo.remote().repo.heads if "data" in x.name][0]
            try:
                repo.remote().fetch(kill_after_timeout=20)
                # logger.info("数据仓库远端同步完成")
            except Exception as e:
                logger.error(f"同步数据仓库失败: {e}")
                raise e

            (local_ver, remote_ver) = local_and_remote_ver()
            if str(next(repo.iter_commits()))[:7] == str(next(remote.repo.iter_commits(remote.repo.heads[0].name)))[:7]:
                logger.info(f"{local_ver}(local) == {remote_ver}(remote), 数据仓库已是最新版本")
                return None
            else:
                logger.info(f"数据仓库正在更新: {local_ver}(local) -> {remote_ver}(remote)")
                repo.remote().pull()
                logger.info("数据仓库已更新")
                return True

    if force:
        import shutil
        shutil.rmtree("./data/remote", ignore_errors=True)

    logger.info("未检测到数据文件夹, 即将开始克隆数据仓库。若出现下载缓慢的情况，请在config.yml中配置代理")
    try:
        repo = Repo.clone_from("https://github.com/ACGN-Alliance/nonebot-plugin-azurlane-assistant-data", "./data/remote", branch="data", single_branch=True)
        checkout_branch("data", repo, force=True)
        return True
    except Exception as e:
        logger.error(f"克隆数据仓库失败: {e}")
        raise e

def local_file_check():
    data_path_lst = ["data/azurlane", "data/word_bank", "data/bili", "data/equip", "data/server"]
    for path in data_path_lst:
        if not os.path.exists(path):
            os.makedirs(path)

    data_file = [
        "data/group.json",
        "data/user.json",
        "data/cd.json",
        "data/group_cmd.json",
        "data/group_func.json",
        "data/config.json",
        "data/bili/latest.json",
        "data/server/server_status.json",
        "data/server/server_status_user.json"
    ]
    # await ju.init_many_jsons(data_file, init_val=init_val)
    for file in data_file:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write(json.dumps({}))