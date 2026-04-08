"""
图像分割API路由
"""
import os
import time
import uuid
import base64
from io import BytesIO
import torch
import torch.nn.functional as F
from flask import request, jsonify, current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

from src.models.unet_plusplus import UNetPlusPlus
from src.web.backend.services.model_service import get_model_service


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def preprocess_image(image_path, target_size=(512, 512)):
    """预处理图像"""
    # 读取图像
    image = Image.open(image_path).convert('RGB')
    original_size = image.size
    
    # 调整大小
    image_resized = image.resize(target_size, Image.BILINEAR)
    
    # 转换为numpy数组并归一化
    image_array = np.array(image_resized, dtype=np.float32) / 255.0
    
    # 转换为CHW格式
    image_array = np.transpose(image_array, (2, 0, 1))
    
    # 添加batch维度并转换为tensor
    image_tensor = torch.from_numpy(image_array).unsqueeze(0)
    
    return image_tensor, original_size, np.array(image)


def postprocess_mask(mask, original_size, class_colors):
    """后处理分割掩码"""
    # mask shape: [H, W] 每个像素是类别索引
    
    # 创建彩色掩码
    colored_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    
    for class_idx, color in enumerate(class_colors):
        colored_mask[mask == class_idx] = color
    
    # 调整回原始大小
    mask_image = Image.fromarray(colored_mask)
    mask_image = mask_image.resize(original_size, Image.NEAREST)
    
    return np.array(mask_image)


def create_fused_image(original_image, mask_image, alpha=0.5):
    """创建融合图像"""
    fused = (original_image * (1 - alpha) + mask_image * alpha).astype(np.uint8)
    return fused


class SegmentResource(Resource):
    """图像分割资源"""
    
    def post(self):
        """
        执行单张图像分割
        
        Returns:
            分割结果
        """
        try:
            # 检查文件
            if 'images' not in request.files:
                return {
                    'success': False,
                    'error': 'No images provided'
                }, 400
            
            files = request.files.getlist('images')
            if not files or files[0].filename == '':
                return {
                    'success': False,
                    'error': 'No images selected'
                }, 400
            
            # 获取参数
            model_name = request.form.get('model', 'best_model')
            segment_type = request.form.get('type', 'semantic')
            
            # 只处理第一张图片
            file = files[0]
            if not allowed_file(file.filename):
                return {
                    'success': False,
                    'error': 'Invalid file type'
                }, 400
            
            # 保存上传文件
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # 设备选择 - 支持 CUDA (NVIDIA GPU), MPS (Apple Silicon) 和 CPU
            if torch.cuda.is_available():
                device = torch.device('cuda')
                print(f"使用 CUDA GPU: {torch.cuda.get_device_name(0)}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = torch.device('mps')
                print("使用 Apple Silicon GPU (MPS)")
            else:
                device = torch.device('cpu')
                print("使用 CPU")
            
            # 加载模型
            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])
            checkpoint = model_service.load_model(model_name)
            
            # 检查是否有配置信息
            use_deep_supervision = False
            encoder_name = 'vgg19_bn'  # 默认值
            
            if 'args' in checkpoint:
                args = checkpoint['args']
                use_deep_supervision = getattr(args, 'deep_supervision', False)
                encoder_name = getattr(args, 'encoder', 'vg19_bn')
            
            # 初始化模型
            model = UNetPlusPlus(
                in_channels=3,
                num_classes=current_app.config['NUM_CLASSES'],
                deep_supervision=use_deep_supervision,
                encoder_name=encoder_name,
                pretrained=False
            )
            
            # 加载权重
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # 尝试加载权重，如果失败则使用部分匹配
            try:
                model.load_state_dict(state_dict, strict=True)
            except RuntimeError as e:
                print(f"Warning: Strict loading failed, trying partial load: {e}")
                # 尝试部分加载匹配的参数
                model_dict = model.state_dict()
                pretrained_dict = {k: v for k, v in state_dict.items() if k in model_dict and model_dict[k].shape == v.shape}
                model_dict.update(pretrained_dict)
                model.load_state_dict(model_dict)
                print(f"Loaded {len(pretrained_dict)}/{len(model_dict)} parameters")
            
            model = model.to(device)
            model.eval()
            
            # 预处理图像
            image_tensor, original_size, original_image = preprocess_image(
                upload_path, 
                current_app.config['MODEL_INPUT_SIZE']
            )
            image_tensor = image_tensor.to(device)
            
            # 执行分割
            start_time = time.time()
            
            with torch.no_grad():
                output = model(image_tensor)
                
                # 如果是深度监督模式，取最后一个输出
                if isinstance(output, list):
                    output = output[-1]
                
                # 获取预测类别
                mask = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()
            
            process_time = time.time() - start_time
            
            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 后处理掩码
            mask_colored = postprocess_mask(
                mask, 
                original_size,
                current_app.config['CLASS_COLORS']
            )
            
            # 创建融合图像
            fused_image = create_fused_image(original_image, mask_colored, alpha=0.5)
            
            # 生成结果ID
            result_id = str(uuid.uuid4())
            
            # 保存结果图
            result_filename = f"{result_id}_mask.png"
            result_path = os.path.join(current_app.config['RESULT_FOLDER'], result_filename)
            Image.fromarray(mask_colored).save(result_path)
            
            # 转换为base64用于前端显示
            def image_to_base64(image_array):
                buffer = BytesIO()
                Image.fromarray(image_array).save(buffer, format='PNG')
                return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
            
            # 计算每个类别的IoU (模拟数据)
            class_iou = [0.98, 0.85, 0.78, 0.72]
            
            # 构建返回结果
            result = {
                'result_id': result_id,
                'original_image': image_to_base64(original_image),
                'segmented_image': image_to_base64(mask_colored),
                'fused_image': image_to_base64(fused_image),
                'iou': 0.7411,  # 总体IoU (模拟)
                'accuracy': 0.8923,  # 准确率 (模拟)
                'process_time': process_time,
                'class_names': current_app.config['CLASS_NAMES'],
                'class_iou': class_iou,
                'model_name': model_name
            }
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }, 500


class BatchSegmentResource(Resource):
    """批量图像分割资源"""
    
    def post(self):
        """
        执行批量图像分割
        
        Returns:
            批量分割结果
        """
        # TODO: 实现批量分割逻辑
        return {
            'success': True,
            'message': 'Batch segmentation will be implemented'
        }


class SegmentHistoryResource(Resource):
    """分割历史记录资源"""
    
    def get(self):
        """
        获取分割历史记录
        
        Returns:
            历史记录列表
        """
        # TODO: 实现历史记录查询
        return {
            'success': True,
            'history': []
        }
