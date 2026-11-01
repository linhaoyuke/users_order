# generate_hash.py
# 该脚本专门用于在您当前的环境中生成一个有效的密码哈希。

try:
    # 导入 werkzeug 库中的密码哈希函数
    from werkzeug.security import generate_password_hash

    # 您想要设置的密码
    plain_password = 'admin123'

    # 生成哈希值
    hashed_password = generate_password_hash(plain_password)
    
    # 打印清晰的分割线和结果
    print("\n请完整复制下面分割线之间的哈希密码：")
    print("-" * 70)
    print(hashed_password)
    print("-" * 70)
    print("\n然后，使用这个哈希密码去更新数据库中的 admin 用户。")

except ImportError:
    print("\n[错误] 无法导入 'werkzeug' 库。")
    print("请确保您已经激活了项目的 Python 虚拟环境 (backend)。")
    print("如果您确认已激活，但仍然报错，请尝试重新安装库: uv pip install werkzeug")
except Exception as e:
    print(f"\n发生未知错误: {e}")

