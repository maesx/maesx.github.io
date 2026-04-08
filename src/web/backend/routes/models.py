"""
模型管理API路由
"""
import os
from flask import request, jsonify, current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename

from src.web.backend.services.model_service import get_model_service


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
        
        Args:
            model_name: 模型名称
            
        Returns:
            删除结果
        """
        try:
            model_service = get_model_service(current_app.config['CHECKPOINT_FOLDER'])
            success = model_service.delete_model(model_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Model {model_name} deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Failed to delete model {model_name}'
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
        
        Returns:
            上传结果
        """
        try:
            # 检查是否有文件
            if 'model_file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No model file provided'
                }), 400
            
            file = request.files['model_file']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # 检查文件扩展名
            if not file.filename.endswith('.pth'):
                return jsonify({
                    'success': False,
                    'error': 'Only .pth files are allowed'
                }), 400
            
            # 获取模型名称
            model_name = request.form.get('model_name')
            if not model_name:
                model_name = os.path.splitext(file.filename)[0]
            
            # 安全的文件名
            filename = secure_filename(f"{model_name}.pth")
            save_path = os.path.join(current_app.config['CHECKPOINT_FOLDER'], filename)
            
            # 检查文件是否已存在
            if os.path.exists(save_path):
                return jsonify({
                    'success': False,
                    'error': f'Model {model_name} already exists'
                }), 400
            
            # 保存文件
            file.save(save_path)
            
            # 验证模型文件
            try:
                import torch
                torch.load(save_path, map_location='cpu', weights_only=False)
            except Exception as e:
                # 删除无效文件
                os.remove(save_path)
                return jsonify({
                    'success': False,
                    'error': f'Invalid model file: {str(e)}'
                }), 400
            
            return jsonify({
                'success': True,
                'message': 'Model uploaded successfully',
                'model_name': model_name,
                'path': save_path
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
