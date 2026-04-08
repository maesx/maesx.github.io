"""
可视化API路由
"""
import torch
from flask_restful import Resource


class VisualizationResource(Resource):
    """可视化资源"""
    
    def get(self, result_id):
        """
        获取分割结果的可视化数据
        
        Args:
            result_id: 结果ID
            
        Returns:
            可视化数据（图表等）
        """
        # TODO: 实现从文件或数据库读取结果
        return {
            'success': True,
            'result_id': result_id,
            'message': 'Visualization data will be implemented'
        }


class GPUMonitorResource(Resource):
    """GPU监控资源"""
    
    def get(self):
        """
        获取GPU使用状态
        
        Returns:
            GPU信息
        """
        gpu_info = {
            'available': False,
            'type': 'CPU',
            'device': 'CPU Only'
        }
        
        try:
            # 检查MPS (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                gpu_info = {
                    'available': True,
                    'type': 'MPS',
                    'device': 'Apple Silicon GPU',
                    'backend': 'Metal Performance Shaders',
                    'memory': {
                        'used': 0,  # MPS 目前没有提供准确的内存使用接口
                        'recommended_max': 8192  # 估计值,实际取决于系统内存
                    }
                }
            # 检查CUDA
            elif torch.cuda.is_available():
                device_id = 0
                gpu_info = {
                    'available': True,
                    'type': 'CUDA',
                    'device': torch.cuda.get_device_name(device_id),
                    'capability': f"{torch.cuda.get_device_capability(device_id)[0]}.{torch.cuda.get_device_capability(device_id)[1]}",
                    'memory': {
                        'total': torch.cuda.get_device_properties(device_id).total_memory / (1024**3),  # GB
                        'used': torch.cuda.memory_allocated(device_id) / (1024**3),  # GB
                        'cached': torch.cuda.memory_reserved(device_id) / (1024**3)  # GB
                    }
                }
        except Exception as e:
            print(f"Error getting GPU info: {e}")
        
        return {
            'success': True,
            'gpu': gpu_info
        }
