# backend/utils/jwt.py

from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)

# 实例化JWTManager，这个实例将在app.py中与Flask应用关联
jwt = JWTManager()

def get_current_user():
    """
    从JWT中获取当前用户的完整信息（claims）。
    这是一个辅助函数，用于在受保护的路由中方便地获取用户信息。
    """
    try:
        # get_jwt() 返回一个字典，包含了JWT的所有声明（payload）
        claims = get_jwt()
        # 我们在登录时将用户信息存储在了 'sub' (identity) 和其他自定义声明中
        # Flask-JWT-Extended 4.x 之后，自定义声明会自动合并到顶级claims中
        return claims
    except Exception:
        # 如果在JWT上下文之外调用，或者token无效，可能会出错
        return None

def admin_required(fn):
    """
    一个装饰器，用于保护路由，确保只有管理员角色的用户才能访问。
    """
    @wraps(fn)
    @jwt_required()  # 首先确保有一个有效的JWT
    def wrapper(*args, **kwargs):
        try:
            # 从JWT中获取当前用户信息
            current_user_claims = get_jwt()
            
            # 检查claims中是否有 'admin' 角色编码
            # 我们在登录时将角色信息存入了claims
            roles = current_user_claims.get('roles', [])
            if not any(role.get('code') == 'admin' for role in roles):
                return jsonify({"message": "需要管理员权限"}), 403
            
            # 如果权限检查通过，则执行原始的路由函数
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"message": f"权限验证失败: {str(e)}"}), 500
    return wrapper

def permission_required(permission_code):
    """
    一个带参数的装饰器，用于保护路由，确保用户拥有特定的权限。
    用法: @permission_required('user:create')
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                # 从JWT中获取所有权限编码
                current_user_claims = get_jwt()
                user_permissions = current_user_claims.get('permissions', [])
                
                # 检查所需的权限是否存在于用户的权限列表中
                if permission_code not in user_permissions:
                    return jsonify({"message": f"需要权限: {permission_code}"}), 403
                
                # 权限检查通过，执行原始路由函数
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"message": f"权限验证失败: {str(e)}"}), 500
        return wrapper
    return decorator

# 重新导出flask_jwt_extended中的函数，以便在项目其他地方统一从这里导入
# 这是一种良好的实践，可以方便未来更换JWT库或进行统一修改
__all__ = [
    'jwt',
    'create_access_token',
    'create_refresh_token',
    'jwt_required',
    'get_jwt_identity',
    'get_jwt',
    'get_current_user',
    'admin_required',
    'permission_required'
]
