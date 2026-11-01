# backend/models/__init__.py

"""
模型包初始化文件

这个文件的主要作用是：
1. 方便地从包外部导入模型类。当其他模块需要使用模型时，可以直接写 `from models import User`，
   而不需要写 `from models.user import User`，简化了导入路径。
2. 使用 `__all__` 变量明确定义了当使用 `from models import *` 时，哪些模块或变量会被导入。
   这是一种良好的编程实践，可以避免无意中导入不必要的模块。
"""

from .order import Order, OrderItem
from .permission import Permission
from .product import Product
from .role import Role
# 从各个模型文件中导入主要的类和关联表
from .user import User, user_roles, role_permissions

# 定义 `from models import *` 时要导出的公开接口
__all__ = [
    'User',
    'Order',
    'OrderItem',
    'Role',
    'Permission',
    'Product',
    'user_roles',        # 用户和角色的多对多关联表
    'role_permissions'   # 角色和权限的多对多关联表
]