import random
from typing import List

from AZbot.plugins.exception import DataMeteringException
from AZbot.plugins.json_utils import JsonUtils as ju
from AZbot.plugins._error import report_error


async def build_simulator(
        pool_type: str = "qx",
        num: int = 1
) -> List[dict]:
    """
    抽取建造池内容
    
    :param pool_type: 建造池类型:qx, zx, tx, xd
    :param num: 抽取次数
    """

    async def get_icon(name: str):
        # data = json.load(open("data/azurelane/ship.json", "r", encoding="utf-8"))
        data = await ju.get_val("data/remote/azurlane/ship.json", [])
        assert data is not None
        for ship in data["data"]:
            if ship["name"] == name:
                return ship["remote_icon_path"]

    # data = json.load(open("data/azurelane/data/pool.json", "r", encoding="utf-8"))
    data = await ju.get_val("data/remote/azurlane/pool.json", [])
    assert data is not None
    result_lst = []

    if pool_type != "xd":
        ship_data = data[pool_type]
        probability = data["data"][pool_type]
        for _ in range(num):
            rnd = random.random()
            res_prob = ""
            for prob in probability.keys():
                rnd -= probability[prob]
                if rnd <= 0:
                    res_prob = prob
                    break
            ship = random.choice(ship_data[res_prob])
            result_lst.append({
                "ship": ship,
                "probability": res_prob,
                "img_url": await get_icon(ship)
            })
    else:
        xd_lst = {
            "ssr": [],
            "sr": [],
            "r": [],
            "n": []
        }
        is_selected = False

        for k in data.keys():
            if (k != "data"):
                xd_lst["ssr"] += data[k]["ssr"]
                xd_lst["sr"] += data[k]["sr"]
                xd_lst["r"] += data[k]["r"]
                xd_lst["n"] += data[k]["n"]

        for _ in range(num):
            rnd = random.random()
            # UP角色
            for k in data["xd"].keys():
                rnd -= data["xd"][k]["rate"]
                if rnd <= 0:
                    result_lst.append({
                        "ship": data["xd"][k]["name"],
                        "probability": data["xd"][k]["rarity"],
                        "img_url": await get_icon(data["xd"][k]["name"])
                    })
                    is_selected = True
                    break

            if not is_selected:
                # 普通角色
                for v in data["data"]["xd"].keys():
                    rnd -= data["data"]["xd"][v]
                    if rnd <= 0:
                        name = random.choice(xd_lst[v])
                        result_lst.append({
                            "ship": name,
                            "probability": v,
                            "img_url": await get_icon(name)
                        })
                        is_selected = True
                        break

            if not is_selected:
                raise DataMeteringException("建造池")

    return result_lst
