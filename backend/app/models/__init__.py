"""
数据库模型模块
"""

from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# 导入模型类，确保它们被注册到SQLAlchemy
from .category import Category
from .policy import Policy 