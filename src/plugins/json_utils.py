import json
from typing import List, Any
from pathlib import Path

async def read_and_add_list(file_path, key, value):
    raw_data = json.loads(open(file_path, "r", encoding="utf-8").read())
    if key in raw_data:
        if value not in raw_data[key]:
            raw_data[key].append(value)
        else:
            return False
    else:
        raw_data[key] = [value]
    return True

async def read_and_remove_list(file_path, key, value):
    raw_data = json.loads(open(file_path, "r", encoding="utf-8").read())
    if key in raw_data:
        if value in raw_data[key]:
            raw_data[key].remove(value)
        else:
            return False
    else:
        return False
    return True

async def read_and_write_key(file_path, key, value):
    raw_data = json.loads(open(file_path, "r", encoding="utf-8").read())
    raw_data[key] = value
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(raw_data))

class JsonUtils(object):
    path_prefix = "data/"
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
                            key_path: List[str|int] | str | int
                            ) -> Any | Exception | None:
        """
        读取Json文件并获取值

        :param file_path: 文件路径
        :param key_path: 键路径
        :return: 值
        """
        if isinstance(key_path, str):
            key_path = [key_path]
        elif isinstance(key_path, int):
            key_path = [key_path]

        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        temp_next_val = None
        is_first = True
        deepth = 2

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
        if isinstance(key_path, str):
            key_path = [key_path]
        elif isinstance(key_path, int):
            key_path = [key_path]
        
        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        global temp_next_val
        is_first = True
        deepth = 2

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
        if isinstance(key_path, str):
            key_path = [key_path]
        elif isinstance(key_path, int):
            key_path = [key_path]
        
        raw: dict = json.loads(open(cls.path_prefix + str(file_path), "r", encoding=cls.encode).read())
        global temp_next_val
        is_first = True
        deepth = 2

        for key in key_path:
            if(is_first):
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
                    init_val: Any = None,
    ):
        pass

    @classmethod
    async def init_many_jsons(
                            cls,
                            file_paths: List[str | Path],
                            *args,
                            init_val: Any = None,
    ):
        pass