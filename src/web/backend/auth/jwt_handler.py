"""
JWT 认证处理器
处理 JWT token 的签发、验证和刷新
"""
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

from flask import request, jsonify, current_app
import jwt


class JWTHandler:
    """JWT 认证处理器"""

    def __init__(self, secret_key: str = None, algorithm: str = 'HS256'):
        """
        初始化 JWT 处理器

        Args:
            secret_key: JWT 签名密钥，默认从环境变量或 Flask config 获取
            algorithm: 签名算法
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        # Token 过期时间配置
        self.access_token_expires = timedelta(hours=1)  # 访问令牌 1 小时
        self.refresh_token_expires = timedelta(days=7)  # 刷新令牌 7 天

    def _get_secret_key(self) -> str:
        """获取密钥"""
        if self.secret_key:
            return self.secret_key
        if hasattr(current_app, 'config'):
            return current_app.config.get('SECRET_KEY', 'default-secret-key')
        return os.environ.get('SECRET_KEY', 'default-secret-key')

    def generate_token(self, user_id: str, username: str, role: str = 'user',
                       expires_delta: timedelta = None) -> str:
        """
        生成访问令牌

        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            expires_delta: 过期时间增量

        Returns:
            JWT token 字符串
        """
        if expires_delta is None:
            expires_delta = self.access_token_expires

        payload = {
            'sub': user_id,
            'username': username,
            'role': role,
            'type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + expires_delta
        }

        return jwt.encode(payload, self._get_secret_key(), algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: str) -> str:
        """
        生成刷新令牌

        Args:
            user_id: 用户ID

        Returns:
            刷新令牌字符串
        """
        payload = {
            'sub': user_id,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.refresh_token_expires
        }

        return jwt.encode(payload, self._get_secret_key(), algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌

        Args:
            token: JWT token 字符串

        Returns:
            解码后的 payload，验证失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                self._get_secret_key(),
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token 已过期
        except jwt.InvalidTokenError:
            return None  # Token 无效

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        使用刷新令牌获取新的访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            新的访问令牌，失败返回 None
        """
        payload = self.verify_token(refresh_token)

        if payload is None:
            return None

        if payload.get('type') != 'refresh':
            return None

        user_id = payload.get('sub')
        if not user_id:
            return None

        # 生成新的访问令牌
        return self.generate_token(user_id=user_id, username=user_id)

    def extract_token_from_header(self) -> Optional[str]:
        """
        从请求头提取 token

        Returns:
            Token 字符串，未找到返回 None
        """
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # 移除 'Bearer ' 前缀

        return None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        获取当前认证用户

        Returns:
            用户信息字典，未认证返回 None
        """
        token = self.extract_token_from_header()
        if not token:
            return None

        payload = self.verify_token(token)
        if not payload:
            return None

        return {
            'user_id': payload.get('sub'),
            'username': payload.get('username'),
            'role': payload.get('role', 'user')
        }


# 全局 JWT 处理器实例
_jwt_handler: Optional[JWTHandler] = None


def get_jwt_handler() -> JWTHandler:
    """
    获取 JWT 处理器单例

    Returns:
        JWTHandler 实例
    """
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler()
    return _jwt_handler