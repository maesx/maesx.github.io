"""
模型管理API路由
"""
import os
from datetime import datetime
from flask import request, jsonify, current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename

from src.web.backend.services.model_service import get_model_service
from src.web.backend.auth.decorators import require_role
from src.web.backend.database.session import get_db_session
from src.web.backend.database.models.model import Model
from src.web.backend.database.models.log import OperationLog


# 默认模型列表（不允许删除）
DEFAULT_MODELS = ['best_model']


def _log_operation(user_id, operation_type, resource_type, resource_id, detail, ip_address=None, user_agent=None):
    """记录操作日志"""
    try:
        with get_db_session() as session:
            if session is None:
                return
            log = OperationLog(
                user_id=user_id,
                operation_type=operation_type,
                resource_type=resource_type,
                resource_id=resource_id,
                operation_detail=detail,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(log)
    except Exception as e:
        print(f"[Models] 记录操作日志失败: {e}")


def _save_model_to_db(model_info, user_id=None):
    """保存模型信息到数据库"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            # 检查是否已存在
            existing = session.query(Model).filter(
                Model.model_name == model_info['name']
            ).first()

            if existing:
                # 更新现有记录
                existing.model_path = model_info.get('path', '')
                existing.model_size = int(model_info.get('size_mb', 0) * 1024 * 1024)
                existing.updated_at = datetime.now()
                session.commit()
                return existing.id
            else:
                # 创建新记录
                model = Model(
                    model_name=model_info['name'],
                    model_type='segmentation',
                    model_path=model_info.get('path', ''),
                    model_size=int(model_info.get('size_mb', 0) * 1024 * 1024),
                    is_active=1,
                    is_default=0,
                    is_latest=1,
                    performance_metrics={'iou': model_info.get('iou', 0)}
                )
                session.add(model)
                session.commit()
                return model.id
    except Exception as e:
        print(f"[Models] 保存模型到数据库失败: {e}")
        return None


def _delete_model_from_db(model_name):
    """从数据库删除模型记录"""
    try:
        with get_db_session() as session:
            if session is None:
                return False
            model = session.query(Model).filter(
                Model.model_name == model_name
            ).first()
            if model:
                session.delete(model)
                session.commit()
                return True
            return False
    except Exception as e:
        print(f"[Models] 从数据库删除模型失败: {e}")
        return False


def _is_default_model(model_name):
    """检查是否为默认模型"""
    # 检查文件系统默认模型
    for default in DEFAULT_MODELS:
        if model_name == default or model_name.startswith(f"{default}_"):
            return True

    # 检查数据库中的默认模型
    try:
        with get_db_session() as session:
            if session is None:
                return False
            model = session.query(Model).filter(
                Model.model_name == model_name,
                Model.is_default == 1
            ).first()
            return model is not None
    except Exception as e:
        print(f"[Models] 检查默认模型失败: {e}")
        return False


def _get_model_id_from_db(model_name):
    """从数据库获取模型ID"""
    try:
        with get_db_session() as session:
            if session is None:
                return None
            model = session.query(Model).filter(
                Model.model_name == model_name
            ).first()
            return model.id if model else None
    except Exception as e:
        print(f"[Models] 获取模型ID失败: {e}")
        return None


class ModelsResource(Resource):
    """模型列表资源"""
    
    def get(self):
        """
        获取所有可用模型列表
        
        Returns:
            模型列表
        """
        try:
            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])
            models = model_service.get_model_list()
            
            return jsonify({
                'success': True,
                'models': models,
                'count': len(models)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


class ModelDetailResource(Resource):
    """单个模型详情资源"""

    def get(self, model_name):
        """
        获取单个模型的详细信息

        Args:
            model_name: 模型名称

        Returns:
            模型详细信息
        """
        try:
            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])
            models = model_service.get_model_list()

            # 查找指定模型
            model = next((m for m in models if m['name'] == model_name), None)

            if not model:
                return jsonify({
                    'success': False,
                    'error': f'Model {model_name} not found'
                }), 404

            # 添加是否为默认模型的标记
            model['is_default'] = _is_default_model(model_name)

            return jsonify({
                'success': True,
                'model': model
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def delete(self, model_name):
        """
        删除指定模型
        
        注意: 当前版本暂时移除管理员权限验证
        TODO: 在完善用户系统后恢复权限验证

        Args:
            model_name: 模型名称

        Returns:
            删除结果
        """
        try:
            # 检查是否为默认模型
            if _is_default_model(model_name):
                return jsonify({
                    'success': False,
                    'error': '系统默认模型不允许删除',
                    'code': 'CANNOT_DELETE_DEFAULT_MODEL'
                }), 403

            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])

            # 获取模型信息用于日志记录
            model_id = _get_model_id_from_db(model_name)

            success = model_service.delete_model(model_name)

            if success:
                # 从数据库删除记录
                _delete_model_from_db(model_name)

                # 记录操作日志
                _log_operation(
                    user_id=None,
                    operation_type='delete',
                    resource_type='model',
                    resource_id=model_id,
                    detail={'model_name': model_name},
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:255]
                )

                return jsonify({
                    'success': True,
                    'message': f'模型 {model_name} 删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'删除模型 {model_name} 失败'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


class ModelUploadResource(Resource):
    """模型上传资源"""

    def post(self):
        """
        上传自定义模型文件
        
        注意: 当前版本暂时移除管理员权限验证
        TODO: 在完善用户系统后恢复权限验证

        Returns:
            上传结果
        """
        try:
            # 检查是否有文件
            if 'model_file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '未提供模型文件',
                    'code': 'NO_FILE'
                }), 400

            file = request.files['model_file']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件',
                    'code': 'NO_FILE_SELECTED'
                }), 400

            # 检查文件扩展名
            if not (file.filename.endswith('.pth') or file.filename.endswith('.pt')):
                return jsonify({
                    'success': False,
                    'error': '仅支持 .pth 和 .pt 格式的模型文件',
                    'code': 'INVALID_FORMAT'
                }), 400

            # 获取模型名称
            model_name = request.form.get('model_name', '').strip()
            if not model_name:
                model_name = os.path.splitext(file.filename)[0]

            # 验证模型名称格式
            import re
            if not re.match(r'^[a-zA-Z0-9_\-]+$', model_name):
                return jsonify({
                    'success': False,
                    'error': '模型名称只能包含字母、数字、下划线和连字符',
                    'code': 'INVALID_MODEL_NAME'
                }), 400

            # 安全的文件名
            filename = secure_filename(f"{model_name}.pth")
            save_path = os.path.join(current_app.config['CHECKPOINT_FOLDER'], filename)

            # 检查文件是否已存在
            if os.path.exists(save_path):
                return jsonify({
                    'success': False,
                    'error': f'模型 {model_name} 已存在',
                    'code': 'MODEL_EXISTS'
                }), 400

            # 保存文件
            file.save(save_path)

            # 验证模型文件
            try:
                import torch
                checkpoint = torch.load(save_path, map_location='cpu', weights_only=True)
            except Exception as e:
                # 删除无效文件
                os.remove(save_path)
                return jsonify({
                    'success': False,
                    'error': f'无效的模型文件: {str(e)}',
                    'code': 'INVALID_MODEL'
                }), 400

            # 获取模型信息
            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])
            model_info = model_service._get_model_info(save_path)

            # JSON序列化处理
            if model_info:
                # 移除不可序列化的字段
                serializable_info = {
                    'name': model_info.get('name'),
                    'size': model_info.get('size'),
                    'size_mb': model_info.get('size_mb'),
                    'created_at': model_info.get('created_at'),
                    'type': model_info.get('type'),
                    'architecture': model_info.get('architecture'),
                    'iou': model_info.get('iou', 0.0),
                    'epoch': model_info.get('epoch'),
                    'use_fpn': model_info.get('use_fpn', False)
                }
                
                # 保存到数据库
                model_id = _save_model_to_db(model_info, user_id=None)

                # 记录操作日志
                _log_operation(
                    user_id=None,
                    operation_type='upload',
                    resource_type='model',
                    resource_id=model_id,
                    detail={
                        'model_name': model_name,
                        'file_size': model_info.get('size_mb', 0),
                        'iou': model_info.get('iou', 0)
                    },
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:255]
                )
            else:
                serializable_info = None

            return jsonify({
                'success': True,
                'message': '模型上传成功',
                'model_name': model_name,
                'model_info': serializable_info,
                'path': save_path
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
