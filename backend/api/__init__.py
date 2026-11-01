# backend/api/__init__.py

# 导入Flask的蓝图（Blueprint）功能，用于模块化应用
from flask import Blueprint

# 创建一个名为 'api' 的主蓝图
# 这个蓝图将作为所有API子蓝图的容器
api_bp = Blueprint('api', __name__)

# --- 导入各个模块的子蓝图 ---
# 从同级目录下的文件中导入各自的蓝图实例
from .auth import auth_bp  # 认证相关的API
from .user_api import user_bp  # 用户管理相关的API
from .role_api import role_bp  # 角色管理相关的API
from .permission_api import permission_bp  # 权限管理相关的API
from .order_api import order_bp  # 订单管理相关的API
from .stats_api import stats_bp  # 统计数据相关的API
from .product_api import product_bp # 商品管理相关的API
# 临时注释操作日志API导入，先让系统启动
# from .operation_log_api import operation_log_bp  # 操作日志相关的API

# --- 注册子蓝图到主蓝图 ---
# 将导入的子蓝图注册到 'api_bp' 上，并为每个子蓝图指定URL前缀
# 这样做可以更好地组织URL结构，例如所有用户相关的API都会在 /api/users/ 路径下
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(role_bp, url_prefix='/roles')
api_bp.register_blueprint(permission_bp, url_prefix='/permissions')
api_bp.register_blueprint(order_bp, url_prefix='/orders')
api_bp.register_blueprint(stats_bp, url_prefix='/stats')
api_bp.register_blueprint(product_bp, url_prefix='/products')
# 临时注释操作日志API注册
# api_bp.register_blueprint(operation_log_bp, url_prefix='/operation-logs')
