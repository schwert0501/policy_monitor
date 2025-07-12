"""
应用配置模块
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传文件配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 政策监测配置
    ENABLE_POLICY_MONITOR = os.environ.get('ENABLE_POLICY_MONITOR', 'false').lower() == 'true'
    POLICY_MONITOR_INTERVAL = int(os.environ.get('POLICY_MONITOR_INTERVAL', 24))  # 小时
    
    # 存储配置
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')  # local, minio, etc.

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'tax_policy.db')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'test.db')

class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'tax_policy.db')

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 