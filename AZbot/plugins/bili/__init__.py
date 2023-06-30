import os.path

from nonebot import on_command

from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    GROUP_ADMIN,
    GROUP_OWNER,
    MessageSegment
)
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.exception import ActionFailed

from AZbot.plugins.checker.rule_check import event_handle
from AZbot.plugins.json_utils import JsonUtils as ju
from .bili_article import bili_pic

bili_sub = on_command("bili订阅", rule=event_handle, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)


@bili_sub.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().split()
    if len(args) == 0:
        await bili_sub.finish("用法: bili订阅 开启|关闭")
    elif len(args) == 1:
        lst: list = await ju.get_val("data/group_func.json", "bili")
        if_on = event.group_id in lst if lst else False
        if args[0] == "开启":
            if if_on:
                await bili_sub.finish("本群已启用bili订阅")
            await ju.update_val("data/group_func.json", "bili", lst.append(event.group_id))
            await bili_sub.finish("开启成功")
        elif args[0] == "关闭":
            if not if_on:
                await bili_sub.finish("本群未启用bili订阅")
            await ju.update_val("data/group_func.json", "bili", lst.remove(event.group_id))
            await bili_sub.finish("关闭成功")
        elif args[0] == "推送":
            await bili_pic(force_push=True)
            file_path = "file:///" + os.path.join(os.getcwd(), "data/bili/bili_temp.png")
            try:
                print(file_path)
                await bili_sub.finish(MessageSegment.image(file_path))
            except ActionFailed as e:
                await bili_sub.finish(f"推送失败, 原因: {str(e)}")
    else:
        await bili_sub.finish("用法: bili订阅 开启|关闭")
