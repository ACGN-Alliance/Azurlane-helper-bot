from bilibili_api import user, article
import json, os

from AZbot.md2img import trans_img, trans_plain_text

async def bili_pic(force_push: bool = False):
    # TODO 图片插入
    u = user.User(233114659)
    page = await u.get_dynamics(0)
    latest_dynamic = page[0]["card"]
    if not force_push:  # 检查是否已经推送过
        local_data = json.load(open("data/bili/latest.json", "r", encoding="utf-8"))
        now_data = latest_dynamic.json()
        if local_data:
            if local_data["desc"]["dynamic_id"] == now_data["desc"]["dynamic_id"]:
                return None

        json.dump(now_data, open("data/bili/latest.json", "w", encoding="utf-8"), ensure_ascii=False)

    if hasattr(latest_dynamic, "id"):  # 专栏
        page_article = article.Article(latest_dynamic["id"])
        if page_article.is_note():
            page_article = page_article.turn_to_note()
        await page_article.fetch_content()
        md = page_article.markdown()

        trans_img(md, "data/bili_temp.png", "msyh.ttc", spacing=10)

        # 返回绝对路径
        return os.path.abspath("data/bili_temp.png")

    elif hasattr(latest_dynamic, "origin"):  # 动态转发
        pass

    elif hasattr(latest_dynamic, "aid"):  # 视频
        pass

    else:  # 动态
        content = latest_dynamic["item"]["description"]
        trans_plain_text(content, "data/bili_temp.png", "msyh.ttc", spacing=10)

        return os.path.abspath("data/bili_temp.png")