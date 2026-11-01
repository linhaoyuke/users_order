# backend/schemas/permission.py

from extensions import ma  # 导入Marshmallow实例
from marshmallow import fields, validate
from models.permission import Permission


class PermissionSchema(ma.SQLAlchemyAutoSchema):
    """
    用于序列化和反序列化Permission模型的Schema。
    """
    # 添加验证规则
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    code = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    resource = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    action = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    class Meta:
        model = Permission
        load_instance = True  # 在加载时创建模型实例
        # 定义需要序列化/反序列化的字段
        fields = ('id', 'name', 'code', 'description', 'resource', 'action')
