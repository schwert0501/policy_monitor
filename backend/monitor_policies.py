#!/usr/bin/env python
"""
政策监测脚本，用于手动运行监测任务
"""

import sys
import os
import logging
from app import create_app
from app.monitor.monitor import run_monitor, ensure_categories_exist

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('policy_monitor_cli')

def main():
    """主函数"""
    logger.info("开始运行政策监测命令行工具")
    
    # 创建Flask应用
    app = create_app()
    
    # 在应用上下文中运行
    with app.app_context():
        # 确保分类存在
        ensure_categories_exist()
        
        # 运行监测任务
        run_monitor()
    
    logger.info("政策监测命令行工具运行完成")

if __name__ == "__main__":
    main() 