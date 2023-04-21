import httpx, base64, json, os
from nonebot.log import logger
from nonebot import get_driver

from src.plugins.exception import RemoteFileNotExistsException
from src.plugins.config import cfg
from src.plugins.json_utils import JsonUtils as ju

driver = get_driver()

class GithubHook(object):
    if(cfg["base"]["download_source"] == "github"):
        # url_prefix = 'https://api.github.com/repos/MRSlouzk/nonebot-plugin-azurlane-assistant-data/'
        url_prefix = 'https://api.github.com/repositories/578098474/'
    elif(cfg["base"]["download_source"] == "gitee"):
        url_prefix = 'https://gitee.com/mrslouzk/nonebot-plugin-azurlane-assistant-data/'
    elif(cfg["base"]["download_source"] == "jsdelivr"):
        url_prefix = 'https://cdn.jsdelivr.net/gh/ACGN-Alliance/nonebot-plugin-azurlane-assistant-data/'
    else:
        url_prefix = 'https://api.github.com/repositories/578098474/'
        
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
        if(cfg["base"]["network_proxy"]): r = httpx.get(url, proxies=cfg["base"]["network_proxy"])
        else: r = httpx.get(url)
        if(r.status_code == 403): raise Exception("检测更新时Github API请求过于频繁")
        # logger.error(f"检测更新时状态码:{r.status_code}")
        if(not(r.status_code == 200 or r.status_code == 301)): raise Exception("检测更新时Github API出错")
        return r.json()[0]['sha']
    
    async def sync_data(self, sync_list: list, _path: str = ""):
        """
        同步数据

        """
        for path in sync_list:
            url = self.url_prefix + 'contents/' + path
            r = None
            try:
                if(cfg["base"]["network_proxy"]): r = httpx.get(url, proxies=cfg["base"]["network_proxy"])
                else: r = httpx.get(url)
            except Exception as e:
                raise Exception(f"Github API请求失败, 错误原因:{e}")
            if(r is not None):
                logger.info("状态码："+str(r.status_code))
                if(r.status_code == 404): raise RemoteFileNotExistsException(path)
                elif(r.status_code != 200): raise Exception("Github API出错")
                content = base64.b64decode(r.json()['content'])
                open(self.root_path + _path + path, "w", encoding="utf-8").write(content.decode("utf-8"))

async def data_sync():
    is_need_inited = False
    data_path_lst = ["data/azurlane", "data/word_bank", "data/bili"]
    for path in data_path_lst:
        if not os.path.exists(path):
            os.makedirs(path)
            is_need_inited = True

    data_file = [
                "data/group.json",
                "data/user.json",
                "data/group_cmd.json", 
                "data/group_func.json", 
                "data/config.json", 
                "data/bili/latest.json"
                ]
    init_val = [
        {},
        {
            "global":[]
        }
    ]
    await ju.init_many_jsons(data_file, init_val = init_val)
    for file in data_file:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write(json.dumps({}))

    # TODO 初始化加载所有功能数据

    g = GithubHook()
    try:
        await g.sync_data(["sync.json"], _path="")
    except Exception as e:
        logger.error(str(e) + "===获取同步列表失败, 已终止数据同步")
        return False

    if is_need_inited:
        logger.warning("未检测到数据文件夹, 即将进入初始化")
        try: 
            sync = json.load(open("data/sync.json", "r", encoding="utf-8"))
            await g.sync_data(sync["default"])
            with open("data/git.json", "w", encoding="utf-8") as f:
                f.write(json.dumps({"lastest_commit": await g.get_lastest_commit()}))
            logger.info("初始化完成")
        except RemoteFileNotExistsException as e:
            logger.error(e)
            return False
        except Exception as e:
            logger.error(str(e) + "\n初始化失败, 请删除data文件夹后重试")
            return False
    else:
        logger.info("检测到数据文件夹, 即将进行数据更新")
        local_commit = None
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
            logger.error(str(e) + "\n获取最新commit失败")
            return False
        
        if local_commit != lastest_commit:
            try: 
                sync = json.load(open("data/sync.json", "r", encoding="utf-8"))
                await g.sync_data(sync["default"])
                with open("data/git.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps({"lastest_commit": lastest_commit}))
                logger.info("数据更新完成")
            except RemoteFileNotExistsException as e:
                logger.error(e)
                return False
            except Exception as e:
                logger.error(str(e) + "\n数据更新失败, 请重试")
                return False
        else:
            logger.info("数据无需更新")

    return True