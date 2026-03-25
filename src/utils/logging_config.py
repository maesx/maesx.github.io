"""
日志配置模块

提供统一的日志配置功能，支持控制台和文件输出。
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    配置并返回一个日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可选）
        level: 日志级别
        format_string: 自定义格式字符串（可选）

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 默认格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string)

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_training_logger(log_dir: str = 'outputs/logs') -> logging.Logger:
    """
    获取训练日志记录器

    Args:
        log_dir: 日志目录

    Returns:
        训练日志记录器
    """
    log_file = f"{log_dir}/training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    return setup_logger('training', log_file)


def get_inference_logger(log_dir: str = 'outputs/logs') -> logging.Logger:
    """
    获取推理日志记录器

    Args:
        log_dir: 日志目录

    Returns:
        推理日志记录器
    """
    log_file = f"{log_dir}/inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    return setup_logger('inference', log_file)


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    获取通用日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可选）

    Returns:
        日志记录器
    """
    return setup_logger(name, log_file)