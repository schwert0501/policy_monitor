"""
政策相关路由
"""

from flask import Blueprint, jsonify, request, current_app
from ..models import db
from ..models.policy import Policy
from ..models.category import Category
from sqlalchemy import desc
from datetime import datetime

policies_bp = Blueprint('policies', __name__, url_prefix='/api/policies')

@policies_bp.route('/', methods=['GET'])
def get_policies():
    """获取政策列表"""
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 过滤参数
    category_id = request.args.get('category_id', type=int)
    
    # 创建查询
    query = Policy.query
    
    # 应用过滤
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 排序（默认按发布日期降序）
    query = query.order_by(desc(Policy.pub_date))
    
    # 执行分页查询
    policies = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 格式化结果
    return jsonify({
        'success': True,
        'data': {
            'policies': [policy.to_dict() for policy in policies.items],
            'total': policies.total,
            'pages': policies.pages,
            'current_page': page
        }
    })

@policies_bp.route('/<int:id>', methods=['GET'])
def get_policy(id):
    """获取单个政策详情"""
    policy = Policy.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': policy.to_dict()
    }) 