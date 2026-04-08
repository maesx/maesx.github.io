"""
Flask应用主入口
图像分割可视化Web应用
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api

from src.web.backend.config import Config


def create_app(config_class=Config):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CHECKPOINT_FOLDER'], exist_ok=True)
    
    # 初始化API
    api = Api(app)
    
    # 注册路由
    from src.web.backend.routes.models import ModelsResource, ModelDetailResource, ModelUploadResource
    from src.web.backend.routes.segment import SegmentResource, BatchSegmentResource, SegmentHistoryResource
    from src.web.backend.routes.visualization import VisualizationResource, GPUMonitorResource
    from src.web.backend.routes.auth import LoginResource
    from src.web.backend.routes.augmentation import AugmentationPreviewResource
    
    # API路由
    api.add_resource(LoginResource, '/api/login')
    
    # 模型管理
    api.add_resource(ModelsResource, '/api/models')
    api.add_resource(ModelDetailResource, '/api/models/<string:model_name>')
    api.add_resource(ModelUploadResource, '/api/models/upload')
    
    # 图像分割
    api.add_resource(SegmentResource, '/api/segment')
    api.add_resource(BatchSegmentResource, '/api/segment/batch')
    api.add_resource(SegmentHistoryResource, '/api/segment/history')
    
    # 可视化
    api.add_resource(VisualizationResource, '/api/visualization/<string:result_id>')
    api.add_resource(GPUMonitorResource, '/api/gpu/status')
    
    # 数据增强预览
    api.add_resource(AugmentationPreviewResource, '/api/augmentation/preview')
    
    # 健康检查
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    # 根路径
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'name': '图像分割可视化平台',
            'version': '1.0.0',
            'description': 'U-Net++ & YOLOv8-seg 图像分割系统',
            'endpoints': {
                'models': '/api/models',
                'segment': '/api/segment',
                'health': '/api/health'
            }
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("🚀 图像分割可视化平台")
    print("="*60)
    print(f"📡 API服务器: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"🔧 调试模式: {'启用' if app.config['DEBUG'] else '禁用'}")
    print(f"📁 上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"📊 结果目录: {app.config['RESULT_FOLDER']}")
    print(f"🤖 模型目录: {app.config['CHECKPOINT_FOLDER']}")
    print("="*60 + "\n")
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
