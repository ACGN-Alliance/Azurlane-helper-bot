from bilibili_api import user, article
import json, os

from AZbot.md2img import trans_img, trans_plain_text

async def bili_pic(force_push: bool = False):
    # TODO 图片插入
    u = user.User(233114659)
    page = await u.get_dynamics(0)
    latest_dynamic = page["cards"][0]["card"]
    all_info = page["cards"][0]
    if not force_push:  # 检查是否已经推送过
        local_data = json.load(open("data/bili/latest.json", "r", encoding="utf-8"))
        if local_data:
            if local_data["desc"]["dynamic_id"] == all_info["desc"]["dynamic_id"]:
                return None

        json.dump(all_info, open("data/bili/latest.json", "w", encoding="utf-8"), ensure_ascii=False)

    if hasattr(latest_dynamic, "id"):  # 专栏
        page_article = article.Article(latest_dynamic["id"])
        if page_article.is_note():
            page_article = page_article.turn_to_note()
        await page_article.fetch_content()
        md = page_article.markdown()

        trans_img(md,
                  os.path.join(os.getcwd(), "data/bili/bili_temp.png"),
                  os.path.join(os.getcwd(), "AZbot/plugins/bili/msyh.ttc"),
                  spacing=10)

        return True

    elif hasattr(latest_dynamic, "origin"):  # 动态转发
        pass

    elif hasattr(latest_dynamic, "aid"):  # 视频
        pass

    else:  # 动态
        content = latest_dynamic["item"]["description"]
        trans_plain_text(content,
                         os.path.join(os.getcwd(), "data/bili/bili_temp.png"),
                         os.path.join(os.getcwd(), "AZbot/plugins/bili/msyh.ttc"),
                         spacing=10,
                         time=latest_dynamic["item"]["upload_time"])

        return True