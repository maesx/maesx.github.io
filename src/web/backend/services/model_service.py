"""
模型管理服务
处理模型的扫描、加载、缓存等功能
"""
import os
import glob
import torch
from typing import Dict, List, Optional, Tuple, Any
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
        self.loaded_checkpoints: Dict[str, dict] = {}  # checkpoint缓存（权重数据）
        self.loaded_models: Dict[str, Tuple[torch.nn.Module, str]] = {}  # 模型实例缓存 (model, device)
        self._model_list_cache: Optional[List[Dict]] = None  # 模型列表缓存
        self._model_list_cache_time: float = 0  # 缓存时间戳
        
    def get_model_list(self, use_cache: bool = True) -> List[Dict]:
        """
        获取所有可用模型列表
        
        Args:
            use_cache: 是否使用缓存（默认True，首次加载后缓存10分钟）
            
        Returns:
            模型信息列表
        """
        import time
        cache_ttl = 600  # 缓存有效期10分钟
        
        # 检查缓存是否有效
        if use_cache and self._model_list_cache is not None:
            if time.time() - self._model_list_cache_time < cache_ttl:
                return self._model_list_cache
        
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
        
        # 更新缓存
        self._model_list_cache = models
        self._model_list_cache_time = time.time()
        
        return models
    
    def invalidate_model_list_cache(self):
        """清除模型列表缓存"""
        self._model_list_cache = None
        self._model_list_cache_time = 0
    
    def _detect_model_architecture(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测模型架构类型和配置
        
        Args:
            state_dict: 模型权重字典
            
        Returns:
            架构信息字典: {'type': 'ultimate'|'enhanced'|'standard', 'use_fpn': bool, ...}
        """
        result = {'type': 'standard', 'use_fpn': False, 'use_separable_conv': False, 'attention_type': 'none'}
        
        # 检查是否使用ResNet编码器 (UNetPlusPlusUltimate)
        if 'layer1.0.conv1.weight' in state_dict or 'conv1.weight' in state_dict:
            # 检查是否使用深度可分离卷积
            has_separable = any('conv.0.weight' in k and state_dict[k].shape[1] == 1 
                               for k in state_dict.keys() if 'decoder' in k)
            if has_separable:
                result['type'] = 'ultimate'
                result['use_separable_conv'] = True
                
                # 检查是否使用FPN - 通过检查decoder的输入通道数
                # 深度可分离卷积结构: conv.0(深度), conv.1(BN), conv.2(逐点), conv.3(BN)
                # conv.2.weight的形状是 [out_channels, in_channels, 1, 1]
                if 'decoder4.0.conv.2.weight' in state_dict:
                    # conv.2是逐点卷积,shape的第2维是输入通道数
                    dec4_conv_weight = state_dict['decoder4.0.conv.2.weight']
                    if len(dec4_conv_weight.shape) == 4:
                        dec4_in_ch = dec4_conv_weight.shape[1]
                        # FPN模式下,decoder4输入应该是512(256+256)
                        # 非FPN模式下,decoder4输入应该是3072(2048+1024)或1536(512+1024)
                        result['use_fpn'] = (dec4_in_ch == 512)
                
                # 检测注意力类型
                has_cbam = any('cbam_layer' in k for k in state_dict.keys())
                has_se = any('se_layer' in k for k in state_dict.keys())
                has_aspp = any('aspp' in k for k in state_dict.keys())
                
                if has_cbam and has_se and has_aspp:
                    result['attention_type'] = 'full'
                elif has_cbam and has_aspp:
                    result['attention_type'] = 'cbam_aspp'
                elif has_se and has_aspp:
                    result['attention_type'] = 'se_aspp'
                elif has_cbam:
                    result['attention_type'] = 'cbam'
                elif has_se:
                    result['attention_type'] = 'se'
                elif has_aspp:
                    result['attention_type'] = 'aspp'
        
        # 检查是否使用注意力模块 (UNetPlusPlusEnhanced)
        has_attention = any('cbam' in k or 'se_' in k or 'aspp' in k 
                           for k in state_dict.keys())
        if has_attention and result['type'] == 'standard':
            result['type'] = 'enhanced'
        
        print(f"[ModelService] 架构检测细节:")
        print(f"  - 类型: {result['type']}")
        print(f"  - 使用FPN: {result['use_fpn']}")
        print(f"  - 使用深度可分离卷积: {result['use_separable_conv']}")
        print(f"  - 注意力类型: {result['attention_type']}")
        
        return result
    
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
                'created_at': created_time.strftime('%Y-%m-%d %H:%M'),
                'type': 'unknown',
                'architecture': 'unknown'
            }
            
            # 提取模型权重
            state_dict = checkpoint.get('model_state_dict', checkpoint)
            
            # 检测模型架构
            arch_info = self._detect_model_architecture(state_dict)
            model_info['architecture'] = arch_info['type']
            model_info['use_fpn'] = arch_info.get('use_fpn', False)
            
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
    
    def load_checkpoint(self, model_name: str) -> dict:
        """
        加载模型权重（带缓存）
        
        Args:
            model_name: 模型名称
            
        Returns:
            checkpoint字典
        """
        # 检查缓存
        if model_name in self.loaded_checkpoints:
            print(f"[ModelService] 使用缓存的checkpoint: {model_name}")
            return self.loaded_checkpoints[model_name]
        
        # 查找模型文件
        model_files = glob.glob(os.path.join(self.checkpoint_folder, f'{model_name}.pth'))
        if not model_files:
            raise FileNotFoundError(f"Model {model_name} not found")
        
        model_path = model_files[0]
        print(f"[ModelService] 从磁盘加载checkpoint: {model_path}")
        
        # 加载模型 - 使用与 _get_model_info 相同的错误处理逻辑
        try:
            # 第一次尝试使用 weights_only=True（更安全）
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
        except Exception as e:
            # 如果失败，使用 weights_only=False（需要信任文件来源）
            print(f"[ModelService] Warning: weights_only load failed for {model_name}, using full load: {e}")
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        
        # 缓存checkpoint
        self.loaded_checkpoints[model_name] = checkpoint
        
        return checkpoint
    
    def get_or_create_model(self, model_name: str, model_class, device: str, **model_kwargs) -> Tuple[torch.nn.Module, dict]:
        """
        获取或创建模型实例（带缓存）
        
        Args:
            model_name: 模型名称
            model_class: 模型类（已弃用，自动检测架构）
            device: 设备 ('cuda', 'mps', 'cpu')
            **model_kwargs: 模型初始化参数
            
        Returns:
            (模型实例, checkpoint字典)
        """
        # 加载checkpoint（使用缓存）
        checkpoint = self.load_checkpoint(model_name)
        
        # 检查是否有缓存的模型实例
        cache_key = f"{model_name}_{device}"
        if cache_key in self.loaded_models:
            cached_model, cached_device = self.loaded_models[cache_key]
            if cached_device == device:
                print(f"[ModelService] 使用缓存的模型实例: {cache_key}")
                return cached_model, checkpoint
        
        print(f"[ModelService] 创建新的模型实例: {cache_key}")
        
        # 提取模型权重
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
        
        # 检测模型架构
        arch_info = self._detect_model_architecture(state_dict)
        print(f"[ModelService] 检测到模型架构: {arch_info}")
        
        # 根据架构选择模型类
        if arch_info['type'] == 'ultimate':
            from src.models.unet_plusplus_ultimate import UNetPlusPlusUltimate
            model_class_to_use = UNetPlusPlusUltimate
            print(f"[ModelService] 使用 UNetPlusPlusUltimate (ResNet-101编码器)")
        elif arch_info['type'] == 'enhanced':
            from src.models.unet_plusplus_enhanced import UNetPlusPlusEnhanced
            model_class_to_use = UNetPlusPlusEnhanced
            print(f"[ModelService] 使用 UNetPlusPlusEnhanced (注意力机制)")
        else:
            # 使用传入的默认模型类
            model_class_to_use = model_class
            print(f"[ModelService] 使用标准 UNetPlusPlus")
        
        # 从checkpoint获取配置
        use_deep_supervision = False
        encoder_name = 'vgg19_bn'  # 默认值
        
        if 'args' in checkpoint:
            args = checkpoint['args']
            use_deep_supervision = getattr(args, 'deep_supervision', False)
            encoder_name = getattr(args, 'encoder', 'vgg19_bn')
        
        # 根据架构类型设置参数
        if arch_info['type'] == 'ultimate':
            # Ultimate模型的特殊参数 - 根据checkpoint中的配置
            model_params = {
                'in_channels': 3,
                'num_classes': model_kwargs.get('num_classes', 4),
                'deep_supervision': True,  # Ultimate模型默认使用深度监督
                'pretrained': False,
                'use_boundary_refinement': True,
                'use_fpn': arch_info.get('use_fpn', True),  # 使用检测到的FPN配置
                'attention_type': arch_info.get('attention_type', 'cbam_aspp'),  # 使用检测到的注意力类型
                'use_separable_conv': True
            }
            print(f"[ModelService] Ultimate模型配置:")
            print(f"  - use_fpn: {model_params['use_fpn']}")
            print(f"  - deep_supervision: {model_params['deep_supervision']}")
            print(f"  - attention_type: {model_params['attention_type']}")
        elif arch_info['type'] == 'enhanced':
            # Enhanced模型的参数
            model_params = {
                'in_channels': 3,
                'num_classes': model_kwargs.get('num_classes', 4),
                'deep_supervision': use_deep_supervision,
                'encoder_name': encoder_name,
                'pretrained': False,
                'attention_type': 'cbam'
            }
        else:
            # 标准模型的参数
            model_params = {
                'in_channels': 3,
                'num_classes': model_kwargs.get('num_classes', 4),
                'deep_supervision': use_deep_supervision,
                'encoder_name': encoder_name,
                'pretrained': False
            }
        
        # 创建模型实例
        model = model_class_to_use(**model_params)
        
        # 加载权重
        try:
            model.load_state_dict(state_dict, strict=True)
            print(f"[ModelService] ✓ 权重加载成功 (strict模式)")
        except RuntimeError as e:
            print(f"[ModelService] Warning: Strict loading failed, trying partial load: {e}")
            model_dict = model.state_dict()
            pretrained_dict = {k: v for k, v in state_dict.items() if k in model_dict and model_dict[k].shape == v.shape}
            model_dict.update(pretrained_dict)
            model.load_state_dict(model_dict)
            print(f"[ModelService] Loaded {len(pretrained_dict)}/{len(model_dict)} parameters")
        
        # 移动到设备并设置为评估模式
        model = model.to(device)
        model.eval()
        
        # 缓存模型实例
        self.loaded_models[cache_key] = (model, device)
        
        return model, checkpoint
    
    def load_model(self, model_name: str, model_class=None):
        """
        加载模型（带缓存）- 保持向后兼容
        
        Args:
            model_name: 模型名称
            model_class: 模型类（已弃用，仅为了向后兼容）
            
        Returns:
            加载的checkpoint
        """
        return self.load_checkpoint(model_name)
    
    def clear_cache(self, model_name: Optional[str] = None):
        """
        清除模型缓存
        
        Args:
            model_name: 指定模型名称，None则清除所有
        """
        if model_name:
            if model_name in self.loaded_checkpoints:
                del self.loaded_checkpoints[model_name]
            # 清除所有相关的模型实例缓存
            keys_to_remove = [k for k in self.loaded_models.keys() if k.startswith(model_name)]
            for key in keys_to_remove:
                del self.loaded_models[key]
        else:
            self.loaded_checkpoints.clear()
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
                # 清除模型列表缓存
                self.invalidate_model_list_cache()
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