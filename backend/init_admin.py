#!/usr/bin/env python3
"""
初始化admin用户脚本

该脚本用于在系统中创建初始的管理员（admin）用户和角色。
可以直接运行此脚本来完成初始化。
"""

# 导入Flask应用和相关配置、扩展及模型
from flask import Flask

from config import Config
from extensions import db, db_session
from models.role import Role
from models.user import User


def create_admin_user():
    """
    创建管理员用户和角色的主函数。
    """
    # 创建一个临时的Flask应用实例，以便使用应用上下文
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化数据库扩展
    db.init_app(app)
    
    # 推入应用上下文，确保数据库操作可以正常进行
    with app.app_context():
        try:
            # --- 1. 检查admin用户是否已存在 ---
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("Admin用户已存在！")
                print(f"  用户名: {existing_admin.username}")
                print(f"  邮箱: {existing_admin.email}")
                return  # 如果存在，则直接退出

            # --- 2. 创建或获取admin角色 ---
            admin_role = Role.query.filter_by(code='admin').first()
            if not admin_role:
                print("创建admin角色...")
                # 如果'admin'角色不存在，则创建一个新的
                admin_role = Role(name='管理员', code='admin', description='拥有所有权限的系统管理员')
                db_session.add(admin_role)
                db_session.commit()  # 提交到数据库
                print("Admin角色创建成功！")
            
            # --- 3. 创建admin用户 ---
            print("创建admin用户...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='系统管理员',
                is_active=True  # 默认激活用户
            )
            
            # --- 4. 设置密码 ---
            # 使用User模型中定义的set_password方法来设置和哈希密码
            admin_user.set_password('admin123')
            
            # --- 5. 分配角色 ---
            # 将admin角色分配给新创建的admin用户
            admin_user.roles.append(admin_role)
            
            # --- 6. 保存到数据库 ---
            db_session.add(admin_user)
            db_session.commit()
            
            # --- 7. 打印成功信息 ---
            print("=" * 50)
            print("🎉 Admin用户创建成功！")
            print("=" * 50)
            print(f"  用户名: admin")
            print(f"  密  码: admin123")
            print(f"  邮  箱: admin@example.com")
            print(f"  角  色: 管理员")
            print("=" * 50)
            
            # 显示存储在数据库中的哈希密码，用于验证
            print(f"数据库中的加密密码: {admin_user.password}")
            
        except Exception as e:
            # 如果发生任何异常，打印错误信息并回滚数据库会话
            print(f"❌ 创建admin用户失败: {e}")
            db_session.rollback()

# 当脚本作为主程序执行时，调用创建函数
if __name__ == "__main__":
    create_admin_user()