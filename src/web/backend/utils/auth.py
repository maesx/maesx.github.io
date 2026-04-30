"""
认证工具函数
提供token验证和用户权限检查
"""
from functools import wraps
from flask import request


def token_required(f):
    """
    Token验证装饰器
    
    验证请求头中的Authorization token
    如果valid，将user_id传递给被装饰的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # 格式: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return {'success': False, 'message': 'Token格式错误'}, 401
        
        if not token:
            return {'success': False, 'message': '缺少认证Token'}, 401
        
        # 简化版本：验证token是否为demo-token（实际项目应该验证JWT或查询数据库）
        if token != 'demo-token-12345':
            return {'success': False, 'message': 'Token无效或已过期'}, 401
        
        # 从token中提取user_id（这里使用固定的demo用户ID）
        user_id = 1
        
        # 将user_id传递给被装饰的函数
        return f(user_id, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    管理员权限装饰器
    
    验证用户是否为管理员
    """
    @wraps(f)
    @token_required
    def decorated(user_id, *args, **kwargs):
        # 简化版本：demo用户默认为管理员
        # 实际项目应该查询数据库验证用户角色
        return f(user_id, *args, **kwargs)
    
    return decorated
