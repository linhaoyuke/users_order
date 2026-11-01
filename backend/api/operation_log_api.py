# backend/api/operation_log_api.py

from datetime import datetime, timedelta
from typing import Dict, Any

from extensions import db_session
from flask import Blueprint, request, jsonify
from models.operation_log import OperationLog, LogModule, LogAction, LogStatus
from schemas.operation_log import operation_logs_schema, operation_log_query_schema
from sqlalchemy import desc, and_, or_
from utils.jwt import permission_required
from utils.log_helper import LogHelper

operation_log_bp = Blueprint('operation_log_bp', __name__)


@operation_log_bp.route('/', methods=['GET'])
@permission_required('view_log')
def get_operation_logs():
    """
    获取操作日志列表
    支持多种筛选条件和分页查询
    """
    try:
        # 验证查询参数
        raw_query_data = operation_log_query_schema.load(request.args)
        # 类型强制转换为字典
        query_data: Dict[str, Any] = dict(raw_query_data or {})
        
        # 构建基础查询
        query = OperationLog.query.order_by(desc(OperationLog.created_at))
        
        # 应用筛选条件
        operator_id = query_data.get('operator_id')
        if operator_id:
            query = query.filter(OperationLog.operator_id == operator_id)
        
        operator_username = query_data.get('operator_username')
        if operator_username:
            query = query.filter(OperationLog.operator_username.ilike(f"%{operator_username}%"))
        
        module = query_data.get('module')
        if module:
            query = query.filter(OperationLog.module == module)
        
        action = query_data.get('action')
        if action:
            query = query.filter(OperationLog.action == action)
        
        resource_type = query_data.get('resource_type')
        if resource_type:
            query = query.filter(OperationLog.resource_type == resource_type)
        
        resource_id = query_data.get('resource_id')
        if resource_id:
            query = query.filter(OperationLog.resource_id == resource_id)
        
        status = query_data.get('status')
        if status:
            query = query.filter(OperationLog.status == status)
        
        # 时间范围筛选
        start_time = query_data.get('start_time')
        if start_time:
            query = query.filter(OperationLog.created_at >= start_time)
        
        end_time = query_data.get('end_time')
        if end_time:
            query = query.filter(OperationLog.created_at <= end_time)
        
        # 关键词搜索（搜索描述、资源名称、操作者等）
        keyword = query_data.get('keyword')
        if keyword:
            keyword_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    OperationLog.description.ilike(keyword_pattern),
                    OperationLog.resource_name.ilike(keyword_pattern),
                    OperationLog.operator_username.ilike(keyword_pattern),
                    OperationLog.operator_name.ilike(keyword_pattern)
                )
            )
        
        # 分页查询
        page = query_data.get('page', 1)
        per_page = query_data.get('per_page', 20)
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        logs = pagination.items
        
        # 序列化数据
        result = operation_logs_schema.dump(logs)
        
        # 构建响应
        response = {
            'items': result,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'message': f'获取操作日志失败: {str(e)}'}), 500


@operation_log_bp.route('/<int:log_id>', methods=['GET'])
@permission_required('view_log')
def get_operation_log_detail(log_id):
    """获取操作日志详情"""
    try:
        log = OperationLog.query.get_or_404(log_id)
        
        # 解析JSON字段
        result = log.to_dict()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'获取操作日志详情失败: {str(e)}'}), 500


@operation_log_bp.route('/statistics', methods=['GET'])
@permission_required('view_log')
def get_log_statistics():
    """
    获取操作日志统计信息
    """
    try:
        # 获取时间范围参数（默认最近30天）
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        # 基础查询
        base_query = OperationLog.query.filter(OperationLog.created_at >= start_date)
        
        # 总操作数
        total_operations = base_query.count()
        
        # 按模块统计
        module_stats = []
        for module in [LogModule.USER, LogModule.ROLE, LogModule.PERMISSION, 
                      LogModule.ORDER, LogModule.PRODUCT, LogModule.AUTH]:
            count = base_query.filter(OperationLog.module == module).count()
            module_stats.append({
                'module': module,
                'count': count,
                'percentage': round((count / total_operations * 100) if total_operations > 0 else 0, 2)
            })
        
        # 按操作类型统计
        action_stats = []
        for action in [LogAction.CREATE, LogAction.UPDATE, LogAction.DELETE, 
                      LogAction.LOGIN, LogAction.LOGOUT]:
            count = base_query.filter(OperationLog.action == action).count()
            action_stats.append({
                'action': action,
                'count': count,
                'percentage': round((count / total_operations * 100) if total_operations > 0 else 0, 2)
            })
        
        # 按状态统计
        status_stats = []
        for status in [LogStatus.SUCCESS, LogStatus.FAILED, LogStatus.WARNING]:
            count = base_query.filter(OperationLog.status == status).count()
            status_stats.append({
                'status': status,
                'count': count,
                'percentage': round((count / total_operations * 100) if total_operations > 0 else 0, 2)
            })
        
        # 最活跃的用户
        active_users = base_query.group_by(OperationLog.operator_username)\
                                .order_by(desc(OperationLog.operator_username))\
                                .limit(10)\
                                .all()
        
        user_stats = []
        for log in active_users:
            user_count = base_query.filter(OperationLog.operator_username == log.operator_username).count()
            user_stats.append({
                'username': log.operator_username,
                'name': log.operator_name,
                'count': user_count
            })
        
        # 按天统计（最近7天）
        daily_stats = []
        for i in range(7):
            day_start = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = base_query.filter(
                and_(OperationLog.created_at >= day_start, OperationLog.created_at < day_end)
            ).count()
            daily_stats.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_stats.reverse()  # 按时间正序
        
        response = {
            'total_operations': total_operations,
            'days_range': days,
            'module_stats': module_stats,
            'action_stats': action_stats,
            'status_stats': status_stats,
            'user_stats': user_stats,
            'daily_stats': daily_stats
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500


@operation_log_bp.route('/export', methods=['GET'])
@permission_required('export_log')
def export_operation_logs():
    """
    导出操作日志
    """
    try:
        # 记录导出操作日志
        LogHelper.log_auth_operation(
            action=LogAction.EXPORT,
            description="导出操作日志"
        )
        
        # 获取筛选参数
        raw_query_data = operation_log_query_schema.load(request.args)
        # 类型强制转换为字典
        query_data: Dict[str, Any] = dict(raw_query_data or {})
        
        # 构建查询（与列表查询相同的逻辑）
        query = OperationLog.query.order_by(desc(OperationLog.created_at))
        
        # 应用筛选条件（简化实现，可根据需要扩展）
        operator_id = query_data.get('operator_id')
        if operator_id:
            query = query.filter(OperationLog.operator_id == operator_id)
        
        module = query_data.get('module')
        if module:
            query = query.filter(OperationLog.module == module)
        
        status = query_data.get('status')
        if status:
            query = query.filter(OperationLog.status == status)
        
        start_time = query_data.get('start_time')
        if start_time:
            query = query.filter(OperationLog.created_at >= start_time)
        
        end_time = query_data.get('end_time')
        if end_time:
            query = query.filter(OperationLog.created_at <= end_time)
        
        # 获取所有符合条件的记录（注意：生产环境中应该限制导出数量）
        logs = query.limit(10000).all()  # 限制最多导出10000条
        
        # 转换为导出格式
        export_data = []
        for log in logs:
            export_data.append({
                'ID': log.id,
                '操作时间': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                '操作者': log.operator_name or log.operator_username or '系统',
                '模块': log.module,
                '操作': log.action,
                '资源类型': log.resource_type,
                '资源名称': log.resource_name or '',
                '操作描述': log.description,
                '状态': log.status,
                'IP地址': log.ip_address or '',
                '错误信息': log.error_message or ''
            })
        
        return jsonify({
            'message': '导出成功',
            'data': export_data,
            'total': len(export_data)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500


@operation_log_bp.route('/clean', methods=['POST'])
@permission_required('manage_log')
def clean_operation_logs():
    """
    清理操作日志
    """
    try:
        # 获取清理参数
        request_data = request.get_json() or {}
        days = request_data.get('days', 90)  # 默认保留90天
        
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 删除指定日期之前的日志
        deleted_count = OperationLog.query.filter(
            OperationLog.created_at < cutoff_date
        ).delete()
        
        db_session.commit()
        
        # 记录清理操作
        LogHelper.log_auth_operation(
            action='clean_logs',
            description=f"清理{days}天前的操作日志，共删除{deleted_count}条记录"
        )
        
        return jsonify({
            'message': '日志清理成功',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        db_session.rollback()
        return jsonify({'message': f'日志清理失败: {str(e)}'}), 500