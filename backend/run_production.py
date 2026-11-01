#!/usr/bin/env python3
"""
生产环境启动脚本

该脚本使用 Waitress WSGI 服务器来运行Flask应用，适用于生产环境。
它会明确设置环境变量以关闭调试模式，并打印出启动信息。
"""

import os

from waitress import serve  # 导入Waitress服务器

from app import create_app  # 从app模块导入应用工厂函数
from extensions import db  # 导入数据库实例

# --- 1. 强制设置环境变量为生产模式 ---
# 这确保了即使在其他地方有不同的设置，这里也会覆盖为生产环境配置
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

def main():
    """
    主函数，用于创建应用并启动服务器。
    """
    # --- 2. 创建Flask应用实例 ---
    app = create_app()
    
    # --- 3. 再次确认关闭调试模式 ---
    # 双重保险，确保应用不在调试模式下运行
    app.debug = False
    app.config['DEBUG'] = False
    
    # --- 4. 初始化数据库 ---
    # 在应用上下文中创建所有数据库表（如果它们尚不存在）
    with app.app_context():
        db.create_all()
    
    # --- 5. 打印启动信息 ---
    # 向控制台输出清晰的启动信息，方便运维
    print("=" * 50)
    print("🚀 后台管理系统启动 (生产模式 - Waitress)")
    print("=" * 50)
    print(f"  📍 服务地址: http://127.0.0.1:5000")
    print(f"  🌐 可用网络: http://0.0.0.0:5000 (可供局域网访问)")
    print(f"  🔧 并发线程数: 16")
    # 根据配置显示SQL日志状态
    sql_echo_status = '开启' if app.config.get('SQLALCHEMY_ECHO') else '关闭'
    print(f"  📜 SQL日志: {sql_echo_status}")
    print("=" * 50)
    
    # --- 6. 使用 Waitress 启动服务器 ---
    # serve是Waitress的启动函数
    # app: 要运行的Flask应用
    # host='0.0.0.0': 监听所有可用的网络接口
    # port=5000: 监听5000端口
    # threads=16: 设置工作线程数为16，以处理并发请求
    serve(app, host='0.0.0.0', port=5000, threads=16)

# 当脚本作为主程序执行时，调用main函数
if __name__ == '__main__':
    main()
