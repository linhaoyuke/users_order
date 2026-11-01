# backend/models/role.py

from extensions import db
from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.orm import relationship, backref

class Role(db.Model):  # type: ignore
    """
    角色模型，代表系统中的一个角色（如管理员、普通用户等）。
    """
    __tablename__ = 'roles'  # 定义在数据库中的表名

    # --- 字段定义 ---
    id = Column(BigInteger, primary_key=True)  # 主键ID
    name = Column(String(50), unique=True, nullable=False)  # 角色名称，唯一且不为空
    code = Column(String(50), unique=True, nullable=False)  # 角色编码，用于程序内部判断，唯一且不为空
    description = Column(Text)  # 角色描述

    # --- 关系定义 ---
    # 与Permission模型的多对多关系
    # secondary='role_permissions' 指定了在 user.py 中定义的中间表
    # backref='roles' 使得在Permission模型中可以通过 .roles 访问关联的所有角色
    permissions = relationship(
        'Permission',
        secondary='role_permissions',
        backref=backref('roles', lazy='dynamic')
    )

    def to_dict(self):
        """将角色对象转换为字典，方便API返回。"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'permissions': [p.to_dict() for p in self.permissions] # 假设Permission模型也有to_dict方法
        }