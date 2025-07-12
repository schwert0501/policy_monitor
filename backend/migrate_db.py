#!/usr/bin/env python
"""
数据库迁移脚本
"""

import os
import sys
import logging
import sqlite3
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_db():
    """执行数据库迁移"""
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'tax_policy.db')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    logger.info(f"使用SQLite数据库: {db_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查policies表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='policies'")
        if not cursor.fetchone():
            logger.info("policies表不存在，请先初始化数据库")
            return
        
        # 迁移1: 添加content_md5字段到policies表
        try:
            cursor.execute("PRAGMA table_info(policies)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'content_md5' not in column_names:
                logger.info("添加content_md5字段到policies表")
                cursor.execute("ALTER TABLE policies ADD COLUMN content_md5 VARCHAR(32)")
                conn.commit()
                logger.info("content_md5字段添加成功")
            else:
                logger.info("content_md5字段已存在")
        except Exception as e:
            logger.error(f"添加content_md5字段时出错: {str(e)}")
            
        # 迁移2: 添加source_url字段到policies表
        try:
            cursor.execute("PRAGMA table_info(policies)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'source_url' not in column_names:
                logger.info("添加source_url字段到policies表")
                cursor.execute("ALTER TABLE policies ADD COLUMN source_url VARCHAR(255)")
                conn.commit()
                logger.info("source_url字段添加成功")
            else:
                logger.info("source_url字段已存在")
        except Exception as e:
            logger.error(f"添加source_url字段时出错: {str(e)}")
            
        # 关闭连接
        conn.close()
        
        logger.info("数据库迁移完成")
    except Exception as e:
        logger.error(f"数据库迁移时出错: {str(e)}")

if __name__ == "__main__":
    migrate_db() 