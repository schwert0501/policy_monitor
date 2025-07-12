"""
数据库初始化脚本
"""

import os
import sys
import logging
from app import create_app
from app.models import db
from app.models.category import Category
from app.models.policy import Policy

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库"""
    logger.info("开始初始化数据库")
    
    # 创建应用实例
    app = create_app()
    
    # 确保instance目录存在
    os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        logger.info("已创建所有数据库表")
        
        # 添加默认分类
        if Category.query.count() == 0:
            logger.info("添加默认分类")
            categories = [
                Category(name='税收政策', description='税收相关政策法规'),
                Category(name='财政政策', description='财政相关政策法规'),
                Category(name='金融政策', description='金融相关政策法规')
            ]
            db.session.add_all(categories)
            db.session.commit()
            logger.info(f"已添加 {len(categories)} 个默认分类")
    
    logger.info("数据库初始化完成")

if __name__ == "__main__":
    init_db() 