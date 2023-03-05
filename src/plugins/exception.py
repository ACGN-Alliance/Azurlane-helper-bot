class BotRiskManageException(BaseException):
    def __str__(self):
        return "机器人被风控, 请联系管理员解决"
    
class CanNotSyncException(BaseException):
    def __str__(self):
        return "机器人无法同步数据, 请联系管理员解决"
    
class FunctionNotImplementedException(BaseException):
    def __init__(self, func_name: str):
        self.func_name = func_name

    def __str__(self):
        return f"{self.func_name}功能尚未实现"
    
class DataMeteringException(BaseException):
    def __init__(self, data_name: str):
        self.data_name = data_name

    def __str__(self):
        return f"{self.data_name}数据计量出现错误, 请更新数据"
    
class RemoteFileNotExistsException(BaseException):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def __str__(self):
        return f"{self.file_name}远程文件不存在, 请更新至最新的release"