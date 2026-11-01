# backend/api/role_api.py

from extensions import db_session
# 导入所需模块
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.operation_log import LogModule
from models.permission import Permission
from models.role import Role
from models.user import User
from schemas.permission import PermissionSchema
from schemas.role import RoleSchema
from sqlalchemy.orm import selectinload
from utils.jwt import jwt_required, admin_required
# 导入操作日志相关模块
from utils.log_helper import LogHelper, LogAction, LogStatus

# 创建角色管理的蓝图
role_bp = Blueprint('roles', __name__)

# 实例化Schema
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
permission_schema = PermissionSchema(many=True)

@role_bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    """获取所有角色的列表，会预加载关联的权限信息。"""
    try:
        # 使用 selectinload 预加载权限信息，避免 N+1 查询
        roles = Role.query.options(selectinload(Role.permissions)).all()
        result = roles_schema.dump(roles)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"获取角色列表失败: {str(e)}"}), 500

@role_bp.route('/', methods=['POST'])
@admin_required  # 仅管理员可创建
def create_role():
    """创建一个新角色。"""
    try:
        # .load() 会返回一个经过验证的 Role 对象（如果 Schema 设置了 model）
        # 或者一个字典。我们需要根据实际情况处理。
        # 从错误来看，它返回的是一个对象。
        json_data = request.get_json()
        # 先用 schema 验证和加载数据
        validated_data = role_schema.load(json_data)

    except ValidationError as err:
        # 记录验证失败日志
        LogHelper.log_role_operation(
            action=LogAction.CREATE,
            role_data=request.get_json(),
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400

    # 检查角色名和编码的唯一性
    if Role.query.filter_by(name=validated_data.name).first():
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.CREATE,
            role_data=json_data,
            status=LogStatus.FAILED,
            error_message="角色名已存在"
        )
        return jsonify({"message": "角色名已存在"}), 400
    if Role.query.filter_by(code=validated_data.code).first():
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.CREATE,
            role_data=json_data,
            status=LogStatus.FAILED,
            error_message="角色编码已存在"
        )
        return jsonify({"message": "角色编码已存在"}), 400

    try:
        # 创建角色实例
        new_role = Role(
            name=validated_data.name,
            code=validated_data.code,
            description=validated_data.description
        )

        # 分配权限，从原始的 json_data 中获取
        if 'permissions' in json_data and json_data['permissions']:
            permission_ids = json_data['permissions']
            permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            new_role.permissions = permissions

        db_session.add(new_role)
        db_session.commit()
        
        # 准备日志数据
        log_data = {
            'name': new_role.name,
            'code': new_role.code,
            'description': new_role.description,
            'role_id': new_role.id
        }
        if 'permissions' in json_data and json_data['permissions']:
            log_data['assigned_permissions'] = [{'id': p.id, 'name': p.name} for p in new_role.permissions]
        
        # 记录成功日志
        LogHelper.log_role_operation(
            action=LogAction.CREATE,
            role_data=log_data,
            resource_id=new_role.id,
            description=f"创建角色 - {new_role.name}"
        )
        
        # 序列化新创建的对象以返回
        return jsonify(role_schema.dump(new_role)), 201
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.CREATE,
            role_data=json_data,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"创建角色失败: {str(e)}"}), 500

@role_bp.route('/<int:role_id>', methods=['PUT'])
@admin_required  # 仅管理员可更新
def update_role(role_id):
    """更新指定ID的角色信息。"""
    role = Role.query.get_or_404(role_id)
    json_data = request.get_json()
    
    # 获取更新前的数据用于日志记录
    old_data = {
        'name': role.name,
        'code': role.code,
        'description': role.description,
        'permissions': [{'id': p.id, 'name': p.name} for p in role.permissions]
    }
    
    try:
        # partial=True 允许部分更新
        validated_data = role_schema.load(json_data, partial=True)
    except ValidationError as err:
        # 记录验证失败日志
        LogHelper.log_role_operation(
            action=LogAction.UPDATE,
            role_data=json_data,
            old_data=old_data,
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400

    try:
        # 更新字段并检查唯一性
        if 'name' in json_data and json_data['name'] != role.name:
            if Role.query.filter(Role.name == json_data['name'], Role.id != role_id).first():
                LogHelper.log_role_operation(
                    action=LogAction.UPDATE,
                    role_data=json_data,
                    old_data=old_data,
                    resource_id=role_id,
                    status=LogStatus.FAILED,
                    error_message="角色名已存在"
                )
                return jsonify({"message": "角色名已存在"}), 400
            role.name = json_data['name']

        if 'code' in json_data and json_data['code'] != role.code:
            if Role.query.filter(Role.code == json_data['code'], Role.id != role_id).first():
                LogHelper.log_role_operation(
                    action=LogAction.UPDATE,
                    role_data=json_data,
                    old_data=old_data,
                    resource_id=role_id,
                    status=LogStatus.FAILED,
                    error_message="角色编码已存在"
                )
                return jsonify({"message": "角色编码已存在"}), 400
            role.code = json_data['code']
        
        if 'description' in json_data:
            role.description = json_data.get('description', role.description)

        # 更新权限
        permissions_changed = False
        if 'permissions' in json_data:
            permission_ids = json_data['permissions']
            # 使用先清空再添加的方式，更安全
            role.permissions.clear()
            if permission_ids:
                permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
                role.permissions.extend(permissions)
            permissions_changed = True

        db_session.commit()
        
        # 准备日志数据（更新后的数据）
        new_data = {
            'name': role.name,
            'code': role.code,
            'description': role.description,
            'permissions': [{'id': p.id, 'name': p.name} for p in role.permissions]
        }
        
        # 添加特殊操作说明
        if permissions_changed:
            new_data['permissions_updated'] = True
            
        # 记录成功日志
        LogHelper.log_role_operation(
            action=LogAction.UPDATE,
            role_data=new_data,
            old_data=old_data,
            resource_id=role_id,
            description=f"更新角色信息 - {role.name}"
        )
        
        return jsonify(role_schema.dump(role)), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.UPDATE,
            role_data=json_data,
            old_data=old_data,
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"更新角色失败: {str(e)}"}), 500

@role_bp.route('/<int:role_id>', methods=['DELETE'])
@admin_required  # 仅管理员可删除
def delete_role(role_id):
    """删除指定ID的角色。"""
    role = Role.query.get_or_404(role_id)
    
    # 获取角色信息用于日志记录
    role_data = {
        'name': role.name,
        'code': role.code,
        'description': role.description,
        'permissions': [{'id': p.id, 'name': p.name} for p in role.permissions]
    }

    # 检查角色是否仍被任何用户使用
    # .users 是一个查询构造器 (lazy='dynamic'), 需要执行它来检查
    if role.users.first():
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.DELETE,
            old_data=role_data,
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message="该角色已被用户使用，无法删除"
        )
        return jsonify({"message": "该角色已被用户使用，无法删除"}), 400

    try:
        db_session.delete(role)
        db_session.commit()
        
        # 记录成功日志
        LogHelper.log_role_operation(
            action=LogAction.DELETE,
            old_data=role_data,
            resource_id=role_id,
            description=f"删除角色 - {role_data['name']}"
        )
        
        return jsonify({"message": "角色删除成功"}), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.DELETE,
            old_data=role_data,
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"删除角色失败: {str(e)}"}), 500

@role_bp.route('/<int:role_id>/permissions', methods=['POST'])
@admin_required
def assign_permissions_to_role(role_id):
    """为指定角色分配权限。"""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    
    # 获取原有权限信息
    old_permissions = [{'id': p.id, 'name': p.name} for p in role.permissions]
    
    if 'permission_ids' not in data or not isinstance(data['permission_ids'], list):
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.ASSIGN_PERMISSION,
            role_data=data,
            old_data={'permissions': old_permissions},
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message="请提供一个包含权限ID的数组 'permission_ids'"
        )
        return jsonify({"message": "请提供一个包含权限ID的数组 'permission_ids'"}), 400

    try:
        # 验证权限ID的有效性
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
        if len(permissions) != len(data['permission_ids']):
            # 记录失败日志
            LogHelper.log_role_operation(
                action=LogAction.ASSIGN_PERMISSION,
                role_data=data,
                old_data={'permissions': old_permissions},
                resource_id=role_id,
                status=LogStatus.FAILED,
                error_message="一个或多个权限ID无效"
            )
            return jsonify({"message": "一个或多个权限ID无效"}), 400

        role.permissions = permissions
        db_session.commit()
        
        # 获取新权限信息
        new_permissions = [{'id': p.id, 'name': p.name} for p in role.permissions]
        
        # 记录成功日志
        LogHelper.log_role_operation(
            action=LogAction.ASSIGN_PERMISSION,
            role_data={
                'assigned_permissions': new_permissions,
                'permission_ids': data['permission_ids']
            },
            old_data={'permissions': old_permissions},
            resource_id=role_id,
            description=f"为角色 {role.name} 分配权限"
        )
        
        return jsonify({"message": "权限分配成功"}), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_role_operation(
            action=LogAction.ASSIGN_PERMISSION,
            role_data=data,
            old_data={'permissions': old_permissions},
            resource_id=role_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"分配权限失败: {str(e)}"}), 500

@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@jwt_required()
def get_role_permissions(role_id):
    """获取指定角色的所有权限。"""
    role = Role.query.options(selectinload(Role.permissions)).get_or_404(role_id)
    return jsonify(permission_schema.dump(role.permissions)), 200

@role_bp.route('/stats', methods=['GET'])
@admin_required
def get_role_stats():
    """获取角色相关的统计数据。"""
    total_roles = Role.query.count()
    # 统计有多少角色至少被一个用户使用
    active_roles = Role.query.filter(Role.users.any()).count()
    return jsonify({
        "total_roles": total_roles,
        "active_roles": active_roles
    }), 200
