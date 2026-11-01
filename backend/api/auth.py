# backend/api/auth.py

# 导入所需模块
from flask import Blueprint, request, jsonify  # 导入Flask蓝图、请求对象和JSON响应功能
from models.user import User  # 导入用户模型
from utils.captcha import CaptchaGenerator  # 导入验证码生成工具
from utils.jwt import create_access_token, create_refresh_token, jwt_required, get_jwt_identity  # 导入JWT相关工具函数

# 创建一个名为 'auth' 的蓝图，用于组织认证相关的API
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    """
    获取图片验证码接口。
    ---
    responses:
      200:
        description: 成功获取验证码
        schema:
          properties:
            image:
              type: string
              description: Base64编码的验证码图片
            token:
              type: string
              description: 用于验证的唯一令牌
      500:
        description: 服务器内部错误
    """
    try:
        # 实例化验证码生成器
        captcha_generator = CaptchaGenerator()
        # 创建验证码数据（图片和答案）
        captcha_data = captcha_generator.create_captcha()

        # 返回Base64编码的图片和用于后续验证的token
        return jsonify({
            'image': captcha_data['image'],
            'token': captcha_data['token']
        }), 200
    except Exception as e:
        # 如果生成过程中出现异常，返回500错误
        return jsonify({"message": f"生成验证码失败: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口。
    需要提供用户名、密码和验证码进行认证。
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
            password:
              type: string
            captcha:
              type: string
            captcha_token:
              type: string
    responses:
      200:
        description: 登录成功，返回access_token, refresh_token和用户信息
      400:
        description: 验证码错误
      401:
        description: 用户名或密码错误，或账户未激活
    """
    # 从请求体中获取JSON数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    captcha = data.get('captcha')  # 用户输入的验证码
    captcha_token = data.get('captcha_token')  # 获取验证码时得到的token

    # --- 1. 验证验证码 ---
    if not CaptchaGenerator.verify_captcha(captcha, captcha_token):
        return jsonify({"message": "验证码错误或已过期"}), 400

    # --- 2. 验证用户身份 ---
    # 使用 joinedload 预加载角色和权限，避免在后续操作中产生额外的数据库查询
    from sqlalchemy.orm import joinedload
    user = User.query.options(
        joinedload(User.roles).joinedload('permissions')
    ).filter_by(username=username).first()

    # 检查用户是否存在、密码是否正确、账户是否激活
    if not user or not user.check_password(password) or not user.is_active:
        return jsonify({"message": "用户名或密码错误，或账户未激活"}), 401

    # --- 3. 创建JWT ---
    # 使用用户模型中定义的方法获取JWT的identity和claims
    user_claims = user.to_jwt_dict()  # 包含角色和权限等信息
    user_identity = user.get_jwt_identity()  # 通常是用户ID

    # 创建access token和refresh token
    access_token = create_access_token(
        identity=user_identity,
        additional_claims=user_claims
    )
    refresh_token = create_refresh_token(
        identity=user_identity,
        additional_claims=user_claims  # refresh token也包含用户信息，方便刷新时使用
    )

    # --- 4. 返回响应 ---
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()  # 返回用户的基本信息
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # 保护此路由，要求提供有效的refresh token
def refresh():
    """
    刷新Access Token接口。
    需要提供有效的Refresh Token。
    ---
    responses:
      200:
        description: 成功刷新，返回新的access_token
      401:
        description: Refresh Token无效或用户不存在/被禁用
    """
    try:
        # 从refresh token中获取用户身份（ID）
        current_user_id = get_jwt_identity()

        # 从数据库重新获取最新的用户信息，确保信息实时性
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({"message": "用户不存在或已被禁用"}), 401

        # 使用最新的用户信息创建新的access token
        user_claims = user.to_jwt_dict()
        access_token = create_access_token(
            identity=current_user_id,
            additional_claims=user_claims
        )
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        # 捕获可能的异常
        return jsonify({"message": "刷新token失败"}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()  # 保护此路由，要求提供有效的access token
def logout():
    """
    用户登出接口。
    在实际应用中，可以实现token黑名单机制来使token立即失效。
    ---
    responses:
      200:
        description: 成功登出
    """
    # 在无状态的JWT认证中，服务器端登出通常是可选的。
    # 前端只需删除本地存储的token即可。
    # 如果需要强制token失效，需要引入一个黑名单机制（如使用Redis存储已登出的token）。
    return jsonify({"message": "成功退出登录"}), 200
