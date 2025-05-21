"""パラメータのスキーマのバリデータ."""

from typing import TypeVar

from omegaconf import ListConfig

T = TypeVar("T")


def convert_value_to_list(v: T) -> list[T]:
    """値をリストに変換する."""
    if isinstance(v, (list, ListConfig)):
        return list(v)
    return [v]


def convert_value_to_list_optional(v: T) -> list[T]:
    """値をリストに変換する. 値がNoneの場合は空のリストを返す."""
    if v is None:
        return []
    if isinstance(v, (list, ListConfig)):
        return list(v)
    return [v]
