"""
内存存储服务
用于存储分割历史记录、对比列表、批量任务等数据
设计为便于后续迁移到MySQL数据库
"""
import uuid
import zipfile
import os
import io
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class SegmentationResult:
    """分割结果数据结构"""
    result_id: str
    original_filename: str
    model_name: str
    segment_type: str  # 'semantic' 或 'instance'
    iou: float
    accuracy: float
    process_time: float
    class_names: List[str]
    class_iou: List[float]
    pixel_distribution: List[float]
    timestamp: str
    # 图片数据（base64编码）
    original_image: Optional[str] = None
    segmented_image: Optional[str] = None
    fused_image: Optional[str] = None
    bbox_image: Optional[str] = None
    # 实例分割特有数据
    instance_info: Optional[List[Dict]] = None
    instance_count: Optional[int] = None
    # 文件路径（用于批量下载）
    result_file_path: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SegmentationResult':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class BatchTask:
    """批量分割任务数据结构"""
    task_id: str
    total_count: int  # 总图片数
    success_count: int  # 成功数
    failed_count: int  # 失败数
    status: str  # 'processing', 'completed', 'failed'
    created_at: str
    completed_at: Optional[str]
    results: List[Dict]  # 成功的结果列表
    failed_files: List[Dict]  # 失败的文件列表
    zip_file_path: Optional[str]  # ZIP文件路径
    preview_results: List[Dict]  # 前3张预览结果
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BatchTask':
        """从字典创建实例"""
        return cls(**data)


class MemoryStorageService:
    """内存存储服务（单例模式）"""
    
    def __init__(self):
        """初始化存储服务"""
        self.segmentation_history: Dict[str, SegmentationResult] = {}  # result_id -> result
        self.compare_list: List[str] = []  # result_id列表
        self.batch_tasks: Dict[str, BatchTask] = {}  # task_id -> batch_task
        
        print("[MemoryStorageService] Initialized memory storage service")
    
    # ========== 分割历史记录 ==========
    
    def add_segmentation_result(self, result: SegmentationResult) -> None:
        """添加分割结果到历史记录"""
        self.segmentation_history[result.result_id] = result
        print(f"[MemoryStorage] Added segmentation result: {result.result_id}")
    
    def get_segmentation_result(self, result_id: str) -> Optional[SegmentationResult]:
        """获取单个分割结果"""
        return self.segmentation_history.get(result_id)
    
    def get_all_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取所有历史记录（分页）"""
        all_results = list(self.segmentation_history.values())
        # 按时间倒序排序
        all_results.sort(key=lambda x: x.timestamp, reverse=True)
        # 分页
        paginated = all_results[offset:offset+limit]
        return [r.to_dict() for r in paginated]
    
    def delete_segmentation_result(self, result_id: str) -> bool:
        """删除分割结果"""
        if result_id in self.segmentation_history:
            del self.segmentation_history[result_id]
            # 同时从对比列表中移除
            if result_id in self.compare_list:
                self.compare_list.remove(result_id)
            print(f"[MemoryStorage] Deleted segmentation result: {result_id}")
            return True
        return False
    
    # ========== 对比列表 ==========
    
    def add_to_compare(self, result_id: str) -> bool:
        """添加结果到对比列表"""
        if result_id not in self.segmentation_history:
            print(f"[MemoryStorage] Result not found: {result_id}")
            return False
        
        if result_id not in self.compare_list:
            self.compare_list.append(result_id)
            print(f"[MemoryStorage] Added to compare list: {result_id}")
            return True
        return False
    
    def remove_from_compare(self, result_id: str) -> bool:
        """从对比列表移除"""
        if result_id in self.compare_list:
            self.compare_list.remove(result_id)
            print(f"[MemoryStorage] Removed from compare list: {result_id}")
            return True
        return False
    
    def clear_compare_list(self) -> None:
        """清空对比列表"""
        self.compare_list.clear()
        print("[MemoryStorage] Cleared compare list")
    
    def get_compare_list(self) -> List[Dict]:
        """获取对比列表详情"""
        results = []
        for result_id in self.compare_list:
            result = self.segmentation_history.get(result_id)
            if result:
                results.append(result.to_dict())
        return results
    
    # ========== 批量任务 ==========
    
    def create_batch_task(self, total_count: int) -> BatchTask:
        """创建批量任务"""
        task_id = str(uuid.uuid4())
        task = BatchTask(
            task_id=task_id,
            total_count=total_count,
            success_count=0,
            failed_count=0,
            status='processing',
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            completed_at=None,
            results=[],
            failed_files=[],
            zip_file_path=None,
            preview_results=[]
        )
        self.batch_tasks[task_id] = task
        print(f"[MemoryStorage] Created batch task: {task_id}")
        return task
    
    def update_batch_task(self, task_id: str, **kwargs) -> Optional[BatchTask]:
        """更新批量任务"""
        if task_id not in self.batch_tasks:
            return None
        
        task = self.batch_tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        print(f"[MemoryStorage] Updated batch task: {task_id}")
        return task
    
    def get_batch_task(self, task_id: str) -> Optional[BatchTask]:
        """获取批量任务"""
        return self.batch_tasks.get(task_id)
    
    def add_batch_result(self, task_id: str, result: SegmentationResult) -> None:
        """添加批量任务的结果"""
        if task_id not in self.batch_tasks:
            return
        
        task = self.batch_tasks[task_id]
        task.results.append(result.to_dict())
        task.success_count += 1
        
        # 只有前3张加入预览结果
        if len(task.preview_results) < 3:
            task.preview_results.append(result.to_dict())
        
        print(f"[MemoryStorage] Added result to batch task {task_id}: {result.result_id}")
    
    def add_batch_failure(self, task_id: str, filename: str, error: str) -> None:
        """添加批量任务的失败记录"""
        if task_id not in self.batch_tasks:
            return
        
        task = self.batch_tasks[task_id]
        task.failed_files.append({
            'filename': filename,
            'error': error
        })
        task.failed_count += 1
        
        print(f"[MemoryStorage] Added failure to batch task {task_id}: {filename}")
    
    # ========== 工具方法 ==========
    
    def export_to_json(self) -> str:
        """导出所有数据为JSON（便于后续迁移）"""
        data = {
            'segmentation_history': {
                k: v.to_dict() for k, v in self.segmentation_history.items()
            },
            'compare_list': self.compare_list,
            'batch_tasks': {
                k: v.to_dict() for k, v in self.batch_tasks.items()
            }
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_from_json(self, json_str: str) -> None:
        """从JSON导入数据"""
        data = json.loads(json_str)
        
        # 导入分割历史
        for result_id, result_dict in data.get('segmentation_history', {}).items():
            self.segmentation_history[result_id] = SegmentationResult.from_dict(result_dict)
        
        # 导入对比列表
        self.compare_list = data.get('compare_list', [])
        
        # 导入批量任务
        for task_id, task_dict in data.get('batch_tasks', {}).items():
            self.batch_tasks[task_id] = BatchTask.from_dict(task_dict)
        
        print("[MemoryStorage] Imported data from JSON")


# 全局存储服务实例
_storage_service_instance = None


def get_storage_service() -> MemoryStorageService:
    """获取存储服务实例（单例）"""
    global _storage_service_instance
    if _storage_service_instance is None:
        _storage_service_instance = MemoryStorageService()
    return _storage_service_instance
