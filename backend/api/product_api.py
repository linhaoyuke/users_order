from extensions import db_session
from flask import Blueprint, request, jsonify
from models import Product
from models.operation_log import LogModule
from schemas.product import product_schema, products_schema
from sqlalchemy import desc
from utils.jwt import permission_required
# 导入操作日志相关模块
from utils.log_helper import LogHelper, LogAction, LogStatus

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=['GET'])
@permission_required('view_product')
def get_products():
    """
    获取所有商品
    支持按商品名称(name)进行筛选。
    支持分页查询。
    """
    # 构建基础查询
    query = Product.query.order_by(desc(Product.created_at))

    # 筛选参数
    name = request.args.get('name')
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    # 准备响应数据
    response = {
        'items': products_schema.dump(products),
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }
    
    return jsonify(response)

@product_bp.route('/<string:id>', methods=['GET'])
@permission_required('view_product')
def get_product(id):
    """获取单个商品"""
    product = Product.query.get_or_404(id)
    return jsonify(product_schema.dump(product))

@product_bp.route('/', methods=['POST'])
@permission_required('manage_product')
def create_product():
    """创建新商品"""
    data = request.get_json()
    errors = product_schema.validate(data)
    if errors:
        # 记录验证失败日志
        LogHelper.log_product_operation(
            action=LogAction.CREATE,
            product_data=data,
            status=LogStatus.FAILED,
            error_message=f"数据验证失败: {errors}"
        )
        return jsonify(errors), 400
    
    try:
        new_product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            stock=data['stock'],
            initial_stock=data['stock']
        )
        
        db_session.add(new_product)
        db_session.commit()
        
        # 准备日志数据
        log_data = {
            'name': new_product.name,
            'description': new_product.description,
            'price': float(new_product.price),
            'stock': new_product.stock,
            'initial_stock': new_product.initial_stock,
            'product_id': new_product.id
        }
        
        # 记录成功日志
        LogHelper.log_product_operation(
            action=LogAction.CREATE,
            product_data=log_data,
            resource_id=new_product.id,
            description=f"创建商品 - {new_product.name}"
        )
        
        return jsonify(product_schema.dump(new_product)), 201
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_product_operation(
            action=LogAction.CREATE,
            product_data=data,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({'message': f'创建商品失败: {str(e)}'}), 500

@product_bp.route('/<string:id>', methods=['PUT'])
@permission_required('manage_product')
def update_product(id):
    """更新商品信息"""
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    # 获取更新前的数据用于日志记录
    old_data = {
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'initial_stock': product.initial_stock
    }
    
    try:
        # 检查库存调整
        stock_adjusted = False
        if 'stock' in data and data['stock'] != product.stock:
            stock_adjusted = True
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock = data.get('stock', product.stock)
        
        db_session.commit()
        
        # 准备日志数据（更新后的数据）
        new_data = {
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'initial_stock': product.initial_stock
        }
        
        # 如果是库存调整，使用库存调整操作类型
        if stock_adjusted:
            action = LogAction.ADJUST_STOCK
            description = f"调整库存 - {product.name} (从 {old_data['stock']} 到 {new_data['stock']})"
            new_data['stock_change'] = new_data['stock'] - old_data['stock']
        else:
            action = LogAction.UPDATE
            description = f"更新商品信息 - {product.name}"
        
        # 记录成功日志
        LogHelper.log_product_operation(
            action=action,
            product_data=new_data,
            old_data=old_data,
            resource_id=id,
            description=description
        )
        
        return jsonify(product_schema.dump(product))
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_product_operation(
            action=LogAction.UPDATE,
            product_data=data,
            old_data=old_data,
            resource_id=id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({'message': f'更新商品失败: {str(e)}'}), 500

@product_bp.route('/<string:id>', methods=['DELETE'])
@permission_required('manage_product')
def delete_product(id):
    """删除商品"""
    product = Product.query.get_or_404(id)
    
    # 获取商品信息用于日志记录
    product_data = {
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'initial_stock': product.initial_stock,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }
    
    try:
        db_session.delete(product)
        db_session.commit()
        
        # 记录成功日志
        LogHelper.log_product_operation(
            action=LogAction.DELETE,
            old_data=product_data,
            resource_id=id,
            description=f"删除商品 - {product_data['name']}"
        )
        
        return jsonify({'message': '商品已删除'}), 200
        
    except Exception as e:
        db_session.rollback()
        # 记录失败日志
        LogHelper.log_product_operation(
            action=LogAction.DELETE,
            old_data=product_data,
            resource_id=id,
            status=LogStatus.FAILED,
            error_message=str(e)
        )
        return jsonify({'message': f'删除商品失败: {str(e)}'}), 500
