from nonebot.adapters.onebot.v11 import Message

__version__ = "0.0.1-dev"

black_list = Message(Message("黑名单功能: \n")
+ Message("1. 添加黑名单[SU]: /黑名单 添加 [群/人] 号码 *功能名\n")
+ Message("2. 删除黑名单[SU]: /黑名单 删除 [群/人] 号码 *功能名\n")
+ Message("3. 清空黑名单[SU]: /黑名单 清空\n")
+ Message("4. 是否在黑名单: /黑名单 查询 [群/人] 号码 *功能名\n"))