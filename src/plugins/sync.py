import httpx, base64, json, os
from nonebot.log import logger

class GithubHook(object):
    url_prefix = 'https://api.github.com/repos/MRSlouzk/nonebot-plugin-azurlane-assistant-data/'
    data_path = "data/azurlane/"

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
    
    async def sync_data(self, sync_list: list):
        """
        同步数据
        """
        for path in sync_list:
            url = self.url_prefix + 'contents/' + path
            r = httpx.get(url)
            if(r.status_code == 404): raise Exception("未找到文件: " + path)
            elif(r.status_code != 200): raise Exception("Github API出错")
            content = base64.b64decode(r.json()['content'])
            open(self.data_path + path, "w", encoding="utf-8").write(content.decode("utf-8"))

sync_ls = [
    "data/pool.json"
]

async def data_sync():
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
            logger.error("初始化失败, 请删除data/azurlane/data文件夹后重试")
    else:
        logger.info("检测到数据文件夹, 即将进行数据更新")
        try:
            with open(data_path_lst[0] + "git.json", "r", encoding="utf-8") as f:
                lastest_commit = json.loads(f.read())["lastest_commit"]
        except FileNotFoundError:
            lastest_commit = None
        except json.JSONDecodeError:
            logger.error("json文件解析失败, 请删除data/azurlane/data文件夹后重试")
            os._exit(0)

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