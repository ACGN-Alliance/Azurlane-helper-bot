from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel

class Config(BaseModel):
    start_up_notify: Optional[bool] = False
    regular_update: Optional[bool] = False

config = Config.parse_obj(get_driver().config.dict())