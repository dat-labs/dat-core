from enum import Enum
from pydantic import BaseModel


class EnumWithStr(str, Enum):
    def __str__(self):
        return self.value
