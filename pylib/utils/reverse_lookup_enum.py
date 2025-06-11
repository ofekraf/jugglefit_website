from enum import Enum


class ReverseLookupEnum(Enum):
    @classmethod
    def get_key_by_value(cls, value):
        for k, v in cls.__members__.items():
            if v.value == value:
                return v
        raise ValueError(f"No enum member with value {value}")
