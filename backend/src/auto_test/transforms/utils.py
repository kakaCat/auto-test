"""
Transform层工具函数
提供函数式编程辅助工具
"""

from typing import Any, Callable, Dict, Optional
from datetime import datetime


def pipe(value: Any, *functions: Callable[[Any], Any]) -> Any:
    """
    函数管道，将值依次通过多个函数处理
    
    Args:
        value: 初始值
        *functions: 处理函数序列
        
    Returns:
        Any: 经过所有函数处理后的最终值
        
    Example:
        result = pipe(
            raw_data,
            add_business_fields,
            format_timestamps,
            validate_data
        )
    """
    for func in functions:
        value = func(value)
    return value


def format_datetime(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化日期时间字符串
    
    Args:
        datetime_str (str): 原始日期时间字符串
        format_str (str): 目标格式字符串
        
    Returns:
        str: 格式化后的日期时间字符串
    """
    if not datetime_str:
        return ''
    
    try:
        # 处理ISO格式的时间字符串
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str.replace('Z', '+00:00')
        
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return datetime_str


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        data (Dict[str, Any]): 数据字典
        key (str): 键名
        default (Any): 默认值
        
    Returns:
        Any: 字典值或默认值
    """
    return data.get(key, default) if isinstance(data, dict) else default


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value (Any): 待转换值
        default (int): 默认值
        
    Returns:
        int: 转换后的整数或默认值
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = '') -> str:
    """
    安全转换为字符串
    
    Args:
        value (Any): 待转换值
        default (str): 默认值
        
    Returns:
        str: 转换后的字符串或默认值
    """
    try:
        return str(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def parse_tags(tags_str: str) -> list:
    """
    解析标签字符串为列表
    
    Args:
        tags_str (str): 标签字符串，逗号分隔
        
    Returns:
        list: 标签列表
    """
    if not tags_str or not isinstance(tags_str, str):
        return []
    
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]


def create_key(*parts: Any) -> str:
    """
    创建复合键
    
    Args:
        *parts: 键的组成部分
        
    Returns:
        str: 复合键字符串
    """
    return '_'.join(str(part) for part in parts if part is not None)


def add_field(data: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """
    添加字段到数据字典（不可变操作）
    
    Args:
        data (Dict[str, Any]): 原始数据
        key (str): 字段名
        value (Any): 字段值
        
    Returns:
        Dict[str, Any]: 新的数据字典
    """
    result = data.copy()
    result[key] = value
    return result


def remove_field(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    移除字段从数据字典（不可变操作）
    
    Args:
        data (Dict[str, Any]): 原始数据
        key (str): 要移除的字段名
        
    Returns:
        Dict[str, Any]: 新的数据字典
    """
    result = data.copy()
    result.pop(key, None)
    return result


def transform_field(data: Dict[str, Any], key: str, transformer: Callable[[Any], Any]) -> Dict[str, Any]:
    """
    转换字段值（不可变操作）
    
    Args:
        data (Dict[str, Any]): 原始数据
        key (str): 字段名
        transformer (Callable): 转换函数
        
    Returns:
        Dict[str, Any]: 新的数据字典
    """
    result = data.copy()
    if key in result:
        result[key] = transformer(result[key])
    return result


def merge_data(*data_dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个数据字典
    
    Args:
        *data_dicts: 数据字典序列
        
    Returns:
        Dict[str, Any]: 合并后的数据字典
    """
    result = {}
    for data in data_dicts:
        if isinstance(data, dict):
            result.update(data)
    return result