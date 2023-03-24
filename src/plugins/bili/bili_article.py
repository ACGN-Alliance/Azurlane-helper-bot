from bilibili_api import user, article
import json

async def bili_article_pic():
    u = user.User(233114659)
    page = await u.get_articles(pn=1, ps=1)
    at_id = page['articles'][0]['id']
    at = article.Article(at_id)
    if at.is_note():
        at = at.turn_to_note()

    await at.fetch_content()
    local_data = json.load(open("data/bili/latest.json", "r", encoding="utf-8"))
    _j = at.json()
    if local_data.get("article_id") is not None and local_data.get("article_id") == _j["meta"]["id"]:
        return None
    else:
        local_data.update({"article_id": _j["meta"]["id"]})
        open("data/bili/latest.json", "w", encoding="utf-8").write(json.dumps(local_data))
    atm = at.markdown()
    atm = atm.split("---")[2]

    from PIL import Image, ImageDraw, ImageFont
    i = Image.new('RGB', (1000, 2000), (255, 255, 255))
    d = ImageDraw.Draw(i)
    fnt = ImageFont.truetype('msyh.ttc', 20)
    d.text((10, 10), atm, font=fnt, fill=(0, 0, 0))
    return [i.tobytes(), at.get_cvid()]
    # i.save('cv.png')

if __name__ == '__main__':
    import asyncio
    asyncio.run(bili_article_pic())