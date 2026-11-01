# backend/api/user_api.py

from typing import Dict, Any

from extensions import db_session
# 导入所需模块
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from models.operation_log import LogModule
from models.role import Role
from models.user import User
from schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload  # 用于预加载关联数据，防止N+1查询问题
from utils.jwt import jwt_required, admin_required, permission_required, get_current_user
# 导入操作日志相关模块
from utils.log_helper import LogHelper, LogAction, LogStatus

# 创建用户管理的蓝图
user_bp = Blueprint('users', __name__)

# 实例化Schema，用于序列化和反序列化
user_schema = UserSchema()  # 用于序列化单个用户
users_schema = UserSchema(many=True) # 用于序列化用户列表
user_create_schema = UserCreateSchema()  # 用于验证创建用户时的数据
user_update_schema = UserUpdateSchema()  # 用于验证更新用户时的数据

from sqlalchemy import or_

@user_bp.route('/', methods=['GET'])
@jwt_required()  # 保护路由，需要有效token
def get_users():
    """获取用户列表。支持按用户名、全名、邮箱进行模糊搜索和分页。"""
    try:
        # 获取分页和搜索参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        search_keyword = request.args.get('search')

        query = User.query.options(selectinload(User.roles))

        if search_keyword:
            # 使用 OR 条件在多个列上进行 ILIKE 搜索
            # pg_trgm 扩展会为这个查询提供索引支持，从而极大地提升性能
            search_pattern = f"%{search_keyword}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )

        # 使用 paginate 进行分页查询
        pagination = query.order_by(User.id.asc()).paginate(page=page, per_page=page_size, error_out=False)
        
        # 构建符合前端期望的返回格式
        response_data = {
            "count": pagination.total,
            "results": users_schema.dump(pagination.items)
        }

        return jsonify(response_data), 200
    except Exception as e:
        # 异常处理
        return jsonify({"message": f"获取用户列表失败: {str(e)}"}), 500

@user_bp.route('/', methods=['POST'])
@admin_required  # 只有管理员可以创建用户
def create_user():
    """创建新用户。"""
    try:
        # 验证请求数据
        raw_data = user_create_schema.load(request.get_json())
        # 类型强制转换为字典
        data: Dict[str, Any] = dict(raw_data or {})
    except ValidationError as err:
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CREATE,
            user_data=request.get_json(),
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400

    try:
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data['username']).first():
            # 记录失败日志
            LogHelper.log_user_operation(
                action=LogAction.CREATE,
                user_data=data,
                status=LogStatus.FAILED,
                error_message="用户名已存在"
            )
            return jsonify({"message": "用户名已存在"}), 400
            
        if User.query.filter_by(email=data['email']).first():
            # 记录失败日志
            LogHelper.log_user_operation(
                action=LogAction.CREATE,
                user_data=data,
                status=LogStatus.FAILED,
                error_message="邮箱已存在"
            )
            return jsonify({"message": "邮箱已存在"}), 400
        
        # 创建用户实例
        new_user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True)
        )
        new_user.set_password(data['password'])
        
        # 分配角色
        if 'roles' in data and data['roles']:
            # 根据ID查找角色并分配
            roles = Role.query.filter(Role.id.in_(data['roles'])).all()
            new_user.roles = roles
        
        db_session.add(new_user)
        db_session.commit()
        
        # 准备日志数据（不包含密码）
        log_data = {key: value for key, value in data.items() if key != 'password'}
        log_data['user_id'] = new_user.id
        if 'roles' in data:
            log_data['assigned_roles'] = [{'id': r.id, 'name': r.name} for r in new_user.roles]
        
        # 记录成功日志
        LogHelper.log_user_operation(
            action=LogAction.CREATE,
            user_data=log_data,
            resource_id=new_user.id,
            description=f"创建用户 - {new_user.username}"
        )
        
        return jsonify(user_schema.dump(new_user)), 201
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CREATE,
            user_data=data,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"创建用户失败: {str(e)}"}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required  # 只有管理员可以修改用户信息
def update_user(user_id):
    """更新指定ID的用户信息。"""
    user = User.query.get_or_404(user_id)
    json_data = request.get_json()
    
    # 获取更新前的数据用于日志记录
    old_data = {
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'is_active': user.is_active,
        'roles': [{'id': r.id, 'name': r.name} for r in user.roles]
    }

    # 如果密码字段为空字符串，则不更新密码
    if 'password' in json_data and not json_data['password']:
        del json_data['password']
    
    try:
        # partial=True 允许部分更新
        user_update_schema.load(json_data, partial=True)
    except ValidationError as err:
        # 记录验证失败日志
        LogHelper.log_user_operation(
            action=LogAction.UPDATE,
            user_data=json_data,
            old_data=old_data,
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {err.messages}"
        )
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400
    
    try:
        # 更新字段
        if 'username' in json_data and json_data['username'] != user.username:
            if User.query.filter_by(username=json_data['username']).first():
                LogHelper.log_user_operation(
                    action=LogAction.UPDATE,
                    user_data=json_data,
                    old_data=old_data,
                    resource_id=user_id,
                    status=LogStatus.FAILED,
                    error_message="用户名已存在"
                )
                return jsonify({"message": "用户名已存在"}), 400
            user.username = json_data['username']

        if 'email' in json_data and json_data['email'] != user.email:
            if User.query.filter_by(email=json_data['email']).first():
                LogHelper.log_user_operation(
                    action=LogAction.UPDATE,
                    user_data=json_data,
                    old_data=old_data,
                    resource_id=user_id,
                    status=LogStatus.FAILED,
                    error_message="邮箱已存在"
                )
                return jsonify({"message": "邮箱已存在"}), 400
            user.email = json_data['email']

        if 'full_name' in json_data:
            user.full_name = json_data.get('full_name', user.full_name)
        if 'phone' in json_data:
            user.phone = json_data.get('phone', user.phone)
        if 'is_active' in json_data:
            user.is_active = json_data.get('is_active', user.is_active)

        # 如果提供了密码，则更新密码
        password_changed = False
        if 'password' in json_data and json_data['password']:
            user.set_password(json_data['password'])
            password_changed = True

        # 更新角色
        roles_changed = False
        if 'roles' in json_data:
            user.roles.clear()
            if json_data['roles']:
                roles = Role.query.filter(Role.id.in_(json_data['roles'])).all()
                user.roles.extend(roles)
            roles_changed = True

        db_session.commit()
        
        # 准备日志数据（更新后的数据）
        new_data = {
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'is_active': user.is_active,
            'roles': [{'id': r.id, 'name': r.name} for r in user.roles]
        }
        
        # 添加特殊操作说明
        if password_changed:
            new_data['password_changed'] = True
        if roles_changed:
            new_data['roles_updated'] = True
            
        # 记录成功日志
        LogHelper.log_user_operation(
            action=LogAction.UPDATE,
            user_data=new_data,
            old_data=old_data,
            resource_id=user_id,
            description=f"更新用户信息 - {user.username}"
        )
        
        return jsonify(user_schema.dump(user)), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.UPDATE,
            user_data=json_data,
            old_data=old_data,
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"更新用户失败: {str(e)}"}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required  # 只有管理员可以删除用户
def delete_user(user_id):
    """删除指定ID的用户。"""
    user = User.query.get_or_404(user_id)
    
    # 防止管理员删除自己
    current_user_id = get_jwt_identity()
    if user.id == int(current_user_id):
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.DELETE,
            old_data={'username': user.username, 'email': user.email},
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message="不能删除当前登录用户"
        )
        return jsonify({"message": "不能删除当前登录用户"}), 400
    
    # 获取用户信息用于日志记录
    user_data = {
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'is_active': user.is_active,
        'roles': [{'id': r.id, 'name': r.name} for r in user.roles],
        'created_at': user.created_at.isoformat() if user.created_at else None
    }

    try:
        db_session.delete(user)
        db_session.commit()
        
        # 记录成功日志
        LogHelper.log_user_operation(
            action=LogAction.DELETE,
            old_data=user_data,
            resource_id=user_id,
            description=f"删除用户 - {user_data['username']}"
        )
        
        return jsonify({"message": "用户删除成功"}), 200
        
    except IntegrityError:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.DELETE,
            old_data=user_data,
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message="该用户可能有关联的订单或其他数据，无法直接删除"
        )
        return jsonify({"message": "删除失败：该用户可能有关联的订单或其他数据，无法直接删除。"}), 400
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.DELETE,
            old_data=user_data,
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": "删除用户时发生未知错误"}), 500

# --- 个人信息管理 (Profile) ---

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """获取当前登录用户的个人信息。"""
    current_user_id = get_jwt_identity()
    user = User.query.options(selectinload(User.roles)).get_or_404(current_user_id)
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_current_user_profile():
    """更新当前登录用户的个人信息。"""
    current_user_id = get_jwt_identity()
    user = User.query.options(selectinload(User.roles)).get_or_404(current_user_id)
    
    try:
        # 普通用户只能更新部分字段，使用UserUpdateSchema但只处理允许的字段
        raw_data = user_update_schema.load(request.get_json(), partial=True)
        # 类型强制转换为字典
        data: Dict[str, Any] = dict(raw_data or {})
    except ValidationError as err:
        return jsonify({"message": "数据验证失败", "errors": err.messages}), 400

    # 检查邮箱唯一性
    if 'email' in data and data['email'] != user.email:
        if User.query.filter(User.email == data['email'], User.id != user.id).first():
            return jsonify({"message": "邮箱已存在"}), 400
        user.email = data['email']

    user.full_name = data.get('full_name', user.full_name)
    user.phone = data.get('phone', user.phone)

    db_session.commit()
    return jsonify(user_schema.dump(user)), 200

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_current_user_password():
    """修改当前用户的密码。"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CHANGE_PASSWORD,
            resource_id=current_user_id,
            status=LogStatus.FAILED,
            error_message="请提供旧密码和新密码"
        )
        return jsonify({"message": "请提供旧密码和新密码"}), 400

    if not user.check_password(old_password):
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CHANGE_PASSWORD,
            resource_id=current_user_id,
            status=LogStatus.FAILED,
            error_message="旧密码错误"
        )
        return jsonify({"message": "旧密码错误"}), 400

    if len(new_password) < 6:
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CHANGE_PASSWORD,
            resource_id=current_user_id,
            status=LogStatus.FAILED,
            error_message="新密码长度至少6位"
        )
        return jsonify({"message": "新密码长度至少6位"}), 400

    try:
        user.set_password(new_password)
        db_session.commit()
        
        # 记录成功日志
        LogHelper.log_user_operation(
            action=LogAction.CHANGE_PASSWORD,
            user_data={'password_changed': True},
            resource_id=current_user_id,
            description=f"用户 {user.username} 修改密码"
        )
        
        return jsonify({"message": "密码修改成功"}), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CHANGE_PASSWORD,
            resource_id=current_user_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"修改密码失败: {str(e)}"}), 500

# --- 其他辅助API ---

@user_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_users_for_selection():
    """获取所有用户的基础信息，用于下拉选择框等场景。不分页。"""
    try:
        # 只查询必要的字段以提高效率
        users = User.query.options(selectinload(User.roles)).order_by(User.username.asc()).all()
        # 使用 a "light" schema if available, for now, use the main one
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        return jsonify({"message": f"获取所有用户失败: {str(e)}"}), 500


@user_bp.route('/stats', methods=['GET'])
@admin_required
def get_user_stats():
    """获取用户统计数据（仅管理员）。"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    return jsonify({
        "total_users": total_users,
        "active_users": active_users
    }), 200

@user_bp.route('/<int:user_id>/roles', methods=['POST'])
@admin_required
def assign_user_roles(user_id):
    """为指定用户分配角色（仅管理员）。"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'role_ids' not in data or not isinstance(data['role_ids'], list):
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.ASSIGN_ROLE,
            user_data=data,
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message="请提供一个包含角色ID的数组'role_ids'"
        )
        return jsonify({"message": "请提供一个包含角色ID的数组'role_ids'"}), 400

    # 获取原有角色信息
    old_roles = [{'id': r.id, 'name': r.name} for r in user.roles]
    
    try:
        # 验证角色ID是否存在
        roles = Role.query.filter(Role.id.in_(data['role_ids'])).all()
        if len(roles) != len(data['role_ids']):
            # 记录失败日志
            LogHelper.log_user_operation(
                action=LogAction.ASSIGN_ROLE,
                user_data=data,
                old_data={'roles': old_roles},
                resource_id=user_id,
                status=LogStatus.FAILED,
                error_message="一个或多个角色ID无效"
            )
            return jsonify({"message": "一个或多个角色ID无效"}), 400

        # 使用更安全的方式更新角色：先清空再添加
        user.roles.clear()
        user.roles.extend(roles)
        
        db_session.commit()
        
        # 获取新角色信息
        new_roles = [{'id': r.id, 'name': r.name} for r in user.roles]
        
        # 记录成功日志
        LogHelper.log_user_operation(
            action=LogAction.ASSIGN_ROLE,
            user_data={'assigned_roles': new_roles, 'role_ids': data['role_ids']},
            old_data={'roles': old_roles},
            resource_id=user_id,
            description=f"为用户 {user.username} 分配角色"
        )
        
        return jsonify(user_schema.dump(user)), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.ASSIGN_ROLE,
            user_data=data,
            old_data={'roles': old_roles},
            resource_id=user_id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({"message": f"分配角色失败: {str(e)}"}), 500
