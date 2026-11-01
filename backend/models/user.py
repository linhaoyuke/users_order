# backend/models/user.py

# 导入所需模块
from extensions import db  # 导入数据库实例
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func  # 用于处理时间戳
from werkzeug.security import generate_password_hash, check_password_hash  # 用于密码的哈希和校验

# --- 中间表定义 ---

# 用户-角色多对多关联表
# 一个用户可以有多个角色，一个角色可以赋予多个用户
user_roles = Table(
    'user_roles', db.metadata,
    Column('user_id', BigInteger, ForeignKey('users.id'), primary_key=True),
    Column('role_id', BigInteger, ForeignKey('roles.id'), primary_key=True)
)

# 角色-权限多对多关联表
# 一个角色可以包含多个权限，一个权限可以属于多个角色
role_permissions = Table(
    'role_permissions', db.metadata,
    Column('role_id', BigInteger, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', BigInteger, ForeignKey('permissions.id'), primary_key=True)
)

class User(db.Model):  # type: ignore
    """
    用户模型，代表系统中的一个用户。
    """
    __tablename__ = 'users'  # 定义在数据库中的表名

    # --- 字段定义 ---
    id = Column(BigInteger, primary_key=True)  # 主键ID
    username = Column(String(50), unique=True, nullable=False)  # 用户名，唯一且不为空
    password = Column(String(255), nullable=False)  # 存储哈希后的密码，不为空
    email = Column(String(100), unique=True, nullable=False)  # 邮箱，唯一且不为空
    full_name = Column(String(100))  # 真实姓名
    phone = Column(String(20))  # 电话号码
    is_active = Column(Boolean, default=True)  # 账户是否激活，默认为True
    created_at = Column(DateTime, server_default=func.now())  # 创建时间，默认为当前UTC时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # 更新时间，每次更新时自动更新

    # --- 关系定义 ---
    # 与Role模型的多对多关系
    # secondary=user_roles 指定了中间表
    # backref='users' 使得在Role模型中可以通过 .users 访问关联的所有用户
    roles = relationship('Role', secondary='user_roles', backref=backref('users', lazy='dynamic'))
    
    # 与Order模型的一对多关系
    # backref='user' 使得在Order模型中可以通过 .user 访问所属的用户
    orders = relationship('Order', backref='user', lazy='dynamic')

    # --- 实例方法 ---
    def set_password(self, password):
        """
        设置密码。将明文密码哈希后存储。
        :param password: 明文密码
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        校验密码。
        :param password: 需要校验的明文密码
        :return: Boolean, 密码是否正确
        """
        return check_password_hash(self.password, password)
    
    def has_role(self, role_code):
        """
        检查用户是否拥有指定编码的角色。
        :param role_code: 角色编码 (e.g., 'admin')
        :return: Boolean
        """
        return any(role.code == role_code for role in self.roles)

    def has_permission(self, permission_code):
        """
        检查用户是否拥有指定编码的权限（通过其角色）。
        :param permission_code: 权限编码 (e.g., 'user:create')
        :return: Boolean
        """
        # 遍历用户的所有角色
        for role in self.roles:
            # 遍历角色的所有权限
            for perm in role.permissions:
                if perm.code == permission_code:
                    return True
        return False

    # --- 数据转换方法 ---
    def to_dict(self):
        """将用户对象转换为包含完整信息的字典，用于API响应。"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'roles': [role.to_dict() for role in self.roles]  # 假设Role模型也有to_dict方法
        }

    def to_jwt_dict(self):
        """将用户对象转换为包含JWT所需核心信息的字典。"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'roles': [{'id': role.id, 'name': role.name, 'code': role.code} for role in self.roles],
            'permissions': list(set(p.code for r in self.roles for p in r.permissions)) # 将所有权限编码聚合
        }

    def get_jwt_identity(self):
        """
        获取用于JWT identity的值。
        Flask-JWT-Extended推荐使用字符串类型的ID。
        """
        return str(self.id)