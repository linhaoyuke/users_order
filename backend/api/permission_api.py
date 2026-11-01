# backend/api/permission_api.py

from extensions import db_session
# 导入所需模块
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.operation_log import LogModule
from models.permission import Permission
from schemas.permission import PermissionSchema
from utils.jwt import jwt_required, admin_required
# 导入操作日志相关模块
from utils.log_helper import LogHelper, LogAction, LogStatus

# 创建权限管理的蓝图
permission_bp = Blueprint('permissions', __name__)

# 实例化Schema
permission_schema = PermissionSchema()
permissions_schema = PermissionSchema(many=True)

@permission_bp.route('/', methods=['GET'])
@jwt_required()
def get_permissions():
    """获取所有权限的列表。"""
    try:
        permissions = Permission.query.all()
        result = permissions_schema.dump(permissions)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"获取权限列表失败: {str(e)}"}), 500

@permission_bp.route('/', methods=['POST'])
@admin_required  # 仅管理员可创建
def create_permission():
    """创建一个新的权限。"""
    json_data = request.get_json()
    try:
        # 验证并加载请求数据
        validated_data = permission_schema.load(json_data)
    except ValidationError as err:
        # 记录验证失败日志
        LogHelper.log_permission_operation(
            action=LogAction.CREATE,
            permission_data=json_data,
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400

    # 检查权限编码的唯一性
    if Permission.query.filter_by(code=validated_data.code).first():
        # 记录失败日志
        LogHelper.log_permission_operation(
            action=LogAction.CREATE,
            permission_data=json_data,
            status=LogStatus.FAILED,
            error_message="权限编码已存在"
        )
        return jsonify({"message": "权限编码已存在"}), 400

    try:
        # 创建权限实例
        new_permission = Permission(
            name=validated_data.name,
            code=validated_data.code,
            description=validated_data.description,
            resource=validated_data.resource,
            action=validated_data.action
        )

        db_session.add(new_permission)
        db_session.commit()
        
        # 准备日志数据
        log_data = {
            'name': new_permission.name,
            'code': new_permission.code,
            'description': new_permission.description,
            'resource': new_permission.resource,
            'action': new_permission.action,
            'permission_id': new_permission.id
        }
        
        # 记录成功日志
        LogHelper.log_permission_operation(
            action=LogAction.CREATE,
            permission_data=log_data,
            resource_id=new_permission.id,
            description=f"创建权限 - {new_permission.name}"
        )
        
        return jsonify(permission_schema.dump(new_permission)), 201
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_permission_operation(
            action=LogAction.CREATE,
            permission_data=json_data,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"创建权限失败: {str(e)}"}), 500

@permission_bp.route('/<int:permission_id>', methods=['PUT'])
@admin_required  # 仅管理员可更新
def update_permission(permission_id):
    """更新指定ID的权限信息。"""
    permission = Permission.query.get_or_404(permission_id)
    json_data = request.get_json()
    
    # 获取更新前的数据用于日志记录
    old_data = {
        'name': permission.name,
        'code': permission.code,
        'description': permission.description,
        'resource': permission.resource,
        'action': permission.action
    }
    
    try:
        # 验证并加载请求数据（允许部分更新）
        permission_schema.load(json_data, partial=True)
    except ValidationError as err:
        # 记录验证失败日志
        LogHelper.log_permission_operation(
            action=LogAction.UPDATE,
            permission_data=json_data,
            old_data=old_data,
            resource_id=permission_id,
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400
    
    try:
        # 更新字段并检查编码唯一性
        if 'code' in json_data and json_data['code'] != permission.code:
            if Permission.query.filter(Permission.code == json_data['code'], Permission.id != permission_id).first():
                LogHelper.log_permission_operation(
                    action=LogAction.UPDATE,
                    permission_data=json_data,
                    old_data=old_data,
                    resource_id=permission_id,
                    status=LogStatus.FAILED,
                    error_message="权限编码已存在"
                )
                return jsonify({"message": "权限编码已存在"}), 400
            permission.code = json_data['code']
        
        if 'name' in json_data:
            permission.name = json_data['name']
        if 'description' in json_data:
            permission.description = json_data.get('description')
        if 'resource' in json_data:
            permission.resource = json_data['resource']
        if 'action' in json_data:
            permission.action = json_data['action']
        
        db_session.commit()
        
        # 准备日志数据（更新后的数据）
        new_data = {
            'name': permission.name,
            'code': permission.code,
            'description': permission.description,
            'resource': permission.resource,
            'action': permission.action
        }
        
        # 记录成功日志
        LogHelper.log_permission_operation(
            action=LogAction.UPDATE,
            permission_data=new_data,
            old_data=old_data,
            resource_id=permission_id,
            description=f"更新权限信息 - {permission.name}"
        )
        
        return jsonify(permission_schema.dump(permission)), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_permission_operation(
            action=LogAction.UPDATE,
            permission_data=json_data,
            old_data=old_data,
            resource_id=permission_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"更新权限失败: {str(e)}"}), 500

@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@admin_required  # 仅管理员可删除
def delete_permission(permission_id):
    """删除指定ID的权限。"""
    permission = Permission.query.get_or_404(permission_id)
    
    # 获取权限信息用于日志记录
    permission_data = {
        'name': permission.name,
        'code': permission.code,
        'description': permission.description,
        'resource': permission.resource,
        'action': permission.action
    }

    # 检查权限是否仍被任何角色使用
    # .roles 是一个查询构造器 (lazy='dynamic'), 需要执行它来检查
    if permission.roles.first():
        # 记录失败日志
        LogHelper.log_permission_operation(
            action=LogAction.DELETE,
            old_data=permission_data,
            resource_id=permission_id,
            status=LogStatus.FAILED,
            error_message="该权限已被角色使用，无法删除"
        )
        return jsonify({"message": "该权限已被角色使用，无法删除"}), 400

    try:
        db_session.delete(permission)
        db_session.commit()
        
        # 记录成功日志
        LogHelper.log_permission_operation(
            action=LogAction.DELETE,
            old_data=permission_data,
            resource_id=permission_id,
            description=f"删除权限 - {permission_data['name']}"
        )
        
        return jsonify({"message": "权限删除成功"}), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_permission_operation(
            action=LogAction.DELETE,
            old_data=permission_data,
            resource_id=permission_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"删除权限失败: {str(e)}"}), 500

@permission_bp.route('/stats', methods=['GET'])
@admin_required
def get_permission_stats():
    """获取权限相关的统计数据。"""
    total_permissions = Permission.query.count()
    # 统计有多少权限至少被一个角色使用
    active_permissions = Permission.query.filter(Permission.roles.any()).count()
    return jsonify({
        "total_permissions": total_permissions,
        "active_permissions": active_permissions
    }), 200
