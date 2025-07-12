"""
API路由模块
"""

from flask import Blueprint
from .categories import categories_bp
from .monitor import monitor_bp
from .policies import policies_bp

# 创建API蓝图
api = Blueprint('api', __name__, url_prefix='/api')

# 注册子蓝图
def init_app(app):
    # 注册主API蓝图
    app.register_blueprint(api)
    
    # 注册子蓝图
    app.register_blueprint(categories_bp)
    app.register_blueprint(policies_bp)
    app.register_blueprint(monitor_bp) 