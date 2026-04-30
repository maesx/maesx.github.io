"""
系统设置API路由
提供系统配置管理、存储管理、日志查看等功能
"""
from flask_restful import Resource, reqparse
from flask import request
import os
import json
import shutil
from datetime import datetime
from pathlib import Path


class SystemConfigResource(Resource):
    """系统配置资源"""
    
    CONFIG_FILE = 'config/system_settings.json'
    
    def get(self):
        """
        获取系统配置
        
        Returns:
            系统配置信息
        """
        try:
            config = self._load_config()
            return {
                'success': True,
                'config': config
            }
        except Exception as e:
            return {'success': False, 'message': f'获取配置失败: {str(e)}'}, 500
    
    def put(self):
        """
        更新系统配置
        
        Returns:
            更新结果
        """
        try:
            data = request.get_json()
            config = self._load_config()
            
            # 更新配置
            if 'general' in data:
                config['general'].update(data['general'])
            if 'storage' in data:
                config['storage'].update(data['storage'])
            if 'model' in data:
                config['model'].update(data['model'])
            
            config['updated_at'] = datetime.now().isoformat()
            
            # 保存配置
            self._save_config(config)
            
            return {
                'success': True,
                'message': '配置更新成功',
                'config': config
            }
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}, 500
    
    def _load_config(self):
        """加载配置"""
        default_config = {
            'general': {
                'app_name': '图像分割可视化平台',
                'default_language': 'zh-CN',
                'upload_max_size': 50,  # MB
                'session_timeout': 3600,  # 秒
                'enable_gpu': True,
                'auto_save': True
            },
            'storage': {
                'upload_dir': 'uploads',
                'result_dir': 'results',
                'model_dir': 'checkpoints',
                'max_storage_gb': 100,
                'auto_cleanup': True,
                'retention_days': 30
            },
            'model': {
                'default_model': 'best_model.pth',
                'default_encoder': 'vgg19',
                'default_num_classes': 4,
                'batch_size': 4,
                'image_size': [512, 512],
                'use_deep_supervision': True
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 确保配置目录存在
        os.makedirs('config', exist_ok=True)
        
        if not os.path.exists(self.CONFIG_FILE):
            return default_config
        
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_config
    
    def _save_config(self, config):
        """保存配置"""
        os.makedirs('config', exist_ok=True)
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class StorageInfoResource(Resource):
    """存储信息资源"""
    
    def get(self):
        """
        获取存储空间信息
        
        Returns:
            存储空间使用情况
        """
        try:
            # 使用默认目录路径
            directories = {
                'uploads': 'uploads',
                'results': 'outputs/results',
                'models': 'outputs/checkpoints',
                'logs': 'outputs/logs'
            }
            
            storage_info = {}
            total_size = 0
            total_files = 0
            
            for name, path in directories.items():
                if os.path.exists(path):
                    size, files = self._get_dir_info(path)
                    storage_info[name] = {
                        'path': path,
                        'size_mb': round(size / (1024 * 1024), 2),
                        'files': files
                    }
                    total_size += size
                    total_files += files
                else:
                    storage_info[name] = {
                        'path': path,
                        'size_mb': 0,
                        'files': 0
                    }
            
            # 获取磁盘总空间
            disk_usage = shutil.disk_usage('/')
            disk_total_gb = round(disk_usage.total / (1024**3), 2)
            disk_used_gb = round(disk_usage.used / (1024**3), 2)
            disk_free_gb = round(disk_usage.free / (1024**3), 2)
            
            return {
                'success': True,
                'storage': {
                    'directories': storage_info,
                    'total': {
                        'size_mb': round(total_size / (1024 * 1024), 2),
                        'files': total_files
                    },
                    'disk': {
                        'total_gb': disk_total_gb,
                        'used_gb': disk_used_gb,
                        'free_gb': disk_free_gb,
                        'used_percent': round((disk_used_gb / disk_total_gb) * 100, 1)
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'获取存储信息失败: {str(e)}'}, 500
    
    def _get_dir_info(self, path):
        """获取目录大小和文件数"""
        total_size = 0
        total_files = 0
        
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    total_files += 1
                except:
                    continue
        
        return total_size, total_files


class LogsResource(Resource):
    """日志资源"""
    
    def get(self):
        """
        获取系统日志
        
        Returns:
            日志列表
        """
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=100, help='返回条数')
        parser.add_argument('level', type=str, help='日志级别')
        args = parser.parse_args()
        
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                return {
                    'success': True,
                    'logs': [],
                    'message': '暂无日志'
                }
            
            logs = []
            log_files = sorted(
                [f for f in os.listdir(log_dir) if f.endswith('.log')],
                reverse=True
            )
            
            for log_file in log_files[:3]:  # 只查看最近的3个日志文件
                log_path = os.path.join(log_dir, log_file)
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                    for line in lines[-args['limit']:]:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 简单的日志解析
                        log_entry = {
                            'file': log_file,
                            'content': line,
                            'timestamp': self._extract_timestamp(line),
                            'level': self._extract_level(line)
                        }
                        
                        # 级别过滤
                        if args.get('level') and log_entry['level'] != args['level']:
                            continue
                        
                        logs.append(log_entry)
            
            # 限制总条数
            logs = logs[-args['limit']:]
            
            return {
                'success': True,
                'logs': logs,
                'total': len(logs)
            }
        except Exception as e:
            return {'success': False, 'message': f'获取日志失败: {str(e)}'}, 500
    
    def _extract_timestamp(self, line):
        """提取时间戳"""
        try:
            # 格式: 2026-04-27 10:30:45
            import re
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            return match.group(1) if match else None
        except:
            return None
    
    def _extract_level(self, line):
        """提取日志级别"""
        line_upper = line.upper()
        if 'ERROR' in line_upper or 'CRITICAL' in line_upper:
            return 'ERROR'
        elif 'WARNING' in line_upper or 'WARN' in line_upper:
            return 'WARNING'
        elif 'INFO' in line_upper:
            return 'INFO'
        elif 'DEBUG' in line_upper:
            return 'DEBUG'
        else:
            return 'UNKNOWN'
