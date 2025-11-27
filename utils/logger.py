"""
工具模块 - 日志管理
提供统一的日志记录功能
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import config

class LogManager:
    """日志管理器"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.SYSTEM_CONFIG['log_level']))
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建日志目录
        log_dir = config.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            config.LOG_CONFIG['format'],
            datefmt=config.LOG_CONFIG['date_format']
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.LOG_CONFIG['max_bytes'],
            backupCount=config.LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            config.LOG_CONFIG['format'],
            datefmt=config.LOG_CONFIG['date_format']
        )
        file_handler.setFormatter(file_formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger

# 创建默认日志记录器
system_logger = LogManager.get_logger('system')
auth_logger = LogManager.get_logger('auth')
inference_logger = LogManager.get_logger('inference')
training_logger = LogManager.get_logger('training')
