"""
应用初始化模块
"""

import os
from flask import Flask
from flask_cors import CORS
from .models import db
from .config.config import config
from .monitor.monitor import setup_monitor, shutdown_scheduler

def create_app(config_name=None):
    """创建Flask应用实例"""
    # 确定配置类型
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # 创建应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化CORS
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from .routes import init_app as init_routes
    init_routes(app)
    
    # 设置监测任务
    setup_monitor(app)
    
    # 注册关闭函数
    @app.teardown_appcontext
    def shutdown_context(exception=None):
        db.session.remove()
    
    return app 