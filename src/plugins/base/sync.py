import httpx, base64, json, os
from nonebot.log import logger
from nonebot import get_driver

from src.plugins.exception import RemoteFileNotExistsException

driver = get_driver()

class GithubHook(object):
    if(driver.config.download_source == "github"):
        url_prefix = 'https://api.github.com/repos/MRSlouzk/nonebot-plugin-azurlane-assistant-data/'
    elif(driver.config.download_source == "gitee"):
        url_prefix = 'https://gitee.com/mrslouzk/nonebot-plugin-azurlane-assistant-data/'
    else:
        url_prefix = 'https://api.github.com/repos/MRSlouzk/nonebot-plugin-azurlane-assistant-data/'
        
    root_path = "data/"

    def __init__(self):
        pass

    async def get_lastest_commit(
            self
            ) -> str:
        """
        获取最新的commit的SHA值

        """
        url = self.url_prefix + 'commits'
        r = httpx.get(url)
        if(r.status_code == 403): raise Exception("Github API请求过于频繁")
        if(r.status_code != 200): raise Exception("Github API出错")
        return r.json()[0]['sha']
    
    async def sync_data(self, sync_list: list, _path: str = ""):
        """
        同步数据

        """
        for path in sync_list:
            url = self.url_prefix + 'contents/' + path
            try:
                if(driver.config.PROXY): httpx.get(url, proxies=driver.config.PROXY)
                else: r = httpx.get(url)
            except Exception as e:
                raise Exception("Github API请求失败, 请检查代理设置")
            if(r.status_code == 404): raise RemoteFileNotExistsException(path)
            elif(r.status_code != 200): raise Exception("Github API出错")
            content = base64.b64decode(r.json()['content'])
            open(self.root_path + _path + path, "w", encoding="utf-8").write(content.decode("utf-8"))

async def data_sync():
    is_need_inited = False
    data_path_lst = ["data/azurlane/", "data/word_bank"]
    for path in data_path_lst:
        if not os.path.exists(path):
            os.makedirs(path)
            is_need_inited = True

    data_file = ["data/group.json", "data/user.json", "data/group_cmd.json", "data/group_func.json", "data/bili/latest.json"]
    for file in data_file:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write(json.dumps({}))

    g = GithubHook()
    try:
        data = await g.sync_data(["sync.json"], _path="")
        with open("data/sync.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data))
    except Exception as e:
        logger.error(e + "\n获取同步列表失败, 已终止数据同步")
        return False

    if is_need_inited:
        logger.warning("未检测到数据文件夹, 即将进入初始化")
        try: 
            sync = json.load(open("data/sync.json", "r", encoding="utf-8").read())
            await g.sync_data(sync["default"])
            with open("data/git.json", "w", encoding="utf-8") as f:
                f.write(json.dumps({"lastest_commit": await g.get_lastest_commit()}))
            logger.info("初始化完成")
        except RemoteFileNotExistsException as e:
            logger.error(e)
            return False
        except Exception as e:
            logger.error(e + "\n初始化失败, 请删除data文件夹后重试")
            return False
    else:
        logger.info("检测到数据文件夹, 即将进行数据更新")
        try:
            with open("data/git.json", "r", encoding="utf-8") as f:
                local_commit = json.loads(f.read())["lastest_commit"]
        except FileNotFoundError:
            lastest_commit = None
        except json.JSONDecodeError:
            logger.error("json文件解析失败, 请删除data文件夹后重试")
            return False

        try:
            lastest_commit = await g.get_lastest_commit()
            info = f"最新commit: {lastest_commit}, 本地commit: {local_commit}"
            if(local_commit != lastest_commit):
                info += " (数据需要更新)"
            logger.info(info)
        except Exception as e:
            logger.error(e + "\n获取最新commit失败")
            return False
        
        if local_commit != lastest_commit:
            try: 
                await g.sync_data(sync["default"])
                with open("data/git.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps({"lastest_commit": lastest_commit}))
                logger.info("数据更新完成")
            except RemoteFileNotExistsException as e:
                logger.error(e)
                return False
            except Exception as e:
                logger.error(e + "\n数据更新失败, 请重试")
                return False
        else:
            logger.info("数据无需更新")

    return True