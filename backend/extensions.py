# backend/extensions.py

# 导入Flask-Caching扩展，用于缓存处理
from flask_caching import Cache
# 导入Flask-Marshmallow扩展，用于对象序列化和反序列化（ORM模型与JSON之间的转换）
from flask_marshmallow import Marshmallow
# 导入Flask-Session扩展
from flask_session import Session
# 导入Flask-SQLAlchemy扩展，用于数据库操作
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session as SQLAlchemySession

# 创建SQLAlchemy的实例，这个实例将在app.py中与Flask应用关联
db = SQLAlchemy()
# 为 db.session 创建一个带有明确类型提示的别名，以帮助 IDE 和类型检查器
# 将来在代码中，应该直接导入和使用 db_session 而不是 db.session
db_session: SQLAlchemySession = db.session

# 创建Marshmallow的实例，用于后续定义Schema
ma = Marshmallow()

# 创建Cache的实例，用于缓存配置和使用
cache = Cache()

# 创建Session的实例
sess = Session()

# 注意：这里只创建了扩展的实例，但没有进行初始化。
# 真正的初始化（即与Flask app的绑定）是在应用工厂函数create_app中通过调用db.init_app(app)等完成的。
# 这种方式有利于在测试或不同配置下创建多个应用实例。
