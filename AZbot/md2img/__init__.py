from .parse import MarkDownParser as mdp
from .render import Render

from pathlib import Path


def trans_img(markdown_file: str | Path,
              output_file: str | Path,
              font_file: str | Path,
              *args,
              spacing: float = 0,
              inline_spacing: float = 0,
              backgroud: str | Path = None
              ) -> None:
    """
    将markdown文件转换为图片

    :param markdown_file: markdown文件路径
    :param output_file: 输出图片路径
    :param font_file: 字体文件路径
    :param spacing: 行间间距
    :param inline_spacing: 行内间距
    :param backgroud: 背景图片路径
    :return:
    """
    md = mdp()
    node_lst = md.parse(markdown_file)
    r = Render(
        output_file,
        node_lst,
        font_file,
        spacing=spacing,
        inline_spacing=inline_spacing,
        background=backgroud,
        size=(1000, 1000)
    )
    r.render()


def trans_plain_text(text: str,
                     output_file: str | Path,
                     font_file: str | Path,
                     *args,
                     spacing: float = 0,
                     inline_spacing: float = 0,
                     backgroud: str | Path = None,
                     time: int = None
                     ) -> None:
    """
    将纯文本转换为图片

    :param text: 文本
    :param output_file: 输出图片路径
    :param font_file: 字体文件路径
    :param spacing: 行间间距
    :param inline_spacing: 行内间距
    :param backgroud: 背景图片路径
    :param time: 时间戳
    :return:
    """
    md = mdp()
    node_lst = md.parse_plain_text(text, time=time)
    r = Render(
        output_file,
        node_lst,
        font_file,
        spacing=spacing,
        inline_spacing=inline_spacing,
        background=backgroud,
        size=(1000, 1000),
        mode="dynamic"
    )
    r.render()
