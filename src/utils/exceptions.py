"""
自定义异常类

提供统一的异常类层次结构，用于处理各类错误情况。
"""
from typing import Optional


class SegmentationError(Exception):
    """基础异常类 - 所有分割相关异常的基类"""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ModelLoadError(SegmentationError):
    """模型加载失败异常

    当模型文件不存在、格式错误或加载失败时抛出。
    """

    def __init__(self, message: str = "模型加载失败", details: Optional[str] = None) -> None:
        super().__init__(message, details)


class DataLoadError(SegmentationError):
    """数据加载失败异常

    当数据目录不存在、数据格式错误或加载失败时抛出。
    """

    def __init__(self, message: str = "数据加载失败", details: Optional[str] = None) -> None:
        super().__init__(message, details)


class ConfigError(SegmentationError):
    """配置错误异常

    当配置参数无效或缺失时抛出。
    """

    def __init__(self, message: str = "配置错误", details: Optional[str] = None) -> None:
        super().__init__(message, details)


class InferenceError(SegmentationError):
    """推理错误异常

    当推理过程中发生错误时抛出。
    """

    def __init__(self, message: str = "推理错误", details: Optional[str] = None) -> None:
        super().__init__(message, details)