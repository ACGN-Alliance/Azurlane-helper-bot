import json, os
from typing import List, Any
from pathlib import Path

class JsonUtils:
    path_prefix = ""
    enable_ascii = False
    indent = 4
    encode = "utf-8"

    @staticmethod
    def get_next_floor(raw, key: int | str):
        try:
            if(isinstance(key, int)):
                return raw[key]
            else:
                return raw.get(key)
        except AttributeError:
            raise Exception(f"{raw}下一层级不是字典，无法获取键{key}")
        except KeyError:
            raise Exception(f"{raw}下一层级不是列表，无法获取索引{key}")
        except IndexError:
            raise Exception(f"{raw}下一层级索引{key}超出范围，最大索引为{len(raw) - 1}")

    @classmethod
    async def get_val(
                            cls,
                            file_path: str | Path,
                            key_path: List[str | int] | str | int,
                            *args,
                            filter: List[str | int] = []
                            ) -> Any | None:
        """
        读取Json文件并获取值

        :param file_path: 文件路径
        :param key_path: 键路径
        :param filter: 过滤器 # TODO 待添加功能
        :return: 值
        """
        if not os.path.exists(file_path):
            await cls.init_json(file_path)
            return None

        if(isinstance(key_path, (str, int))):
            key_path = [key_path]

        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        temp_next_val = None
        is_first = True
        deepth = 2

        if(len(key_path) == 0):
            return raw
        
        for key in key_path:
            if(is_first):
                val = cls.get_next_floor(raw, key)
                if(val is None):
                    return None
                else:
                    if(len(key_path) == 1):
                        return val
                    else:
                        temp_next_val = val
                        is_first = False
                        continue
            else:
                val = cls.get_next_floor(temp_next_val, key)
                if(val is None):
                    return None
                else:
                    if(len(key_path) == deepth):
                        return val
                    else:
                        temp_next_val = val
                        deepth += 1
                        continue
    
    @classmethod
    async def get_many_vals(
                                cls,
                                file_path: List[str | Path],
                                key_paths: List[List[str|int] | str | int]
                                ) -> List[Any] | Exception | None:
        """
        读取Json文件并获取多个值

        :param file_path: 文件路径
        :param key_paths: 键路径列表
        :return: 值列表
        """
        vals = []
        index = 0
        for key_path in key_paths:
            val = await cls.get_val(file_path[index], key_path)
            index += 1
            vals.append(val)
        return vals

    @classmethod
    async def update_whole_file(
                                cls,
                                file_path: str | Path,
                                value: Any
                                ) -> bool | Exception | None:
        """
        更新Json文件

        :param file_path: 文件路径
        :param value: 值
        :return: 是否成功
        """
        if not os.path.exists(file_path):
            await cls.init_json(file_path)

        with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
            f.write(json.dumps(value, ensure_ascii=cls.enable_ascii, indent=cls.indent))
        return True

    @classmethod
    async def update_val(
                        cls,
                        file_path: str | Path,
                        key_path: List[str|int] | str | int,
                        value: Any
                        ) -> bool | Exception | None:
        """
        更新Json文件中的值

        :param file_path: 文件路径
        :param key_path: 键路径
        :param value: 值
        :return: 是否成功
        """
        if not os.path.exists(file_path):
            await cls.init_json(file_path)

        if(isinstance(key_path, (str, int))):
            key_path = [key_path]
        
        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        global temp_next_val
        is_first = True
        deepth = 2

        if(len(key_path) == 0):
            json.dump(value, open(cls.path_prefix + str(file_path), "w", encoding=cls.encode))

        for key in key_path:
            if(is_first):
                val = cls.get_next_floor(raw, key)
                if(len(key_path) == 1):
                    raw[key] = value
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                    return True
                else:
                    temp_next_val = val
                    is_first = False
                    continue
            else:
                if(len(key_path) == deepth):
                    temp_next_val.update({key: value})
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                    return True
                else:
                    val = cls.get_next_floor(temp_next_val, key)
                    if(val is None):
                        return False
                    temp_next_val = val
                    deepth += 1
                    continue

    @classmethod
    async def update_many_vals(
                            cls,
                            file_path: List[str | Path],
                            key_paths: List[List[str|int] | str | int],
                            values: List[Any]
                            ) -> bool | Exception | None:
        """
        更新Json文件中的多个值

        :param file_path: 文件路径
        :param key_paths: 键路径列表
        :param values: 值列表
        :return: 是否成功
        """
        index = 0
        for key_path in key_paths:
            val = await cls.update_val(file_path[index], key_path, values[index])
            index += 1
            if(val is False):
                return False
        return True
    
    @classmethod
    async def update_or_create_val(
                                cls,
                                file_path: str | Path,
                                key_path: List[str|int] | str | int,
                                value: Any
                                ) -> bool | None:
        """
        更新或创建Json文件中的值

        :param file_path: 文件路径
        :param key_path: 键路径
        :param value: 值
        :return: 是否成功
        """
        if not os.path.exists(file_path):
            await cls.init_json(file_path)

        if(isinstance(key_path, (str, int))):
            key_path = [key_path]
        
        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        global temp_next_val
        is_first = True
        deepth = 2

        for key in key_path:
            if(is_first):
                val = cls.get_next_floor(raw, key)
                if(val is None):
                    if isinstance(key, int):
                        raw.update({key: []})
                    else:
                        raw.update({key: {}})
                    temp_next_val = raw[key]
                    is_first = False
                    continue
                else:
                    if(len(key_path) == 1):
                        raw[key] = value
                        with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                            f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                        return True
                    else:
                        temp_next_val = val
                        is_first = False
                        continue
            else:
                if(len(key_path) == deepth):
                    temp_next_val.update({key: value})
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                    return True
                else:
                    val = cls.get_next_floor(temp_next_val, key)
                    if(val is None):
                        if isinstance(key, int):
                            temp_next_val.update({key: []})
                        else:
                            temp_next_val.update({key: {}})
                        temp_next_val = temp_next_val[key]
                        deepth += 1
                        continue
                    temp_next_val = val
                    deepth += 1
                    continue

    @classmethod
    async def del_val(
                    cls,
                    file_path: str | Path,
                    key_path: List[str|int] | str | int
                    ) -> bool | Exception | None:
        """
        删除Json文件中的值

        :param file_path: 文件路径
        :param key_path: 键路径
        :return: 是否成功
        """
        if not os.path.exists(file_path):
            await cls.init_json(file_path)

        if(isinstance(key_path, (str, int))):
            key_path = [key_path]
        
        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        global temp_next_val
        is_first = True
        deepth = 2

        for key in key_path:
            if(is_first):
                if(len(key_path) == 0):
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps({}, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                val = cls.get_next_floor(raw, key)
                if(len(key_path) == 1):
                    del raw[key]
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                    return True
                else:
                    temp_next_val = val
                    is_first = False
                    continue
            else:
                if(len(key_path) == deepth):
                    del temp_next_val[key]
                    with open(cls.path_prefix + str(file_path), "w", encoding=cls.encode) as f:
                        f.write(json.dumps(raw, ensure_ascii=cls.enable_ascii, indent=cls.indent))
                    return True
                else:
                    val = cls.get_next_floor(temp_next_val, key)
                    if(val is None):
                        return False
                    temp_next_val = val
                    deepth += 1
                    continue

    @classmethod
    async def init_json(
                    cls,
                    file_path: str | Path,
                    *args,
                    init_val: dict = {},
    ):
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        raw = init_val
        json.dump(raw, open(cls.path_prefix + str(file_path), "w", encoding=cls.encode), ensure_ascii=cls.enable_ascii, indent=cls.indent)

    @classmethod
    async def init_many_jsons(
                            cls,
                            file_paths: List[str] | List[Path],
                            *args,
                            init_val: List[dict] = [],
    ):
        index = 0
        for file_path in file_paths:
            if len(init_val) == 0:
                await cls.init_json(file_path)
            else:
                if index >= len(init_val):
                    await cls.init_json(file_path)
                else:
                    await cls.init_json(file_path, init_val=init_val[index])
                    index += 1