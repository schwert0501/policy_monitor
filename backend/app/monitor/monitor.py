"""
政策监测脚本，用于定时检查财税领域官方政策法规
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import logging
import time
import os
import re
from datetime import datetime
from flask import current_app
from ..models import db
from ..models.policy import Policy
from ..models.category import Category
from ..utils.storage import storage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('policy_monitor')

# 定义监测源
MONITOR_SOURCES = {
    'mof_szs': {
        'name': '财政部税政司',
        'url': 'https://szs.mof.gov.cn/zt/jsjfzczl/zcfg/',
        'parser': 'parse_mof_szs',
        'category_name': '税收政策',
        'max_pages': 10  # 最大抓取页数
    }
}

# 全局调度器
scheduler = None

def setup_monitor(app):
    """
    设置监测任务
    :param app: Flask应用实例
    """
    global scheduler
    
    # 如果启用了自动监测，则设置定时任务
    if app.config.get('ENABLE_POLICY_MONITOR', False):
        # 获取监测间隔（小时）
        interval_hours = app.config.get('POLICY_MONITOR_INTERVAL', 24)
        
        # 创建调度器
        if scheduler is None:
            scheduler = BackgroundScheduler()
            
            # 添加定时任务
            scheduler.add_job(
                func=lambda: run_monitor_with_app_context(app),
                trigger=IntervalTrigger(hours=interval_hours),
                id='monitor_job',
                name='政策监测任务',
                replace_existing=True
            )
            
            # 启动调度器
            scheduler.start()
            logger.info(f"已启动政策监测定时任务，间隔 {interval_hours} 小时")

def run_monitor_with_app_context(app):
    """
    在应用上下文中运行监测任务
    :param app: Flask应用实例
    """
    with app.app_context():
        # 确保分类存在
        ensure_categories_exist()
        # 运行监测任务
        run_monitor()

def ensure_categories_exist():
    """确保所需的分类存在于数据库中"""
    categories = set()
    for source in MONITOR_SOURCES.values():
        categories.add(source['category_name'])
    
    for category_name in categories:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            logger.info(f"创建分类: {category_name}")
            category = Category(name=category_name, description=f"{category_name}相关政策")
            db.session.add(category)
    
    db.session.commit()

def run_monitor():
    """运行监测任务"""
    logger.info("开始运行政策监测任务")
    
    results = {}
    
    for source_id, source_config in MONITOR_SOURCES.items():
        try:
            logger.info(f"开始监测来源: {source_config['name']}")
            
            # 获取解析器函数
            parser_func = globals()[source_config['parser']]
            
            # 解析政策列表
            policies = parser_func(source_config)
            
            # 处理政策
            source_results = process_policies(policies, source_config)
            results[source_id] = source_results
            
            logger.info(f"完成监测来源: {source_config['name']}")
        except Exception as e:
            logger.error(f"监测来源 {source_config['name']} 时出错: {str(e)}", exc_info=True)
            results[source_id] = {'error': str(e)}
    
    logger.info("政策监测任务完成")
    return results

def process_policies(policies, source_config):
    """
    处理政策列表，识别新政策和更新的政策
    :param policies: 政策列表
    :param source_config: 来源配置
    """
    # 获取分类ID
    category = Category.query.filter_by(name=source_config['category_name']).first()
    if not category:
        logger.error(f"分类 {source_config['category_name']} 不存在")
        return {'error': f"分类 {source_config['category_name']} 不存在"}
    
    # 记录处理结果
    results = {
        'new': 0,
        'updated': 0,
        'unchanged': 0
    }
    
    for policy in policies:
        # 检查政策是否已存在
        existing_policy = Policy.query.filter_by(title=policy['title']).first()
        
        if not existing_policy:
            # 新政策
            logger.info(f"发现新政策: {policy['title']}")
            
            # 下载政策内容
            content, content_md5 = download_policy_content(policy['url'])
            
            # 创建新政策记录
            new_policy = Policy(
                title=policy['title'],
                content=content,
                pub_date=policy['pub_date'],
                org=source_config['name'],
                category_id=category.id,
                content_md5=content_md5,
                source_url=policy['url']  # 保存源URL
            )
            
            # 下载并保存附件
            if 'attachment_url' in policy and policy['attachment_url']:
                file_path = download_policy_attachment(policy['attachment_url'], policy['title'])
                if file_path:
                    new_policy.file_path = file_path
            
            db.session.add(new_policy)
            db.session.commit()
            logger.info(f"已保存新政策: {policy['title']}")
            results['new'] += 1
        
        else:
            # 已存在的政策，检查内容是否更新
            content, content_md5 = download_policy_content(policy['url'])
            
            # 如果MD5不同，则更新政策
            if not existing_policy.content_md5 or existing_policy.content_md5 != content_md5:
                logger.info(f"政策内容已更新: {policy['title']}")
                
                # 更新政策记录
                existing_policy.content = content
                existing_policy.content_md5 = content_md5
                existing_policy.updated_at = datetime.utcnow()
                
                # 确保源URL被保存
                if not existing_policy.source_url:
                    existing_policy.source_url = policy['url']
                
                # 如果有附件且附件URL不同，则更新附件
                if 'attachment_url' in policy and policy['attachment_url']:
                    file_path = download_policy_attachment(policy['attachment_url'], policy['title'])
                    if file_path:
                        # 删除旧附件
                        if existing_policy.file_path:
                            storage.delete_file(existing_policy.file_path)
                        existing_policy.file_path = file_path
                
                db.session.commit()
                logger.info(f"已更新政策: {policy['title']}")
                results['updated'] += 1
            else:
                # 政策未变化
                results['unchanged'] += 1
    
    logger.info(f"处理结果: 新增 {results['new']} 条，更新 {results['updated']} 条，未变化 {results['unchanged']} 条")
    return results

def parse_mof_szs(source_config):
    """
    解析财政部税政司政策法规页面
    :param source_config: 来源配置
    :return: 政策列表
    """
    base_url = source_config['url']
    max_pages = source_config.get('max_pages', 10)
    logger.info(f"开始解析页面: {base_url}, 最大页数: {max_pages}")
    
    policy_list = []
    current_page = 1
    
    # 处理第一页
    policies, has_next_page = parse_mof_szs_page(base_url, current_page)
    policy_list.extend(policies)
    
    # 处理后续页面
    while has_next_page and current_page < max_pages:
        current_page += 1
        logger.info(f"解析第 {current_page} 页")
        
        # 构建分页URL
        if current_page > 1:
            page_url = f"{base_url}index_{current_page}.html"
        else:
            page_url = base_url
            
        # 解析当前页
        try:
            page_policies, has_next_page = parse_mof_szs_page(page_url, current_page)
            policy_list.extend(page_policies)
            
            # 避免请求过于频繁
            time.sleep(1)
        except Exception as e:
            logger.error(f"解析第 {current_page} 页时出错: {str(e)}", exc_info=True)
            break
    
    logger.info(f"共解析到 {len(policy_list)} 条政策")
    return policy_list

def parse_mof_szs_page(url, page_num):
    """
    解析财政部税政司政策法规单页
    :param url: 页面URL
    :param page_num: 页码
    :return: (政策列表, 是否有下一页)
    """
    logger.info(f"解析页面: {url}")
    
    # 发送请求
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except requests.exceptions.RequestException as e:
        if page_num > 1 and "404" in str(e):
            logger.info(f"页面 {url} 不存在，可能已到达最后一页")
            return [], False
        raise
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找政策列表
    policy_list = []
    
    # 查找包含政策的ul元素
    ul_elements = soup.find_all('ul', class_='liBox')
    
    for ul in ul_elements:
        # 查找所有li元素
        li_elements = ul.find_all('li')
        
        for li in li_elements:
            try:
                # 查找链接
                a_tag = li.find('a')
                if not a_tag:
                    continue
                
                # 获取标题
                title = a_tag.text.strip()
                
                # 获取链接
                href = a_tag.get('href')
                if href.startswith('./'):
                    href = url.rstrip('/') + '/' + href[2:]
                elif href.startswith('/'):
                    href = 'https://szs.mof.gov.cn' + href
                elif not href.startswith(('http://', 'https://')):
                    # 相对路径，转为绝对路径
                    base_parts = url.split('/')
                    if url.endswith('/'):
                        href = url + href
                    else:
                        href = '/'.join(base_parts[:-1]) + '/' + href
                
                # 获取日期
                date_span = li.find('span')
                pub_date = None
                if date_span:
                    date_text = date_span.text.strip()
                    # 解析日期，格式可能为 YYYY-MM-DD
                    try:
                        pub_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                    except ValueError:
                        logger.warning(f"无法解析日期: {date_text}, 使用当前日期")
                        pub_date = datetime.now().date()
                else:
                    pub_date = datetime.now().date()
                
                # 添加到政策列表
                policy_list.append({
                    'title': title,
                    'url': href,
                    'pub_date': pub_date,
                    'attachment_url': None  # 附件URL需要在详情页中获取
                })
            
            except Exception as e:
                logger.error(f"解析政策时出错: {str(e)}", exc_info=True)
    
    # 检查是否有下一页
    has_next_page = False
    pagination = soup.find('div', class_='page')
    if pagination:
        next_link = pagination.find('a', string=re.compile('下一页'))
        has_next_page = next_link is not None
    
    logger.info(f"第 {page_num} 页共解析到 {len(policy_list)} 条政策, 是否有下一页: {has_next_page}")
    return policy_list, has_next_page

def download_policy_content(url):
    """
    下载政策内容并计算MD5
    :param url: 政策URL
    :return: (内容, MD5值)
    """
    logger.info(f"下载政策内容: {url}")
    
    # 发送请求
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找内容区域
    content_div = soup.find('div', class_='content')
    if not content_div:
        content_div = soup.find('div', class_='TRS_Editor')
    if not content_div:
        content_div = soup.find('div', id='zoom')  # 一些政府网站使用id="zoom"
    
    if content_div:
        # 提取纯文本内容
        content = content_div.get_text(separator='\n', strip=True)
        
        # 计算MD5
        content_md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        return content, content_md5
    else:
        logger.warning(f"未找到内容区域: {url}")
        return "", ""

def download_policy_attachment(url, title):
    """
    下载政策附件
    :param url: 附件URL
    :param title: 政策标题
    :return: 保存的文件路径
    """
    try:
        logger.info(f"下载政策附件: {url}")
        
        # 发送请求
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # 获取文件名
        filename = url.split('/')[-1]
        if not filename:
            # 使用标题作为文件名
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            
            # 根据Content-Type添加扩展名
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                filename += '.pdf'
            elif 'word' in content_type or 'doc' in content_type:
                filename += '.doc'
            else:
                filename += '.pdf'  # 默认为PDF
        
        # 保存文件
        temp_path = os.path.join('/tmp', filename)
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 使用存储工具保存文件
        with open(temp_path, 'rb') as f:
            file_path = storage.save_file(f, folder='policies', filename=filename)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return file_path
    
    except Exception as e:
        logger.error(f"下载附件时出错: {str(e)}", exc_info=True)
        return None

def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("已关闭政策监测调度器") 