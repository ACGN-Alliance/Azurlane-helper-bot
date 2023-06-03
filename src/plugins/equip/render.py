from src.render import Frame, Text, Border
from src.plugins.config import cfg
import os

data_dir = "data/azurlane/equip/"
if not cfg["func"]["equip_tmp_dir"]:
    tmp_dir = data_dir + "tmp/"
else:
    tmp_dir = cfg["func"]["equip_tmp_dir"]
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)

IMAGE_PATH = cfg["func"]["image_path"]

suit_types = [
    "驱逐",
    "轻巡",
    "重巡",
    "超巡",
    "战巡",

    "战列",
    "轻航",
    "航母",
    "航战",
    "潜母",

    "重炮",
    "潜艇",
    "维修",
    "运输",
    "风帆"
]


def get_nodes(data: dict, depth: int = 0):
    nodes = []
    for key, value in data.items():
        if isinstance(value, dict):
            nodes.append((depth, key, None))
            nodes.extend(get_nodes(value, depth + 1))
        else:
            nodes.append((depth, key, value))
    return nodes


class Attr(Frame):
    def __init__(self, data: dict, width: int, tab: int) -> None:
        super().__init__(
            width=width
        )

        for depth, key, content in get_nodes(data["attrs"]):
            frame = Frame(
                width=556 - depth*tab,
                margin=Border(10, left=10 + depth*tab),
                padding=Border(bottom=5),
                background=(67, 67, 67)
            )
            key = Text(
                text=key,
                color="white",
                margin=(4, 7)
            )
            frame.append(key)
            if content is not None:
                frame.append(Text(
                    text=content,
                    color="yellow",
                    width=frame.width - frame.padding.width - 14,
                    margin=(4, 7)
                ) if key.text == "描述" else Text(
                    text=content,
                    color="yellow",
                    align="right",
                    width=frame.width - key.width - key.margin.width,
                    margin=(4, 7)
                ), (7 + key.width, 4))
            self.append(frame)


class EquipAttr(Frame):
    def __init__(self, data: dict):
        super().__init__(
            width=576,
            background=(132, 132, 132)
        )
        # title
        self.append(Text(
            text=data["name"],
            font_size=30,
            color="white",
            align="center",
            width=self.width,
            padding=(3, 0, 10),
            background=(67, 67, 67)
        ))
        # rarity
        self.append(f"{IMAGE_PATH}/icon/equip/level_{data['rarity'] + 1}.png")
        # icon
        self.append(
            f"{IMAGE_PATH}/equip/{data['name'].replace('/', '_')}.png",
            ((self.width - 128) // 2, self.height - 175), (128, 128)
        )
        # level
        self.append(
            f"{IMAGE_PATH}/icon/equip/{data['level']}.png",
            (512, self.height - 196), (32, 45)
        )
        # type
        self.draw(
            "rectangle", (20, self.height - 45, 120, self.height - 15),
            "blue" if data["type"] in ["设备", "货物", "唯一设备"] else "red"
        )
        self.append(type := Text(
            text=data["type"],
            font_size=20,
            color="white",
            align="center",
            width=100
        ), (20 + (100 - type.width) // 2, self.height - 45))
        # attrs
        self.append(Attr(
            data=data,
            width=self.width,
            tab=15
        ))
        # use
        use = Frame(
            padding=Border(5),
            margin=Border(10, top=0),
            background=(52, 52, 52)
        ).append(F"{IMAGE_PATH}/icon/equip/use.png")
        for suit_type in data["suit_type"]:
            n = suit_types.index(suit_type)
            use.append(
                f"{IMAGE_PATH}/icon/equip/use_{n+1}.png",
                ((n % 5)*104 + 32, (n // 5)*48 + 14)
            )
        self.append(use)
