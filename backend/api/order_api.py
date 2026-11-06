# backend/api/order_api.py

from extensions import db, db_session
# 导入所需模块
from flask import Blueprint, request, jsonify, current_app
from models import Order, OrderItem, User, Product
from models.operation_log import LogModule
from schemas.order import OrderSchema
from snowflake import SnowflakeGenerator
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from utils.jwt import jwt_required, get_current_user
# 导入操作日志相关模块
from utils.log_helper import LogHelper, LogAction, LogStatus

# 创建雪花ID生成器
# 实例化生成器
# 必须为每个工作进程/节点分配唯一的实例ID
snowflake_generator = SnowflakeGenerator(1)

# 创建订单管理的蓝图
order_bp = Blueprint('orders', __name__)
# 实例化Schema
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@order_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def handle_orders():
    """
    获取订单列表或创建新订单。
    GET: 获取订单列表。
    POST: 创建一个新订单。
    """
    if request.method == 'POST':
        return create_order()

    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "用户未认证"}), 401
            
        # 使用 joinedload 预加载关联的用户和订单项的商品信息，避免 N+1 查询问题
        query = Order.query.options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        )

        # --- 过滤 ---
        args = request.args
        if args.get('status'):
            query = query.filter(Order.status == args.get('status'))
        if args.get('payment_status'):
            query = query.filter(Order.payment_status == args.get('payment_status'))
        if args.get('created_at_start'):
            query = query.filter(Order.created_at >= args.get('created_at_start'))
        end_date = args.get('created_at_end')
        if end_date:
            # 包含当天
            query = query.filter(Order.created_at <= end_date + " 23:59:59")

        # --- 搜索 ---
        if search_keyword := args.get('search'):
            # 使用 or_ 来组合多个搜索条件
            # pg_bigm 会自动加速这里的 ilike 查询
            query = query.join(Order.user).filter(
                or_(
                    Order.order_number.ilike(f"%{search_keyword}%"),
                    User.username.ilike(f"%{search_keyword}%"),
                    User.full_name.ilike(f"%{search_keyword}%"),
                    Order.status.ilike(f"%{search_keyword}%"),
                    Order.payment_status.ilike(f"%{search_keyword}%")
                )
            )

        # --- 权限控制 ---
        is_admin = any(role['code'] == 'admin' for role in current_user.get('roles', []))
        if not is_admin:
            query = query.filter(Order.user_id == current_user['id'])

        # --- 分页 ---
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        paginated_orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        orders = paginated_orders.items
        total = paginated_orders.total

        return jsonify({
            "items": orders_schema.dump(orders),
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": paginated_orders.pages,
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取订单列表时出错: {e}")
        return jsonify({"message": "获取订单列表失败"}), 500

def update_order_items_with_lock(order, new_items_data):
    """
    带悲观排他锁（SELECT ... FOR UPDATE）安全更新订单项与商品库存。
    按商品ID升序加锁以消除并发死锁隐患。
    """
    if not new_items_data:
        raise ValueError("订单项不能为空")

    # 1. 汇总旧订单项中的商品及还回数量
    old_product_qty = {}
    for item in order.items:
        pid = str(item.product_id)
        old_product_qty[pid] = old_product_qty.get(pid, 0) + item.quantity

    # 2. 汇总新订单项中的商品及需求数量（防重复商品ID）
    new_product_qty = {}
    for item_data in new_items_data:
        pid = str(item_data['product_id'])
        qty = int(item_data.get('quantity', 1))
        if qty <= 0:
            raise ValueError("商品数量必须大于0")
        new_product_qty[pid] = new_product_qty.get(pid, 0) + qty

    # 3. 收集所有相关商品ID并排序，按固定顺序加锁防死锁
    all_product_ids = sorted(list(set(old_product_qty.keys()) | set(new_product_qty.keys())))
    if not all_product_ids:
        return 0

    # 4. 加悲观排他锁（SELECT ... FOR UPDATE）
    locked_products = {
        str(p.id): p
        for p in Product.query.filter(Product.id.in_(all_product_ids))
                             .order_by(Product.id.asc())
                             .with_for_update()
                             .all()
    }

    # 检查新商品是否存在
    for pid in new_product_qty.keys():
        if pid not in locked_products:
            raise ValueError(f"商品ID {pid} 不存在")

    # 5. 还原旧库存
    for pid, old_qty in old_product_qty.items():
        if pid in locked_products:
            locked_products[pid].stock += old_qty

    # 校验并扣减新库存
    for pid, new_qty in new_product_qty.items():
        prod = locked_products[pid]
        if prod.stock < new_qty:
            raise ValueError(f"商品 '{prod.name}' 库存不足，当前可用库存: {prod.stock}")
        prod.stock -= new_qty

    # 6. 删除原有订单项并创建新订单项
    old_items = list(order.items)
    for old_item in old_items:
        order.items.remove(old_item)
        db_session.delete(old_item)
    db_session.flush()

    new_total_amount = 0
    for item_data in new_items_data:
        pid = str(item_data['product_id'])
        qty = int(item_data.get('quantity', 1))
        prod = locked_products[pid]
        new_item = OrderItem(
            order_id=order.id,
            product_id=prod.id,
            quantity=qty,
            unit_price=prod.price,
            subtotal=prod.price * qty
        )
        order.items.append(new_item)
        db_session.add(new_item)
        new_total_amount += new_item.subtotal

    order.total_amount = new_total_amount
    return new_total_amount

@order_bp.route('/<string:order_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_order(order_id):
    """处理单个订单的获取、更新和删除操作。"""

    query = Order.query.options(
        joinedload(Order.user),
        joinedload(Order.items).joinedload(OrderItem.product)
    )
    order = query.get_or_404(order_id)
    
    current_user = get_current_user()
    if not current_user:
        return jsonify({"message": "用户未认证"}), 401
        
    is_admin = any(role['code'] == 'admin' for role in current_user.get('roles', []))

    # --- 权限检查 ---
    if not is_admin and str(order.user_id) != str(current_user['id']):
        return jsonify({"message": "无权操作此订单"}), 403

    # --- 根据请求方法执行不同操作 ---
    if request.method == 'GET':
        try:
            return jsonify(order_schema.dump(order)), 200
        except Exception as e:
            current_app.logger.error(f"获取订单 {order_id} 详情时出错: {e}")
            return jsonify({"message": "获取订单详情失败"}), 500

    elif request.method == 'PUT':

        # 获取更新前的数据用于日志记录
        old_data = {
            'order_number': str(order.order_number),
            'status': order.status,
            'payment_status': order.payment_status,
            'shipping_address': order.shipping_address,
            'total_amount': float(order.total_amount),
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'Unknown',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal)
            } for item in order.items]
        }
        
        try:
            data = request.get_json()

            # 记录操作类型
            action_type = LogAction.UPDATE
            status_changed = False
            payment_status_changed = False
            

            # 管理员可以直接修改状态和地址
            if is_admin:
                if 'status' in data and data['status'] != order.status:
                    old_status = order.status
                    order.status = data['status']
                    status_changed = True
                    
                    # 根据状态变化确定操作类型
                    if data['status'] == 'cancelled':
                        action_type = LogAction.CANCEL_ORDER
                    elif data['status'] == 'completed':
                        action_type = LogAction.COMPLETE_ORDER
                    elif data['status'] == 'shipped':
                        action_type = LogAction.SHIP_ORDER
                    elif old_status == 'pending_payment' and data['status'] == 'processing':
                        action_type = LogAction.CONFIRM_ORDER
                        
                if 'payment_status' in data and data['payment_status'] != order.payment_status:
                    order.payment_status = data['payment_status']
                    payment_status_changed = True
                    
                    if data['payment_status'] == 'refunded':
                        action_type = LogAction.REFUND_ORDER
                        
                if 'shipping_address' in data:
                    order.shipping_address = data['shipping_address']
                    
                if 'items' in data:
                    update_order_items_with_lock(order, data['items'])
            
            # 普通用户只能在特定状态下修改订单
            else:
                
                # 检查订单是否允许修改（允许pending和pending_payment状态）
                if order.status not in ['pending_payment', 'pending'] or order.payment_status != 'unpaid':
                    current_app.logger.warning(f"订单状态不允许修改: status={order.status}, payment_status={order.payment_status}")
                    # 记录失败日志
                    LogHelper.log_order_operation(
                        action=LogAction.UPDATE,
                        order_data=data,
                        old_data=old_data,
                        resource_id=order_id,
                        status=LogStatus.FAILED,
                        error_message="此订单状态无法修改"
                    )
                    return jsonify({"message": "此订单状态无法修改"}), 403

                # 用户可以修改收货地址
                if 'shipping_address' in data:
                    order.shipping_address = data['shipping_address']

                if 'items' in data:
                    update_order_items_with_lock(order, data['items'])

            db_session.commit()
            
            # 准备日志数据（更新后的数据）
            updated_order = Order.query.options(
                joinedload(Order.user),
                joinedload(Order.items).joinedload(OrderItem.product)
            ).get(order_id)
            
            new_data = {
                'order_number': str(updated_order.order_number),
                'status': updated_order.status,
                'payment_status': updated_order.payment_status,
                'shipping_address': updated_order.shipping_address,
                'total_amount': float(updated_order.total_amount),
                'items': [{
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else 'Unknown',
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.subtotal)
                } for item in updated_order.items]
            }
            
            # 生成操作描述
            description = f"更新订单 - {updated_order.order_number}"
            if status_changed:
                description = f"订单状态变更 - {updated_order.order_number} (从 {old_data['status']} 到 {new_data['status']})"
            elif payment_status_changed:
                description = f"订单支付状态变更 - {updated_order.order_number} (从 {old_data['payment_status']} 到 {new_data['payment_status']})"
            
            # 记录成功日志
            LogHelper.log_order_operation(
                action=action_type,
                order_data=new_data,
                old_data=old_data,
                resource_id=order_id,
                description=description
            )
            
            # 返回更新后的完整订单信息
            return jsonify(order_schema.dump(updated_order)), 200

        except Exception as e:
            db_session.rollback()
            # 记录失败日志
            LogHelper.log_order_operation(
                action=LogAction.UPDATE,
                order_data=data if 'data' in locals() else {},
                old_data=old_data,
                resource_id=order_id,
                status=LogStatus.FAILED,
                error_message=str(e)
            )
            current_app.logger.error(f"更新订单 {order_id} 时出错: {e}")
            return jsonify({"message": f"更新订单失败: {e}"}), 500

    elif request.method == 'DELETE':
        # 获取订单信息用于日志记录
        order_data = {
            'order_number': str(order.order_number),
            'user_id': str(order.user_id),
            'status': order.status,
            'payment_status': order.payment_status,
            'shipping_address': order.shipping_address,
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'Unknown',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal)
            } for item in order.items]
        }
        
        try:
            db_session.delete(order)
            db_session.commit()
            
            # 记录成功日志
            LogHelper.log_order_operation(
                action=LogAction.DELETE,
                old_data=order_data,
                resource_id=order_id,
                description=f"删除订单 - {order_data['order_number']}"
            )
            
            return jsonify({"message": "订单删除成功"}), 200
            
        except Exception as e:
            db_session.rollback()
            # 记录失败日志
            LogHelper.log_order_operation(
                action=LogAction.DELETE,
                old_data=order_data,
                resource_id=order_id,
                status=LogStatus.FAILED,
                error_message=str(e)
            )
            current_app.logger.error(f"删除订单 {order_id} 时出错: {e}")
            return jsonify({"message": "删除订单失败"}), 500

def create_order():
    """创建一个新订单（带行级悲观锁与防死锁并发安全控制）。"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "用户未认证"}), 401
        
        data = request.get_json()

        # --- 数据校验 ---
        if not data or 'items' not in data or not data['items']:
            # 记录验证失败日志
            LogHelper.log_order_operation(
                action=LogAction.CREATE,
                order_data=data,
                status=LogStatus.FAILED,
                error_message="订单项不能为空"
            )
            return jsonify({"message": "订单项不能为空"}), 400
        
        shipping_address = data.get('shipping_address')
        if not shipping_address:
            # 如果没有提供配送地址，返回错误
            # 记录验证失败日志
            LogHelper.log_order_operation(
                action=LogAction.CREATE,
                order_data=data,
                status=LogStatus.FAILED,
                error_message="缺少配送地址"
            )
            return jsonify({"message": "缺少配送地址"}), 400

        # 1. 聚合各商品的购买数量（防同商品多次传入）并校验数量有效性
        item_qty_map = {}
        for item_data in data['items']:
            pid = str(item_data['product_id'])
            qty = int(item_data.get('quantity', 1))
            if qty <= 0:
                return jsonify({"message": "商品购买数量必须大于0"}), 400
            item_qty_map[pid] = item_qty_map.get(pid, 0) + qty

        # 2. 排序商品ID，消除死锁隐患（Deadlock Prevention）
        sorted_pids = sorted(item_qty_map.keys())

        # 3. 按统一顺序加排他锁（SELECT ... FOR UPDATE）
        locked_products = {
            str(p.id): p
            for p in Product.query.filter(Product.id.in_(sorted_pids))
                                 .order_by(Product.id.asc())
                                 .with_for_update()
                                 .all()
        }

        # 检查商品是否存在
        for pid in sorted_pids:
            if pid not in locked_products:
                LogHelper.log_order_operation(
                    action=LogAction.CREATE,
                    order_data=data,
                    status=LogStatus.FAILED,
                    error_message=f"商品ID {pid} 不存在"
                )
                return jsonify({"message": f"商品ID {pid} 不存在"}), 404

        # 4. 校验库存并执行扣减
        for pid in sorted_pids:
            needed_qty = item_qty_map[pid]
            prod = locked_products[pid]
            if prod.stock < needed_qty:
                db_session.rollback()
                LogHelper.log_order_operation(
                    action=LogAction.CREATE,
                    order_data=data,
                    status=LogStatus.FAILED,
                    error_message=f"商品 '{prod.name}' 库存不足"
                )
                return jsonify({
                    "message": f"商品 '{prod.name}' 库存不足",
                    "details": {
                        "product_id": pid,
                        "product_name": prod.name,
                        "requested": needed_qty,
                        "available": prod.stock
                    }
                }), 400

            # 扣减库存
            prod.stock -= needed_qty

        # 5. 构建订单项及小计
        total_price = 0
        order_items = []
        product_info_list = []

        for item_data in data['items']:
            pid = str(item_data['product_id'])
            qty = int(item_data.get('quantity', 1))
            prod = locked_products[pid]
            subtotal = prod.price * qty
            total_price += subtotal

            order_item = OrderItem(
                product_id=prod.id,
                quantity=qty,
                unit_price=prod.price,
                subtotal=subtotal
            )
            order_items.append(order_item)

            product_info_list.append({
                'product_id': str(prod.id),
                'product_name': prod.name,
                'quantity': qty,
                'unit_price': float(prod.price),
                'subtotal': float(subtotal)
            })

        # 6. 生成雪花ID并持久化订单
        order_number = next(snowflake_generator)
        new_order = Order(
            order_number=order_number,
            user_id=current_user['id'],
            total_amount=total_price,
            shipping_address=shipping_address,
            status='pending',
            payment_status='unpaid',
            items=order_items
        )

        db_session.add(new_order)
        db_session.commit()
        
        # 7. 准备日志数据并返回
        log_data = {
            'order_number': str(order_number),
            'user_id': current_user['id'] if current_user else None,
            'total_amount': float(total_price),
            'shipping_address': shipping_address,
            'status': 'pending',
            'payment_status': 'unpaid',
            'items': product_info_list,
            'order_id': str(new_order.id)
        }
        
        # 记录成功日志
        LogHelper.log_order_operation(
            action=LogAction.CREATE,
            order_data=log_data,
            resource_id=str(new_order.id),
            description=f"创建订单 - {order_number}"
        )

        # 使用预加载的查询来返回完整的订单信息
        order_with_details = Order.query.options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product)
        ).get(new_order.id)

        return jsonify(order_schema.dump(order_with_details)), 201

    except IntegrityError as e:
        db_session.rollback()
        LogHelper.log_order_operation(
            action=LogAction.CREATE,
            order_data=data if 'data' in locals() else {},
            status=LogStatus.FAILED,
            error_message="并发冲突或数据库库存约束触发"
        )
        return jsonify({"message": "库存扣减失败或并发冲突，请稍后重试"}), 400

    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_order_operation(
            action=LogAction.CREATE,
            order_data=data if 'data' in locals() else {},
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        current_app.logger.error(f"创建订单时出错: {e}")
        return jsonify({"message": f"创建订单失败: {str(e)}"}), 500

