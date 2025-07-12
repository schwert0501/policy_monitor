"""
分类相关路由
"""

from flask import Blueprint, jsonify, request
from ..models import db
from ..models.category import Category
from ..models.policy import Policy
from sqlalchemy import func

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('/', methods=['GET'])
def get_categories():
    """获取所有分类"""
    categories = Category.query.all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': category.id,
                'name': category.name,
                'description': category.description
            } for category in categories
        ]
    })

@categories_bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    """获取单个分类"""
    category = Category.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
    })

@categories_bp.route('/stats', methods=['GET'])
def get_category_stats():
    """获取分类统计信息"""
    # 查询每个分类的政策数量
    stats = db.session.query(
        Category.id, 
        Category.name, 
        func.count(Policy.id).label('policy_count')
    ).outerjoin(
        Policy, 
        Category.id == Policy.category_id
    ).group_by(
        Category.id
    ).all()
    
    return jsonify({
        'success': True,
        'data': [
            {
                'id': stat[0],
                'name': stat[1],
                'policy_count': stat[2]
            } for stat in stats
        ]
    }) 