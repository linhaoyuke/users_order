# backend/api/stats_api.py

from extensions import db_session, cache
# 导入所需模块
from flask import Blueprint, jsonify
from models.order import Order
from models.permission import Permission
from models.product import Product
from models.role import Role
from models.user import User
from sqlalchemy import func
from utils.jwt import jwt_required

# 创建统计数据的蓝图
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET'])
@jwt_required()  # 保护路由，需要登录
@cache.cached(timeout=300)  # 缓存此接口的响应5分钟，减轻数据库压力
def get_dashboard_stats():
    """
    获取仪表盘所需的综合统计数据。
    此接口聚合了用户、订单、角色和权限的统计信息。
    """
    try:
        # --- 用户统计 ---
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # --- 订单统计 ---
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending_payment').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        # 使用sqlalchemy.func.sum来计算总金额，如果无订单则返回0
        total_amount = db_session.query(func.sum(Order.total_amount)).scalar() or 0
        
        # --- 角色统计 ---
        total_roles = Role.query.count()
        # 统计有多少角色至少被一个用户使用
        active_roles = Role.query.filter(Role.users.any()).count()
        
        # --- 权限统计 ---
        total_permissions = Permission.query.count()
        # 统计有多少权限至少被一个角色使用
        active_permissions = Permission.query.filter(Permission.roles.any()).count()

        # --- 商品统计 ---
        total_products = Product.query.count()
        # 统计有多少商品库存大于0
        in_stock_products = Product.query.filter(Product.stock > 0).count()
        
        # --- 组合结果 ---
        result = {
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users
            },
            "order_stats": {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "completed_orders": completed_orders,
                "total_amount": float(total_amount)  # 确保金额是浮点数
            },
            "role_stats": {
                "total_roles": total_roles,
                "active_roles": active_roles
            },
            "permission_stats": {
                "total_permissions": total_permissions,
                "active_permissions": active_permissions
            },
            "product_stats": {
                "total_products": total_products,
                "in_stock_products": in_stock_products
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        # 异常处理
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"获取统计数据失败: {str(e)}"}), 500
