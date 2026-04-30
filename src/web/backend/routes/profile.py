"""
个人中心API路由
提供用户资料管理、密码修改、头像上传等功能
"""
from flask_restful import Resource, reqparse
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import re
from datetime import datetime

from src.web.backend.database.session import get_db
from src.web.backend.database.models.user import User
from src.web.backend.utils.auth import token_required


class ProfileResource(Resource):
    """个人资料资源"""
    
    method_decorators = {'get': [token_required], 'put': [token_required]}
    
    def get(self, user_id):
        """
        获取用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户资料信息
        """
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            return {
                'success': True,
                'user': user.to_dict()
            }
        except Exception as e:
            return {'success': False, 'message': f'获取用户资料失败: {str(e)}'}, 500
    
    def put(self, user_id):
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            更新结果
        """
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, help='用户昵称')
        parser.add_argument('email', type=str, help='邮箱地址')
        args = parser.parse_args()
        
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            # 更新昵称
            if args.get('nickname'):
                user.nickname = args['nickname']
            
            # 更新邮箱（需要验证唯一性）
            if args.get('email') and args['email'] != user.email:
                # 验证邮箱格式
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', args['email']):
                    return {'success': False, 'message': '邮箱格式不正确'}, 400
                
                # 检查邮箱是否已被使用
                existing_user = db.query(User).filter(
                    User.email == args['email'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return {'success': False, 'message': '该邮箱已被使用'}, 400
                
                user.email = args['email']
            
            user.updated_at = datetime.now()
            db.commit()
            
            return {
                'success': True,
                'message': '资料更新成功',
                'user': user.to_dict()
            }
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500


class AvatarResource(Resource):
    """头像管理资源"""
    
    method_decorators = {'post': [token_required], 'delete': [token_required]}
    
    def post(self, user_id):
        """
        上传头像
        
        Args:
            user_id: 用户ID
            
        Returns:
            上传结果
        """
        try:
            # 获取base64编码的头像数据
            data = request.get_json()
            avatar_data = data.get('avatar')
            
            if not avatar_data:
                return {'success': False, 'message': '未提供头像数据'}, 400
            
            # 验证base64数据大小（限制为2MB）
            # base64数据约比原始数据大33%，所以base64限制为2.7MB
            if len(avatar_data) > 2.7 * 1024 * 1024:
                return {'success': False, 'message': '头像大小不能超过2MB'}, 400
            
            db = get_db()
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            user.avatar = avatar_data
            user.updated_at = datetime.now()
            db.commit()
            
            return {
                'success': True,
                'message': '头像上传成功',
                'avatar': avatar_data
            }
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'上传失败: {str(e)}'}, 500
    
    def delete(self, user_id):
        """
        删除头像
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除结果
        """
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            user.avatar = None
            user.updated_at = datetime.now()
            db.commit()
            
            return {
                'success': True,
                'message': '头像删除成功'
            }
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}, 500


class PasswordResource(Resource):
    """密码管理资源"""
    
    method_decorators = {'put': [token_required]}
    
    def put(self, user_id):
        """
        修改密码
        
        Args:
            user_id: 用户ID
            
        Returns:
            修改结果
        """
        parser = reqparse.RequestParser()
        parser.add_argument('old_password', type=str, required=True, help='原密码')
        parser.add_argument('new_password', type=str, required=True, help='新密码')
        parser.add_argument('confirm_password', type=str, required=True, help='确认密码')
        args = parser.parse_args()
        
        # 验证新密码
        if len(args['new_password']) < 8:
            return {'success': False, 'message': '新密码长度至少8位'}, 400
        
        if args['new_password'] != args['confirm_password']:
            return {'success': False, 'message': '两次密码输入不一致'}, 400
        
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            # 验证原密码
            if not check_password_hash(user.password_hash, args['old_password'] + user.salt):
                return {'success': False, 'message': '原密码错误'}, 400
            
            # 更新密码
            user.password_hash = generate_password_hash(args['new_password'] + user.salt)
            user.updated_at = datetime.now()
            db.commit()
            
            return {
                'success': True,
                'message': '密码修改成功'
            }
        except Exception as e:
            db.rollback()
            return {'success': False, 'message': f'修改失败: {str(e)}'}, 500
