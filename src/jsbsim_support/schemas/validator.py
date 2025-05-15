from typing import TypeVar

from omegaconf import ListConfig
from pydantic import ValidationError

T = TypeVar("T")


def convert_value_to_list(v: T) -> list[T]:
    if isinstance(v, (list, ListConfig)):
        return list(v)
    return [v]


def convert_value_to_list_optional(v: T) -> list[T]:
    if v is None:
        return []
    if isinstance(v, (list, ListConfig)):
        return list(v)
    return [v]
