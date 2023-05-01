"""
A CSS-like image rendering lib depended to PIL
Allow you to build some beautiful images by several lines.
MIT licence @copyright (一块蒙脱石)[https://GitHub.com/montmorill] 2023
WARNING: THIS IS A DEVELOPING WORK.
"""

__all__ = [
    "Border",
    "Frame",
    "Text",
    "noise",
    "image",
    "border"
]
__version__ = (0, 0, 1)
__author__ = "一块蒙脱石"


from typing import TypeAlias, Literal, Union, Optional, Self, overload
from io import BytesIO
import random

import requests
from PIL import Image, ImageDraw, ImageFont


T_Path: TypeAlias = str | bytes   # a path or path-like
Color: TypeAlias = (            # see: https://drafts.CSSwg.org/CSS-color-4/
    str |                       # named-colors, see: CSS-color-4/#named-colors
    tuple[int, int, int] |      # r(ed), g(reen), b(lue)
    tuple[int, int, int, int]   # r(ed), g(reen), b(lue), a(lpha)
)
T_Border: TypeAlias = (             # allowed border types
    int |                           # all borders
    tuple[int, int] |               # top and bottom, right and left
    tuple[int, int, int] |          # top, right and left, bottom
    tuple[int, int, int, int] |     # top, right, bottom, left
    "Border"                        # a `Border`
)
T_Image: TypeAlias = T_Path | Image.Image | bytes   # allowed image types


FONT = "font.ttf"                   # default font file
TRANSPARENT: Color = (0, 0, 0, 0)   # transparent


class Ink:
    def __init__(
        self,
        func: str,
        args: tuple
    ) -> None:
        self.func = func
        self.args = args


class Child:
    def __init__(
        self,
        frame: "Frame",
        xy: Optional[tuple[int, int]] = None,
        size: Optional[tuple[int, int]] = None
    ) -> None:
        self.frame = frame
        self.xy = xy
        self.size = size


class Border:
    @overload
    def __init__(
        self,
        **kwargs
    ) -> None: ...

    @overload
    def __init__(
        self,
        all_: int,
        **kwargs
    ) -> None: ...

    @overload
    def __init__(
        self,
        top_and_bottom: int,
        left_and_right: int,
        **kwargs
    ) -> None: ...

    @overload
    def __init__(
        self,
        top: int,
        left_and_right: int,
        bottom: int,
        **kwargs
    ) -> None: ...

    @overload
    def __init__(
        self,
        top: int,
        right: int,
        bottom: int,
        left: int,
        **kwargs
    ): ...

    def __init__(self, *args, **kwargs) -> None:    # see: `T_Border`
        match len(args):
            case 0:
                self.top = self.right = self.bottom = self.left = 0
            case 1:
                self.top = self.right = self.bottom = self.left = args[0]
            case 2:
                self.top = self.bottom = args[0]
                self.right = self.left = args[1]
            case 3:
                self.top, self.left, self.bottom = args
                self.right = self.left
            case 4:
                self.top, self.right, self.bottom, self.left = args

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.height = self.top + self.bottom
        self.width = self.left + self.right
        self.xy = self.left, self.top


class Frame:
    def __init__(
        self,
        *,
        width: int = 0,         # frame's width and height,
        height: int = 0,        # excluding margin, including padding
        padding: T_Border = 0,  # frame's padding and margin,
        margin: T_Border = 0,   # see: https://drafts.CSSwg.org/CSS-frame-3/
        background: Color | T_Image = TRANSPARENT
        # a pure color or image, default to `TRANSPARENT`
    ) -> None:
        self.padding = border(padding)
        self.margin = border(margin)
        self.width = width + self.padding.width
        self.height = height + self.padding.height
        self.background = background
        self.children: list[Ink | Child] = []
        self.__margin = 0                   # used for self.append()

    def draw(self, func: str, *args):
        self.children.append(Ink(func, args))

    def append(
        self,
        child: Union["Frame", T_Image],
        xy: Optional[tuple[int, int]] = None,
        size: Optional[tuple[int, int]] = None
    ) -> Self:
        if not isinstance(child, Frame):
            child = image(child)
            child = Frame(                  # trun `PIL.Image.Image` to `Frame`
                width=child.width,
                height=child.height,
                background=child
            )
        self.children.append(Child(child, xy, size))
        if xy is None:                      # append along the y-axis
            self.width = max(
                self.width,
                self.padding.width          # padding
                + child.margin.width        # child's margin
                + child.width               # child's width
            )
            self.height += (
                max(0, child.margin.top - self.__margin)    # top margin
                + child.height                              # child's height
                + child.margin.bottom                       # bottom margin
            )
            self.__margin = child.margin.bottom
        return self                         # use for chain calls

    @property
    def im(self) -> Image.Image:
        if isinstance(self.background, T_Image):
            im = Image.new("RGBA", (self.width, self.height), TRANSPARENT)
            im.alpha_composite(image(self.background), self.padding.xy)
        else:
            im = Image.new("RGBA", (self.width, self.height), self.background)
        draw = ImageDraw.Draw(im)

        x, y = self.padding.left, self.padding.top
        margin = 0
        for child in self.children:
            if isinstance(child, Ink):
                getattr(draw, child.func)(*child.args)
            elif isinstance(child, Child):
                frame = child.frame
                xy = child.xy
                size = child.size
                img = frame.im                  # im
                if size is not None:            # resize
                    img = img.resize(size)
                if xy is None:
                    y += max(margin, frame.margin.top)
                    im.alpha_composite(img, (x + frame.margin.left, y))
                    margin = frame.margin.bottom
                    y += img.height
                else:
                    im.alpha_composite(img, xy)
        return im


class Text(Frame):
    def __init__(
        self,
        *,
        text: str,                      # content
        font_size: int = 20,            # font size
        color: Color = "black",         # text color
        align: Literal["left", "center", "right"] = "left",     # text align
        line_padding: int = 0,          # line padding
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.font = ImageFont.truetype(FONT, font_size)
        self.color = color
        self.line_padding = line_padding
        self.align = align
        self.line_height = self.font.getsize(self.text)[1]
        self.lines = self.text.split("\n")

        if kwargs.get("width", 0) == 0:
            self.width = (
                int(max(map(self.font.getlength, self.lines)))  # max width
                + self.padding.width
            )
        else:
            new_lines = []
            for line in self.lines:
                x = self.padding.left
                y = self.padding.right
                new_line = ""
                for char in line:
                    if x + self.font.getlength(char) > self.width:  # line feed
                        new_lines.append(new_line)
                        new_line = ""
                        x = self.padding.left
                        y += self.line_height + self.line_padding
                    new_line = "".join([new_line, char])    # new_line += char
                    x += self.font.getlength(char)
                new_lines.append(new_line)
            self.lines = new_lines

        self.line_count = len(self.lines)
        self.height = (
            self.padding.height
            + self.line_count * (self.line_height+self.line_padding)
            - self.line_padding
        )

    @property
    def im(self) -> Image.Image:
        im = super().im
        draw = ImageDraw.Draw(im)
        for n,  line in enumerate(self.lines):
            x = self.padding.left
            y = self.padding.top + n * (self.line_padding+self.line_height)
            """
            x += (self.width-self.font.getlength(line)) * {
                "left": 0,          # left
                "center": 0.5,      # center
                "right": 1          # right
            }[self.align]
            """
            # These are pure shit codes, so I changed them to the following...
            x += (self.width-self.font.getlength(line)) * (
                lambda x: 31/4*x - 3/4*x*x - 19    # awesome!!!
            )(len(self.align))
            draw.text((x, y), line, self.color, self.font)
        return im


def noise(im: T_Image, noise: int = 5) -> Image.Image:
    im = image(im).copy()
    for _ in range(noise):
        x = random.randint(0, im.width - 1)
        y = random.randint(0, im.height - 1)
        im.putpixel((x, y), "114514")               # 哼啊啊啊啊啊啊啊啊
    return im


def image(im: T_Image) -> Image.Image:
    if isinstance(im, Image.Image):
        return im
    try:
        return Image.open(im)
    except:
        io = BytesIO()
        if isinstance(im, str):
            im = im.encode()
        io.write(
            requests.get(im).content
            if im.startswith(b"http")
            else im
        )
        return Image.open(io)


def border(padding: T_Border) -> Border:
    if isinstance(padding, Border):
        return padding
    if isinstance(padding, tuple):
        return Border(*padding)
    return Border(padding)
