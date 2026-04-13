"""
认证装饰器
用于保护需要认证的 API 端点
"""
from functools import wraps
from flask import jsonify, request

from .jwt_handler import get_jwt_handler


def require_auth(f):
    """
    认证装饰器
    要求请求必须携带有效的 JWT token

    被装饰的函数可以通过 kwargs['current_user'] 访问当前用户信息
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_handler = get_jwt_handler()

        # 提取并验证 token
        token = jwt_handler.extract_token_from_header()
        if not token:
            return jsonify({
                'success': False,
                'error': 'Missing authentication token',
                'code': 'AUTH_MISSING_TOKEN'
            }), 401

        # 验证 token
        user = jwt_handler.get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token',
                'code': 'AUTH_INVALID_TOKEN'
            }), 401

        # 将用户信息传递给被装饰的函数
        kwargs['current_user'] = user

        return f(*args, **kwargs)

    return decorated_function


def require_role(*roles):
    """
    角色验证装饰器
    要求用户具有指定角色

    Args:
        *roles: 允许的角色列表

    用法:
        @require_role('admin', 'moderator')
        def admin_only_endpoint(current_user=None):
            ...
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }), 401

            user_role = user.get('role', 'user')
            if user_role not in roles:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'code': 'AUTH_INSUFFICIENT_PERMISSIONS'
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def optional_auth(f):
    """
    可选认证装饰器
    如果提供了 token 则验证，否则继续执行（current_user 可能为 None）

    用法:
        @optional_auth
        def public_endpoint(current_user=None):
            if current_user:
                # 已认证用户的逻辑
            else:
                # 匿名用户的逻辑
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_handler = get_jwt_handler()

        # 尝试提取并验证 token
        token = jwt_handler.extract_token_from_header()
        user = None

        if token:
            user = jwt_handler.get_current_user()

        # 将用户信息传递给被装饰的函数（可能为 None）
        kwargs['current_user'] = user

        return f(*args, **kwargs)

    return decorated_function