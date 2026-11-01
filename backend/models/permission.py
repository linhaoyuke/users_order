# backend/models/permission.py

from extensions import db
from sqlalchemy import Column, BigInteger, String, Text

class Permission(db.Model):  # type: ignore
    """
    权限模型，定义了系统中的具体操作权限。
    采用基于资源和动作（Resource-Based Access Control, RBAC的变种）的设计。
    例如：对'user'（资源）有'create'（动作）的权限。
    """
    __tablename__ = 'permissions'  # 定义在数据库中的表名

    # --- 字段定义 ---
    id = Column(BigInteger, primary_key=True)  # 主键ID
    name = Column(String(50), unique=True, nullable=False)  # 权限的显示名称，如"创建用户"，唯一且不为空
    code = Column(String(50), unique=True, nullable=False)  # 权限的编码，如"user:create"，用于程序内部判断，唯一且不为空
    description = Column(Text)  # 权限的详细描述
    
    # --- 基于资源和动作的字段 ---
    resource = Column(String(50), nullable=False)  # 权限所关联的资源名称，如 "user", "order"
    action = Column(String(50), nullable=False)    # 权限所代表的操作类型，如 "create", "read", "update", "delete"

    def to_dict(self):
        """将权限对象转换为字典，方便API返回。"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'resource': self.resource,
            'action': self.action
        }