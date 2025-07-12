#!/usr/bin/env python
"""
运行Flask应用
"""

import os
from app import create_app

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # 运行应用
    app.run(host='0.0.0.0', port=8090, debug=app.config['DEBUG']) 

