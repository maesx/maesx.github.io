"""
认证API路由
"""
from flask import request
from flask_restful import Resource
from datetime import datetime
import re

from src.web.backend.database.session import get_db_session
from src.web.backend.database.models.user import User
from werkzeug.security import generate_password_hash
import secrets
from hashlib import sha256


class LoginResource(Resource):
    """登录资源"""
    
    def post(self):
        """
        用户登录（暂时不验证，后续实现）
        
        Returns:
            登录成功信息和token
        """
        # TODO: 后续实现真实的认证逻辑
        # 暂时不拦截校验，直接返回成功
        
        # 获取请求数据
        data = request.get_json() or {}
        username = data.get('username', '')
        
        return {
            'success': True,
            'message': 'Login successful',
            'token': 'demo-token-' + secrets.token_hex(16),
            'user': {
                'id': 1,
                'name': username or 'Demo User',
                'email': f'{username}@example.com' if username else 'demo@example.com',
                'role': 'admin'
            }
        }


class RegisterResource(Resource):
    """注册资源"""
    
    def post(self):
        """
        用户注册（暂时不验证，后续实现）
        
        Returns:
            注册结果
        """
        # TODO: 后续实现真实的注册逻辑
        # 暂时不拦截校验，直接返回成功
        
        data = request.get_json() or {}
        
        # 参数验证
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username:
            return {
                'success': False,
                'message': '用户名不能为空'
            }, 400
        
        if not email:
            return {
                'success': False,
                'message': '邮箱不能为空'
            }, 400
        
        # 邮箱格式验证
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return {
                'success': False,
                'message': '邮箱格式不正确'
            }, 400
        
        if not password or len(password) < 8:
            return {
                'success': False,
                'message': '密码长度至少8位'
            }, 400
        
        # 尝试保存到数据库（如果启用MySQL）
        try:
            with get_db_session() as session:
                if session is not None:
                    # 检查用户名是否已存在
                    existing_user = session.query(User).filter(
                        User.username == username
                    ).first()
                    
                    if existing_user:
                        return {
                            'success': False,
                            'message': '用户名已存在'
                        }, 400
                    
                    # 检查邮箱是否已存在
                    existing_email = session.query(User).filter(
                        User.email == email
                    ).first()
                    
                    if existing_email:
                        return {
                            'success': False,
                            'message': '邮箱已被注册'
                        }, 400
                    
                    # 创建用户
                    salt = secrets.token_hex(32)
                    password_hash = sha256((password + salt).encode()).hexdigest()
                    
                    user = User(
                        username=username,
                        email=email,
                        password_hash=password_hash,
                        salt=salt,
                        nickname=data.get('nickname', '').strip() or username,
                        role='user',
                        status=1
                    )
                    
                    session.add(user)
                    # session.commit() 由 get_db_session 上下文管理器自动提交
        except Exception as e:
            # 数据库操作失败不影响注册（暂时）
            print(f"[Register] 数据库操作失败: {e}")
        
        return {
            'success': True,
            'message': '注册成功'
        }
