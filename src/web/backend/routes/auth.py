"""
认证API路由（无实际验证）
"""
from flask_restful import Resource


class LoginResource(Resource):
    """登录资源"""
    
    def post(self):
        """
        用户登录（不验证，直接返回成功）
        
        Returns:
            登录成功信息和token
        """
        # 不验证用户名密码，直接返回成功
        return {
            'success': True,
            'message': 'Login successful',
            'token': 'demo-token-12345',
            'user': {
                'id': 1,
                'name': 'Demo User',
                'email': 'demo@example.com',
                'role': 'admin'
            }
        }
