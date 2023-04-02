class BotRiskManageException(BaseException):
    def __str__(self):
        return f"机器人被风控, 请联系管理员解决{StatusCode('x05')}"
    
class CanNotSyncException(BaseException):
    def __str__(self):
        return "机器人无法同步数据, 请联系管理员解决"
    
class FunctionNotImplementedException(BaseException):
    def __init__(self, func_name: str):
        self.func_name = func_name

    def __str__(self):
        return f"{self.func_name}功能尚未实现{StatusCode('x04')}"
    
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
    
class StatusCode(object):
    wbank = {
        "x00": "A",
        "x01": "成功",
        "x02": "网络访问错误",
        "x03": "路径查找错误",
        "x04": "功能不存在",
        "x05": "消息发送错误",
        "x06": "资源无法读取",
        "x50": "未知错误",
        "x91": "调试性功能"
    }

    def __init__(self, code: str):
        self.code = code

    def __str__(self):
        return f"\n\n状态码: {self.code}, 提示: {self.wbank[self.code]}"