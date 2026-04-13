"""
数据增强API路由
"""
import os
import uuid
import base64
import zipfile
import json
import random
from io import BytesIO
from datetime import datetime
from flask import request, current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image

from src.web.backend.services.augmentation_service import get_augmentation_service
from src.web.backend.database.session import get_db_session
from src.web.backend.database.models.augmentation import AugmentationRecord
from src.web.backend.database.models.augmentation_result import AugmentationResult
from src.web.backend.config.database import db_config


def image_to_base64(image_array):
    """将numpy数组转换为base64字符串"""
    if isinstance(image_array, np.ndarray):
        pil_img = Image.fromarray(image_array.astype('uint8'))
    else:
        pil_img = image_array

    buffer = BytesIO()
    pil_img.save(buffer, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"


def save_augmentation_to_db(original_image, augmented_images, methods_used):
    """
    保存增强结果到数据库

    Args:
        original_image: 原图numpy数组
        augmented_images: 增强结果列表 [{'image': base64, 'augmentation_type': str}, ...]
        methods_used: 使用的增强方法列表

    Returns:
        记录ID，如果保存失败返回None
    """
    if not db_config.use_mysql:
        return None

    try:
        with get_db_session() as session:
            if session is None:
                return None

            # 创建主记录
            record = AugmentationRecord(
                user_id=None,  # 暂无用户系统
                original_image=image_to_base64(original_image),
                augmentation_type=' + '.join(methods_used),
                methods_used=methods_used,
                num_variations=len(augmented_images),
                image_width=original_image.shape[1],
                image_height=original_image.shape[0],
                image_format='PNG',
                file_size=len(image_to_base64(original_image)),
                status=1
            )
            session.add(record)
            session.flush()  # 获取record.id

            # 创建结果记录
            for idx, aug in enumerate(augmented_images):
                result = AugmentationResult(
                    record_id=record.id,
                    result_image=aug.get('image', ''),
                    variation_index=idx,
                    image_width=original_image.shape[1],
                    image_height=original_image.shape[0],
                    image_format='PNG'
                )
                session.add(result)

            return record.id

    except Exception as e:
        print(f"[Augmentation] 保存到数据库失败: {e}")
        return None


class AugmentationPreviewResource(Resource):
    """数据增强预览资源"""
    
    def post(self):
        """
        生成数据增强预览
        
        Request:
            - images: 图片文件列表
            - augmentations: 增强方式列表（JSON字符串）
            
        Returns:
            增强后的图片预览
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
            
            # 获取增强方式
            import json
            augmentations_str = request.form.get('augmentations', '[]')
            try:
                augmentations = json.loads(augmentations_str)
            except:
                augmentations = []
            
            if not augmentations:
                return {
                    'success': False,
                    'error': 'No augmentation methods selected'
                }, 400
            
            print(f"[Augmentation] 开始处理 - 图片数量: {len(files)}, 增强方式: {augmentations}")
            
            # 获取增强服务
            aug_service = get_augmentation_service()
            
            # 处理每张图片
            results = []
            
            for idx, file in enumerate(files):
                try:
                    # 读取图片
                    image_bytes = file.read()
                    pil_image = Image.open(BytesIO(image_bytes))
                    
                    # 转换为RGB（如果是RGBA）
                    if pil_image.mode == 'RGBA':
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        background.paste(pil_image, mask=pil_image.split()[3])
                        pil_image = background
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # 转换为numpy数组
                    image_array = np.array(pil_image)
                    
                    # 生成增强效果（2-3种）
                    num_variations = random.randint(2, 3)
                    augmented_images = aug_service.augment_image(
                        image_array,
                        augmentations,
                        num_variations
                    )
                    
                    # 添加到结果
                    results.append({
                        'original_filename': secure_filename(file.filename),
                        'original_image': image_to_base64(image_array),
                        'augmented_images': augmented_images
                    })

                    # 保存到数据库（如果启用MySQL）
                    save_augmentation_to_db(image_array, augmented_images, augmentations)

                    print(f"[Augmentation] 处理图片 {idx + 1}/{len(files)}: {file.filename}")
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"[Augmentation] 处理图片失败 {file.filename}: {str(e)}")
            
            # 计算总数
            total_count = sum(len(r['augmented_images']) for r in results)
            
            return {
                'success': True,
                'results': results,
                'total_count': total_count,
                'message': f'成功生成 {len(results)} 张图片的增强效果，共 {total_count} 个变体'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }, 500


# 内存中存储增强结果（用于下载）
_augmentation_results_cache = {}
_zipped_results_cache = {}


class AugmentationDownloadResource(Resource):
    """增强结果下载资源"""
    
    def post(self):
        """
        打包并下载所有增强结果（ZIP格式）
        
        Request:
            - results: 增强结果数据（从前端传回）
            
        Returns:
            ZIP文件下载
        """
        try:
            import json
            from flask import send_file
            
            # 获取前端传回的结果数据
            results_json = request.form.get('results', '[]')
            try:
                results = json.loads(results_json)
            except:
                return {
                    'success': False,
                    'error': 'Invalid results data'
                }, 400
            
            if not results:
                return {
                    'success': False,
                    'error': 'No results to download'
                }, 400
            
            # 创建ZIP文件
            zip_filename = f"augmentation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(current_app.config['RESULT_FOLDER'], zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for result_group in results:
                    original_filename = result_group['original_filename']
                    base_name = os.path.splitext(original_filename)[0]
                    
                    # 保存原图
                    if result_group.get('original_image'):
                        img_data = result_group['original_image'].split(',')[1]
                        img_bytes = base64.b64decode(img_data)
                        zipf.writestr(f"{base_name}/original.png", img_bytes)
                    
                    # 保存增强图片
                    for aug_idx, aug in enumerate(result_group.get('augmented_images', [])):
                        if aug.get('image'):
                            img_data = aug['image'].split(',')[1]
                            img_bytes = base64.b64decode(img_data)
                            aug_name = aug['augmentation_type'].replace(' + ', '_')
                            zipf.writestr(
                                f"{base_name}/augmented_{aug_idx + 1}_{aug_name}.png",
                                img_bytes
                            )
            
            # 发送文件
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }, 500
