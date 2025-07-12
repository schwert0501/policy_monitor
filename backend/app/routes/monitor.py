"""
监测相关路由
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
from ..monitor.monitor import run_monitor
from ..models import db
from ..models.policy import Policy
from sqlalchemy import func, desc

monitor_bp = Blueprint('monitor', __name__, url_prefix='/api/monitor')

@monitor_bp.route('/run', methods=['POST'])
def run_monitoring():
    """手动触发监测任务"""
    try:
        results = run_monitor()
        return jsonify({
            'success': True,
            'message': '监测任务已完成',
            'results': results
        }), 200
    except Exception as e:
        current_app.logger.error(f"运行监测任务时出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'监测任务失败: {str(e)}'
        }), 500

@monitor_bp.route('/stats', methods=['GET'])
def get_monitor_stats():
    """获取监测统计数据"""
    try:
        # 获取时间范围参数（默认30天）
        days = int(request.args.get('days', 30))
        
        # 计算开始日期
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 查询新增政策数量
        new_policies_count = db.session.query(func.count(Policy.id)).filter(
            Policy.created_at >= start_date
        ).scalar()
        
        # 查询更新政策数量
        updated_policies_count = db.session.query(func.count(Policy.id)).filter(
            Policy.updated_at >= start_date,
            Policy.created_at < start_date
        ).scalar()
        
        # 查询总政策数量
        total_policies_count = db.session.query(func.count(Policy.id)).scalar()
        
        # 获取最近一次监测时间
        latest_policy = db.session.query(Policy).order_by(desc(Policy.updated_at)).first()
        last_monitor_time = latest_policy.updated_at if latest_policy else None
        
        return jsonify({
            'success': True,
            'data': {
                'newPolicies': new_policies_count,
                'updatedPolicies': updated_policies_count,
                'totalPolicies': total_policies_count,
                'lastMonitorTime': last_monitor_time.isoformat() if last_monitor_time else None,
                'timeRange': days
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取监测统计数据时出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取监测统计数据失败: {str(e)}'
        }), 500

@monitor_bp.route('/policies', methods=['GET'])
def get_monitored_policies():
    """获取监测到的政策列表"""
    try:
        # 获取时间范围参数（默认30天）
        days = int(request.args.get('days', 30))
        
        # 计算开始日期
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # 查询在时间范围内新增或更新的政策
        query = Policy.query.filter(
            (Policy.created_at >= start_date) | 
            (Policy.updated_at >= start_date)
        ).order_by(desc(Policy.updated_at))
        
        # 执行分页查询
        policies_page = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 格式化结果
        policies = [policy.to_dict() for policy in policies_page.items]
        
        # 添加标记：新增或更新
        for policy in policies:
            if datetime.fromisoformat(policy['created_at']) >= start_date:
                policy['status'] = 'new'
            else:
                policy['status'] = 'updated'
        
        return jsonify({
            'success': True,
            'data': {
                'policies': policies,
                'total': policies_page.total,
                'pages': policies_page.pages,
                'current_page': page
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取监测政策列表时出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取监测政策列表失败: {str(e)}'
        }), 500

@monitor_bp.route('/policy/<int:policy_id>', methods=['GET'])
def get_policy_detail(policy_id):
    """获取政策详情"""
    try:
        policy = Policy.query.get(policy_id)
        
        if not policy:
            return jsonify({
                'success': False,
                'message': f'未找到ID为{policy_id}的政策'
            }), 404
        
        return jsonify({
            'success': True,
            'data': policy.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取政策详情时出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取政策详情失败: {str(e)}'
        }), 500 