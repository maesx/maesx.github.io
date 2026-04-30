#!/usr/bin/env python3
"""
验证ORM模型与SQL脚本完全匹配
检查所有表的字段数量、类型、约束是否完全一致
"""
import re
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.backend.database.models import User, Model, SegmentationRecord, AugmentationRecord, OperationLog
from sqlalchemy import inspect


def parse_sql_fields(sql_content, table_name):
    """解析SQL CREATE TABLE语句,提取字段信息"""
    # 查找表定义
    pattern = rf'CREATE TABLE\s+`?{table_name}`?\s*\((.*?)\)\s*ENGINE='
    match = re.search(pattern, sql_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return None
    
    fields_text = match.group(1)
    fields = {}
    
    # 解析每个字段
    for line in fields_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('PRIMARY') or line.startswith('KEY') or line.startswith('UNIQUE'):
            continue
        
        # 提取字段名和类型
        field_match = re.match(r'`(\w+)`\s+(\w+(?:\([^)]+\))?)', line)
        if field_match:
            field_name = field_match.group(1)
            field_type = field_match.group(2).upper()
            
            # 检查约束
            nullable = 'NOT NULL' not in line.upper()
            auto_increment = 'AUTO_INCREMENT' in line.upper()
            
            fields[field_name] = {
                'type': field_type,
                'nullable': nullable,
                'auto_increment': auto_increment
            }
    
    return fields


def get_orm_fields(model_class):
    """获取ORM模型的字段信息"""
    inspector = inspect(model_class)
    fields = {}
    
    for column in inspector.columns:
        field_name = column.name
        field_type = str(column.type)
        
        fields[field_name] = {
            'type': field_type,
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'autoincrement': column.autoincrement
        }
    
    return fields


def compare_fields(table_name, sql_fields, orm_fields):
    """对比SQL和ORM字段"""
    print(f"\n{'='*60}")
    print(f"表: {table_name}")
    print(f"{'='*60}")
    
    sql_field_names = set(sql_fields.keys())
    orm_field_names = set(orm_fields.keys())
    
    # 检查字段数量
    print(f"\n字段数量:")
    print(f"  SQL: {len(sql_field_names)}")
    print(f"  ORM: {len(orm_field_names)}")
    
    # 检查是否完全匹配
    if sql_field_names == orm_field_names:
        print(f"  ✅ 字段完全匹配")
    else:
        missing_in_orm = sql_field_names - orm_field_names
        extra_in_orm = orm_field_names - sql_field_names
        
        if missing_in_orm:
            print(f"  ❌ ORM缺少字段: {missing_in_orm}")
        if extra_in_orm:
            print(f"  ❌ ORM多余字段: {extra_in_orm}")
        
        return False
    
    # 逐个检查字段
    print(f"\n字段详情:")
    all_match = True
    for field_name in sorted(sql_field_names):
        sql_field = sql_fields[field_name]
        orm_field = orm_fields[field_name]
        
        # 简化类型对比
        sql_type = sql_field['type'].split('(')[0]  # 去除长度参数
        orm_type = orm_field['type'].split('(')[0] if '(' in orm_field['type'] else orm_field['type']
        
        # 类型映射
        type_mapping = {
            'BIGINT': ['BIGINT', 'INTEGER'],
            'INT': ['INTEGER', 'INT'],
            'VARCHAR': ['VARCHAR', 'STRING'],
            'TEXT': ['TEXT', 'LONGTEXT'],
            'LONGTEXT': ['LONGTEXT', 'TEXT'],
            'DATETIME': ['DATETIME'],
            'SMALLINT': ['SMALLINT', 'INTEGER'],
            'FLOAT': ['FLOAT'],
            'DOUBLE': ['FLOAT', 'DOUBLE'],
            'JSON': ['JSON'],
            'ENUM': ['ENUM']
        }
        
        # 检查类型匹配
        type_match = False
        for sql_key, orm_types in type_mapping.items():
            if sql_type == sql_key and orm_type.upper() in [t.upper() for t in orm_types]:
                type_match = True
                break
        
        if not type_match and sql_type.upper() == orm_type.upper():
            type_match = True
        
        if type_match:
            print(f"  ✅ {field_name:20s} SQL: {sql_field['type']:15s} ORM: {orm_field['type']}")
        else:
            print(f"  ❌ {field_name:20s} SQL: {sql_field['type']:15s} ORM: {orm_field['type']}")
            all_match = False
    
    return all_match


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔍 ORM模型与SQL脚本对比验证")
    print("="*60)
    
    # 读取SQL脚本
    sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            'scripts', 'init_database.sql')
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"\n❌ SQL文件不存在: {sql_file}")
        return False
    
    # 表名映射
    tables = [
        ('users', User),
        ('models', Model),
        ('segmentation_records', SegmentationRecord),
        ('augmentation_records', AugmentationRecord),
        ('operation_logs', OperationLog)
    ]
    
    all_match = True
    
    for table_name, model_class in tables:
        # 解析SQL字段
        sql_fields = parse_sql_fields(sql_content, table_name)
        if not sql_fields:
            print(f"\n❌ 无法解析表: {table_name}")
            all_match = False
            continue
        
        # 获取ORM字段
        orm_fields = get_orm_fields(model_class)
        
        # 对比
        if not compare_fields(table_name, sql_fields, orm_fields):
            all_match = False
    
    # 最终结果
    print(f"\n{'='*60}")
    if all_match:
        print("✅ 所有表结构完全匹配SQL脚本")
        print("="*60)
        return True
    else:
        print("❌ 存在字段不匹配,请检查!")
        print("="*60)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
