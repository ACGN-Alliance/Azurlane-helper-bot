import httpx, base64

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
        if(r.status_code != 201): raise Exception("Github API出错")
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

# if __name__ == '__main__':
#     g = GithubHook()
#     import asyncio
#     from sync_list import sync_ls
#     print(asyncio.run(g.sync_data(sync_ls)))