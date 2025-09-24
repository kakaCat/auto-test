"""
日志服务层

负责日志相关的业务逻辑处理，包括：
- 日志数据收集和组装
- 日志统计信息计算
- 日志查询和筛选

遵循极简控制器编码规范：
- Service层负责数据收集与组装
- 不直接操作基础设施
- 使用静态方法提高性能
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..models.log import LogEntry, LogStats, LogResponse, LogLevel


class LogService:
    """日志服务类 - 使用静态方法"""
    
    @staticmethod
    def collect_logs_data(
        page: int = 1,
        size: int = 20,
        level: Optional[str] = None,
        module: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        收集日志数据
        
        Args:
            page: 页码
            size: 每页数量
            level: 日志级别筛选
            module: 模块筛选
            start_time: 开始时间
            end_time: 结束时间
            keyword: 关键词搜索
            
        Returns:
            包含日志列表和统计信息的字典
        """
        # 模拟日志数据 - 实际项目中应该从数据库或日志文件读取
        mock_logs = LogService._generate_mock_logs()
        
        # 应用筛选条件
        filtered_logs = LogService._filter_logs(
            mock_logs, level, module, start_time, end_time, keyword
        )
        
        # 分页处理
        total = len(filtered_logs)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        # 计算统计信息
        stats = LogService._calculate_stats(filtered_logs)
        
        return {
            "logs": paginated_logs,
            "total": total,
            "page": page,
            "size": size,
            "stats": stats
        }
    
    @staticmethod
    def collect_log_stats_data() -> Dict[str, Any]:
        """
        收集日志统计数据
        
        Returns:
            日志统计信息字典
        """
        mock_logs = LogService._generate_mock_logs()
        stats = LogService._calculate_stats(mock_logs)
        return stats.dict()
    
    @staticmethod
    def _generate_mock_logs() -> List[LogEntry]:
        """生成模拟日志数据"""
        now = datetime.now()
        logs = []
        
        # 生成一些示例日志
        log_entries = [
            {
                "level": LogLevel.INFO,
                "message": "系统启动成功",
                "module": "main",
                "function": "startup"
            },
            {
                "level": LogLevel.INFO,
                "message": "用户登录成功",
                "module": "auth",
                "function": "login",
                "user_id": "user_001"
            },
            {
                "level": LogLevel.WARNING,
                "message": "API调用频率过高",
                "module": "api",
                "function": "rate_limit"
            },
            {
                "level": LogLevel.ERROR,
                "message": "数据库连接失败",
                "module": "database",
                "function": "connect"
            },
            {
                "level": LogLevel.DEBUG,
                "message": "调试信息：变量值检查",
                "module": "debug",
                "function": "check_vars"
            },
            {
                "level": LogLevel.INFO,
                "message": "API请求处理完成",
                "module": "api",
                "function": "handle_request"
            },
            {
                "level": LogLevel.WARNING,
                "message": "内存使用率较高",
                "module": "monitor",
                "function": "check_memory"
            },
            {
                "level": LogLevel.ERROR,
                "message": "文件读取失败",
                "module": "file",
                "function": "read_file"
            }
        ]
        
        for i, entry in enumerate(log_entries):
            log = LogEntry(
                id=i + 1,
                timestamp=now - timedelta(minutes=i * 10),
                level=entry["level"],
                message=entry["message"],
                module=entry.get("module"),
                function=entry.get("function"),
                line_number=100 + i,
                user_id=entry.get("user_id"),
                request_id=f"req_{i+1:03d}",
                extra_data={"source": "mock"}
            )
            logs.append(log)
        
        return logs
    
    @staticmethod
    def _filter_logs(
        logs: List[LogEntry],
        level: Optional[str] = None,
        module: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> List[LogEntry]:
        """应用筛选条件"""
        filtered = logs
        
        if level:
            filtered = [log for log in filtered if log.level == level]
        
        if module:
            filtered = [log for log in filtered if log.module == module]
        
        if start_time:
            filtered = [log for log in filtered if log.timestamp >= start_time]
        
        if end_time:
            filtered = [log for log in filtered if log.timestamp <= end_time]
        
        if keyword:
            filtered = [
                log for log in filtered 
                if keyword.lower() in log.message.lower()
            ]
        
        return filtered
    
    @staticmethod
    def _calculate_stats(logs: List[LogEntry]) -> LogStats:
        """计算日志统计信息"""
        stats = LogStats()
        stats.total_logs = len(logs)
        
        for log in logs:
            if log.level == LogLevel.INFO:
                stats.info_logs += 1
            elif log.level == LogLevel.WARNING:
                stats.warning_logs += 1
            elif log.level == LogLevel.ERROR:
                stats.error_logs += 1
            elif log.level == LogLevel.DEBUG:
                stats.debug_logs += 1
            elif log.level == LogLevel.CRITICAL:
                stats.critical_logs += 1
        
        return stats