"""
模型管理服务
处理模型的扫描、加载、缓存等功能
"""
import os
import glob
import torch
from typing import Dict, List, Optional
from datetime import datetime


class ModelService:
    """模型管理服务"""
    
    def __init__(self, checkpoint_folder: str):
        """
        初始化模型服务
        
        Args:
            checkpoint_folder: 模型存放目录
        """
        self.checkpoint_folder = checkpoint_folder
        self.loaded_models: Dict[str, torch.nn.Module] = {}  # 模型缓存
        
    def get_model_list(self) -> List[Dict]:
        """
        获取所有可用模型列表
        
        Returns:
            模型信息列表
        """
        models = []
        
        if not os.path.exists(self.checkpoint_folder):
            return models
        
        # 扫描所有.pth文件
        model_files = glob.glob(os.path.join(self.checkpoint_folder, '*.pth'))
        
        for model_path in model_files:
            model_info = self._get_model_info(model_path)
            if model_info:
                models.append(model_info)
        
        # 按IoU排序
        models.sort(key=lambda x: x.get('iou', 0), reverse=True)
        
        return models
    
    def _get_model_info(self, model_path: str) -> Optional[Dict]:
        """
        获取单个模型的信息
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            模型信息字典
        """
        try:
            # 获取文件基本信息
            file_stat = os.stat(model_path)
            file_size_mb = file_stat.st_size / (1024 * 1024)
            created_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            # 尝试加载模型获取详细信息
            try:
                # 第一次尝试使用 weights_only=True（更安全）
                checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
            except Exception as e:
                # 如果失败，使用 weights_only=False（需要信任文件来源）
                print(f"[ModelService] Warning: weights_only load failed for {os.path.basename(model_path)}, using full load: {e}")
                checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            
            model_info = {
                'name': os.path.basename(model_path).replace('.pth', ''),
                'path': model_path,
                'filename': os.path.basename(model_path),
                'size': f"{file_size_mb:.1f}MB",
                'size_mb': round(file_size_mb, 2),
                'created_at': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'unknown'
            }
            
            # 提取模型训练信息
            if 'best_iou' in checkpoint:
                model_info['iou'] = round(checkpoint['best_iou'], 4)
            else:
                model_info['iou'] = 0.0
            
            if 'epoch' in checkpoint:
                model_info['epoch'] = checkpoint['epoch']
            
            if 'args' in checkpoint:
                args = checkpoint['args']
                model_info['args'] = {
                    'lr': getattr(args, 'lr', None),
                    'batch_size': getattr(args, 'batch_size', None),
                    'epochs': getattr(args, 'epochs', None),
                    'img_size': getattr(args, 'img_size', None)
                }
            
            # 判断模型类型
            if 'model_state_dict' in checkpoint:
                model_info['type'] = 'semantic'  # U-Net++语义分割
            else:
                # 可能是YOLOv8模型
                model_info['type'] = 'instance'  # 实例分割
            
            return model_info
            
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
            return None
    
    def load_model(self, model_name: str, model_class=None):
        """
        加载模型（带缓存）
        
        Args:
            model_name: 模型名称
            model_class: 模型类（用于语义分割模型）
            
        Returns:
            加载的模型
        """
        # 检查缓存
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        # 查找模型文件
        model_files = glob.glob(os.path.join(self.checkpoint_folder, f'{model_name}.pth'))
        if not model_files:
            raise FileNotFoundError(f"Model {model_name} not found")
        
        model_path = model_files[0]
        
        # 加载模型 - 使用与 _get_model_info 相同的错误处理逻辑
        try:
            # 第一次尝试使用 weights_only=True（更安全）
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
        except Exception as e:
            # 如果失败，使用 weights_only=False（需要信任文件来源）
            print(f"[ModelService] Warning: weights_only load failed for {model_name}, using full load: {e}")
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        
        # 判断模型类型并加载
        # 这里暂时返回checkpoint，具体加载逻辑在分割服务中实现
        self.loaded_models[model_name] = checkpoint
        
        return checkpoint
    
    def clear_cache(self, model_name: Optional[str] = None):
        """
        清除模型缓存
        
        Args:
            model_name: 指定模型名称，None则清除所有
        """
        if model_name:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
        else:
            self.loaded_models.clear()
    
    def delete_model(self, model_name: str) -> bool:
        """
        删除模型文件
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否成功删除
        """
        model_files = glob.glob(os.path.join(self.checkpoint_folder, f'{model_name}.pth'))
        if model_files:
            try:
                # 清除缓存
                self.clear_cache(model_name)
                # 删除文件
                os.remove(model_files[0])
                return True
            except Exception as e:
                print(f"Error deleting model {model_name}: {e}")
                return False
        return False


# 全局模型服务实例
_model_service_instance = None


def get_model_service(checkpoint_folder: str) -> ModelService:
    """
    获取模型服务实例（单例）
    
    Args:
        checkpoint_folder: 模型目录
        
    Returns:
        模型服务实例
    """
    global _model_service_instance
    if _model_service_instance is None:
        _model_service_instance = ModelService(checkpoint_folder)
        print(f"[ModelService] Created new instance with checkpoint_folder: {checkpoint_folder}")
    elif _model_service_instance.checkpoint_folder != checkpoint_folder:
        # 如果checkpoint_folder发生变化，更新实例
        print(f"[ModelService] Updating checkpoint_folder from {_model_service_instance.checkpoint_folder} to {checkpoint_folder}")
        _model_service_instance.checkpoint_folder = checkpoint_folder
    return _model_service_instance