class BotRiskManageException(Exception):
    def __str__(self):
        return "机器人被风控, 请联系管理员解决"
    
class CanNotSyncException(Exception):
    def __str__(self):
        return "机器人无法同步数据, 请联系管理员解决"
    
class FunctionNotImplementedException(Exception):
    def __init__(self, func_name: str):
        self.func_name = func_name

    def __str__(self):
        return f"{self.func_name}功能尚未实现"
    
class DataMeteringException(Exception):
    def __init__(self, data_name: str):
        self.data_name = data_name

    def __str__(self):
        return f"{self.data_name}数据计量出现错误, 请更新数据"