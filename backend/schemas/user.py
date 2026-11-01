# backend/schemas/user.py

from extensions import ma  # 导入Marshmallow实例
from marshmallow import fields, validate
from models.role import Role
from models.user import User


# --- 嵌套的Schema ---

class RoleSchema(ma.SQLAlchemyAutoSchema):
    """用于序列化Role模型的Schema。"""
    class Meta:
        model = Role
        load_instance = True  # 在加载时创建模型实例
        # 定义需要序列化/反序列化的字段
        fields = ('id', 'name', 'code', 'description')

# --- 主要的User Schema ---

class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    用于序列化User模型的Schema。
    这是最完整的Schema，通常用于读取和返回用户信息。
    """
    id = fields.UUID(dump_only=True)
    # 嵌套RoleSchema来处理多对多的roles关系
    roles = fields.Nested(RoleSchema, many=True)

    class Meta:
        model = User
        load_instance = True  # 在加载时创建模型实例
        # 定义需要序列化/反序列化的字段
        fields = ('id', 'username', 'email', 'full_name', 'phone', 'is_active', 'created_at', 'updated_at', 'roles')

class UserCreateSchema(ma.Schema):
    """
    用于验证创建新用户时请求数据的Schema。
    只包含创建时必需或允许的字段。
    """
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)
    full_name = fields.Str(validate=validate.Length(max=100))
    phone = fields.Str(validate=validate.Length(max=20))
    is_active = fields.Bool(load_default=True)
    # 在创建时可以指定角色ID列表
    roles = fields.List(fields.Int())

class UserUpdateSchema(ma.Schema):
    """
    用于验证更新用户时请求数据的Schema。
    所有字段都是可选的。
    """
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    full_name = fields.Str(validate=validate.Length(max=100))
    phone = fields.Str(validate=validate.Length(max=20))
    is_active = fields.Bool()
    # 允许密码字段为空或不提供，只有提供时才更新
    password = fields.Str(validate=validate.Length(min=6), allow_none=True)
    # 在更新时也可以指定角色ID列表
    roles = fields.List(fields.Int())
