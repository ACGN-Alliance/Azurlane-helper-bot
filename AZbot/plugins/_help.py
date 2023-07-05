#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : mrslouzk
@Date           : 2023/6/25
@LastEditors    : mrslouzk
@LastEditTime   : 2023/6/25
@Description    : 帮助命令
@GitHub         : https://github.com/MRSlouzk
"""

# TODO will be added in the future

# from nonebot.matcher import matchers
# from nonebot import on_command
# from nonebot.params import CommandArg
# from nonebot.matcher import Matcher
# from nonebot.adapters.onebot.v11 import Message, MessageEvent
#
# all_matcher_name = []
# for matcher in matchers:
#     if not matcher.__doc__:
#         continue
#     all_matcher_name.append(dict(zip(matcher.state["_prefix"]["command"][0], matcher.__doc__)))
#
# manager = on_command("help", aliases={"帮助"})
# manager.__doc__ = """使用方法：
# %help [命令]
# """
# @manager.handle()
# async def _(arg: Message = CommandArg()):
#     args = arg.extract_plain_text().split()
#     if not args:
#         await manager.finish(manager.__doc__)
#     elif len(args) == 1:
#         if args[0] not in all_matcher_name:
#             await manager.finish("没有这个命令")
#         await manager.finish(all_matcher_name[args[0]])
#     else:
#         await manager.finish(manager.__doc__)