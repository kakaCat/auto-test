"""
Transform层 - 数据转换层
采用函数式编程风格，负责将DAO层原始数据转换为业务响应数据

特点：
- 纯函数设计，无副作用
- 函数组合，可复用
- 数据不可变
- 职责单一
"""

from .module_transform import ModuleTransform
from .system_transform import SystemTransform
from .utils import (
    pipe, format_datetime, safe_get, safe_int, safe_str,
    parse_tags, create_key, add_field, remove_field,
    transform_field, merge_data
)

__all__ = [
    'ModuleTransform',
    'SystemTransform', 
    'pipe',
    'format_datetime',
    'safe_get',
    'safe_int',
    'safe_str',
    'parse_tags',
    'create_key',
    'add_field',
    'remove_field',
    'transform_field',
    'merge_data'
]