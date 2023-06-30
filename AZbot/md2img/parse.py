from typing import List, Dict
from pathlib import Path
import re

"""
parser example:
[
    {
        "id": 0,
        "type": "h1",
        "content": "title"
    },
    {
        "id": 1,
        "type": "text",
        "content": "content",
        "type": "bold", 
        "father": [0]
    }
]
"""


class MarkDownParser:
    def __init__(self):
        self.node_list = []
        self.multilines_cache = []  # 多行合并(结尾没有两个空格的正文均视作一行)
        self.father = None
        self._stack = []

        self.info_parse = False
        self.info = ""

    def _node(self,
              type_,
              content,
              father=None,
              *args,
              color=None,
              ):
        node = {
            "id": len(self.node_list),
            "type": type_,
            "content": content,
            "father": father
        } if not color else {
            "id": len(self.node_list),
            "type": type_,
            "content": content,
            "father": father,
            "color": color
        }
        return node

    def _info(self):
        def find_kv(key: str):
            regex = rf"^{key}: (.*?)(\\s|$)"
            matches = re.finditer(regex, self.info, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                return match.group().split(": ")[1]

        self.node_list.append({
            "id": -1,
            "type": "info",
            "title": find_kv("title"),
            "publish_time": find_kv("publish_time"),
            "cv": find_kv("id")
        })

    def _parse(self,
               line: str
               ):
        # TODO 父节点处理
        content: str = ""

        if line.startswith("---"):
            if not self._stack:
                self._stack.append("---")
                self.info_parse = True
            else:
                if self._stack[-1] == "---":
                    self._stack.pop()
                    self._info()
                    self.info_parse = False
                    return []

        if self.info_parse:
            self.info += line + "\n"
            return

        if line.startswith("#"):  # 标题 如: # title 或者 #tag#
            if line.endswith("#"):  # 处理标签文本
                return self._node("tag", line, color="blue")

            sign = line.split()[0]
            content = str(line.replace(sign, "").strip())
            if sign.replace("#", ""):
                raise MarkDownParserException("标题格式错误")
            type_ = "h" + str(len(sign))

            return self._node(type_, content)

        else:
            # if not line.endswith("  "):  # 结尾两个空格的正文
            #     self.multilines_cache.append(line)
            #     return []

            if self.multilines_cache:  # 多行缓存与合并
                self.multilines_cache.append(line)
                content = "".join(self.multilines_cache)
                self.multilines_cache.clear()
            else:
                content = line

            type_ = "text"

            return self._node(type_, content)

    def parse(self, file: Path | str) -> List[Dict]:
        lines = open(file, "r", encoding="utf-8").readlines()
        for line in lines:
            if line != "\n":
                line = line.replace("\n", "")
                line = line.replace("\r", "")
                node = self._parse(line)
                if node:
                    self.node_list.append(node)
                else:
                    continue

        return self.node_list

    def parse_plain_text(self,
                         text: str,
                         *args,
                         time=None) -> List[dict]:
        lines = text.split("\n")
        for line in lines:
            if line and line != "\r":
                line = line.replace("\r", "")
                node = self._parse(line)
                if node:
                    self.node_list.append(node)

        self.node_list.append({
            "id": -1,
            "type": "info",
            "time": time
        })

        return self.node_list

class MarkDownParserException(BaseException):
    pass
