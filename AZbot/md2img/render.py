"""
此文件用于渲染节点化过的 markdown 文件
"""
import os.path
from pathlib import Path
from typing import Tuple
import time
from PIL import Image, ImageDraw, ImageFont

"""
node example
[
    {
        "id": 0,
        "type": "h1",
        "content": "title"
    },
    {
        "id": 1,
        "type": "text",
        "content": "content" 
        "father": [0]
    }
]
"""

font_size_mapping = {
    "title": (30, 0),
    "h1": (48, 0),
    "h2": (42, 2),
    "h3": (36, 5),
    "h4": (30, 7),
    "text": (23, 8),
}

class Render:
    def __init__(self,
                 file: str | Path,
                 node_lst: list,
                 font: str | Path,
                 *args,
                 size: tuple = (600, 800),
                 spacing: float = 0,
                 inline_spacing: float = 0,
                 background: Path | str = None,
                 init_y: float = 0,
                 mode: str = "bili"
                 ):
        """

        :param file: 保存图片路径
        :param node_lst: markdown 节点列表
        :param font: 字体
        :param size: 渲染图片大小
        :param spacing: 行间间距
        :param inline_spacing: 行内间距
        :param text_tab: 正文首行缩进
        :param background: 背景图片
        :param init_y: 初始 y 坐标
        :param mode: 渲染模式
        """
        self.file = file
        self.node_lst_ori = node_lst
        self.node_lst = node_lst.copy()

        if background:
            self.img = Image.open(background)
        else:
            self.img = Image.new("RGB", size, (255, 255, 255))

        self.draw = ImageDraw.Draw(self.img)
        self.font = font

        self.spacing = spacing
        self.inline_spacing = inline_spacing
        self.mode = mode

        self._now_pos_y = init_y  # 当前 y 坐标

    def _plain_text(self,
                    node: dict,
                    font_size: int,
                    *args,
                    tab: float = 0
                    ) -> None:
        def _multiline_text(line: str, font_: ImageFont.FreeTypeFont) -> Tuple[str, int]:
            global size
            x_pos = 0
            line_count = 1
            multi_line = ""

            for char in line:
                size = self.draw.textsize(char, font_)
                if x_pos + size[1] >= self.img.width - 10:
                    multi_line += f"\n{char}"
                    line_count += 1
                    x_pos = 0
                else:
                    x_pos += size[0]
                    multi_line += char

            return multi_line, line_count * size[1] + 2  # 此处可调整段间距

        if not font_size:
            raise NodeStructureException("节点 type 属性错误 => id: %d" % node["id"])
        content = node["content"]
        color = node.get("color", (0, 0, 0))
        font = ImageFont.truetype(self.font, font_size, encoding="unic")

        text, text_height = _multiline_text(content, font)
        text_height += self.spacing

        if self._now_pos_y + text_height > self.img.size[1]:
            new_img = Image.new("RGB", (self.img.size[0], self.img.size[1] + 300), (255, 255, 255))  # 隐藏漏洞: 当下一段文字超过300时会出现问题
            new_img.paste(self.img, (0, 0))
            self.img = new_img
            self.draw = ImageDraw.Draw(self.img)

        self.draw.text((tab, self._now_pos_y), text, font=font, fill=color)
        self._now_pos_y += text_height

    def _render(self,
                node: dict
                ) -> None:
        if not node.get("type"):
            raise NodeStructureException("节点缺少 type 属性 => id: %d" % node["id"])

        mapping_value = font_size_mapping.get(node["type"], None)
        if not mapping_value:
            if node["type"] == "info":
                self.info = node
                if hasattr(node, "title"):
                    self._render({"id": node["id"], "type": "title", "content": node["title"], "color": "red"})
                return
            elif node["type"] == "tag":
                mapping_value = font_size_mapping["text"]
            else:
                raise NodeStructureException("节点 type 属性不存在 => id: %d" % node["id"])

        self._plain_text(node, mapping_value[0], tab=mapping_value[1])

    def _add_frame(self,
                   width: int,
                   color: Tuple[int, int, int],
                   *args,
                   y_pos: Tuple[int, int] = None
                   ):
        """
        为图片添加边框

        :param width: 边框大小
        :param color: 边框颜色
        :param y_pos: 边框y轴上下坐标(底边与图片底部距离, 顶边与图片顶部距离)
        :return:
        """
        img_width, img_height = self.img.size
        if y_pos:
            temp_new_img = Image.new("RGB", (img_width + 2 * width, img_height + y_pos[0] + y_pos[1] + 2 * width), color)
            temp_new_img.paste(self.img, (width, width + y_pos[1]))
        else:
            img_width += 2 * width
            img_height += 2 * width
            temp_width, temp_height = self.img.size
            temp_new_img = Image.new("RGB", (temp_width, temp_height), color)
            temp_new_img.paste(self.img, (width, width))  # 加边框
        self.img = temp_new_img

    def _add_img(
            self,
            image_path: str | Path,
            position: tuple = (0, 0),
            size: tuple = None
    ):
        img = Image.open(image_path)
        img = img.resize(size, Image.ANTIALIAS)

        if size[0] > self.img.width and size[1] > self.img.height:
            raise ValueError("图片尺寸过大")

        if size[0] < img.width and size[1] < img.height:
            img = img.resize(size, Image.ANTIALIAS)

        self.img.paste(img, position, img)

    @staticmethod
    def _time_stamp_to_str(time_stamp_: int) -> str:
        time_stamp_ = int(time_stamp_)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp_))

    def render(self) -> None:
        for node in self.node_lst:
            self._render(node)

        self.img = self.img.crop((0, 0, self.img.size[0], int(self._now_pos_y) + 10))

        if self.mode == "bili":  # 专栏风格样式
            self._add_frame(8, (137, 207, 240), y_pos=(50, 0))
            self._add_img(
                os.path.join(os.getcwd(), "data/remote/image/bili.png"), (0, self.img.height - 54), (88, 42)
            )
            self._add_img(
                os.path.join(os.getcwd(), "data/remote/image/azurlane.png"), (self.img.width - 50, self.img.height - 46), (40, 40)
                          )

            if hasattr(self, "info"):
                font = ImageFont.truetype(self.font, 24, encoding="unic")
                self.draw = ImageDraw.Draw(self.img)  # 此处不知道为什么要重新初始化ImageDraw, 不然无法显示文字
                if hasattr(self.info, "publish_time"):
                    self.draw.text(
                        (100, self.img.height - 46),
                        self._time_stamp_to_str(self.info["publish_time"]),
                        font=font,
                        fill=(0, 0, 255)
                    )
                if hasattr(self.info, "cv"):
                    self.draw.text(
                        (self.img.width - 215, self.img.height - 46),
                        "CV" + self.info["cv"],
                        font=font,
                        fill=(0, 0, 0)
                    )
        elif self.mode == "dynamic":  # 动态风格样式
            self._add_frame(8, (255, 192, 203), y_pos=(50, 0))
            self._add_img(
                os.path.join(os.getcwd(), "data/remote/image/bili.png"), (0, self.img.height - 54), (88, 42)
            )
            self._add_img(
                os.path.join(os.getcwd(), "data/remote/image/azurlane.png"), (self.img.width - 50, self.img.height - 46), (40, 40)
            )

            if hasattr(self, "info"):
                if self.info.get("time", None):
                    font = ImageFont.truetype(self.font, 24, encoding="unic")
                    self.draw = ImageDraw.Draw(self.img)  # 此处不知道为什么要重新初始化ImageDraw, 不然无法显示文字
                    self.draw.text(
                        (100, self.img.height - 46),
                        self._time_stamp_to_str(self.info["time"]),
                        font=font,
                        fill=(0, 0, 255)
                    )
        else:
            pass

        self.img.save(self.file)


class NodeStructureException(BaseException):
    pass
