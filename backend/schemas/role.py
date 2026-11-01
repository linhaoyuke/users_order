# backend/schemas/role.py

from extensions import ma  # 导入Marshmallow实例
from marshmallow import fields
from models.permission import Permission
from models.role import Role


# --- 嵌套的Schema ---

class PermissionSchema(ma.SQLAlchemyAutoSchema):
    """用于序列化Permission模型的Schema。"""
    class Meta:
        model = Permission
        load_instance = True  # 在加载时创建模型实例
        # 定义需要序列化/反序列化的字段
        fields = ('id', 'name', 'code', 'description', 'resource', 'action')

# --- 主要的Role Schema ---

class RoleSchema(ma.SQLAlchemyAutoSchema):
    """
    用于序列化和反序列化Role模型的Schema。
    """
    # 嵌套PermissionSchema来处理多对多的permissions关系
    permissions = fields.Nested(PermissionSchema, many=True)

    class Meta:
        model = Role
        load_instance = True  # 在加载时创建模型实例
        # 定义需要序列化/反序列化的字段
        fields = ('id', 'name', 'code', 'description', 'permissions')
