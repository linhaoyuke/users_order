# backend/utils/db.py

from extensions import db, db_session
from models.permission import Permission
from models.role import Role
from models.user import User


def init_database():
    """
    初始化数据库，创建所有表并填充初始数据。
    
    这个函数是一个更全面的初始化脚本，它会创建：
    1. 所有的数据库表。
    2. 默认的角色（管理员、普通用户、运营）。
    3. 默认的权限（用户管理、订单管理等）。
    4. 将权限分配给角色。
    5. 创建一个拥有管理员角色的超级管理员用户。
    
    注意：此函数仅在数据库为空时执行数据填充，以避免重复创建。
    它比 `init_admin.py` 更完整，适用于首次部署或完全重置数据库的场景。
    """
    # 创建所有在模型中定义的表
    db.create_all()
    
    # 检查数据库是否已经有角色数据，如果没有才进行初始化
    if Role.query.count() > 0:
        print("数据库已包含初始数据，跳过初始化。")
        return

    print("数据库为空，开始填充初始数据...")

    # --- 1. 创建默认角色 ---
    admin_role = Role(name='管理员', code='admin', description='系统管理员，拥有所有权限')
    user_role = Role(name='普通用户', code='user', description='普通注册用户')
    operator_role = Role(name='运营人员', code='operator', description='负责订单处理等运营工作')
    
    db_session.add_all([admin_role, user_role, operator_role])
    db_session.commit()
    print("  - 默认角色创建成功。")

    # --- 2. 创建默认权限 ---
    permissions = [
        # 用户管理
        Permission(name='查看用户', code='user:read', resource='user', action='read'),
        Permission(name='创建用户', code='user:create', resource='user', action='create'),
        Permission(name='编辑用户', code='user:update', resource='user', action='update'),
        Permission(name='删除用户', code='user:delete', resource='user', action='delete'),
        # 角色和权限管理
        Permission(name='管理角色', code='role:manage', resource='role', action='manage'),
        Permission(name='管理权限', code='permission:manage', resource='permission', action='manage'),
        # 订单管理
        Permission(name='查看订单', code='order:read', resource='order', action='read'),
        Permission(name='创建订单', code='order:create', resource='order', action='create'),
        Permission(name='编辑订单', code='order:update', resource='order', action='update'),
        # 商品管理
        Permission(name='查看商品', code='product:read', resource='product', action='read'),
        Permission(name='创建商品', code='product:create', resource='product', action='create'),
        Permission(name='编辑商品', code='product:update', resource='product', action='update'),
        Permission(name='删除商品', code='product:delete', resource='product', action='delete'),
        # 操作日志管理
        Permission(name='查看日志', code='log:view', resource='log', action='view'),
        Permission(name='导出日志', code='log:export', resource='log', action='export'),
        Permission(name='管理日志', code='log:manage', resource='log', action='manage'),
        # 系统管理
        Permission(name='查看仪表盘', code='dashboard:read', resource='dashboard', action='read'),
    ]
    
    db_session.add_all(permissions)
    db_session.commit()
    print("  - 默认权限创建成功。")

    # --- 3. 分配权限给角色 ---
    # 管理员拥有所有权限
    admin_role.permissions = Permission.query.all()
    
    # 运营人员拥有订单查看和修改权限
    operator_role.permissions = Permission.query.filter(Permission.resource == 'order').all()
    
    # 普通用户只拥有查看自己订单的权限（这个在代码逻辑里控制，这里可以不分配特定权限）
    
    db_session.commit()
    print("  - 权限已成功分配给角色。")

    # --- 4. 创建超级管理员用户 ---
    admin_user = User(
        username='admin',
        email='admin@example.com',
        full_name='系统管理员',
        is_active=True
    )
    admin_user.set_password('admin123')  # 设置并哈希密码
    admin_user.roles.append(admin_role)  # 分配管理员角色
    
    db_session.add(admin_user)
    db_session.commit()
    print("  - 超级管理员用户创建成功。")
    
    print("\n数据库初始化完成！")
    print("  - 管理员账号: admin")
    print("  - 初始密码: admin123")