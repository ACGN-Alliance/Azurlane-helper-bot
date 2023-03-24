import json

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