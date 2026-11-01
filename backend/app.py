# 导入所需模块
import json  # 导入JSON模块
from datetime import datetime  # 导入datetime用于处理时间

from flask import Flask, jsonify  # 导入Flask框架和jsonify用于返回JSON响应
from flask_cors import CORS  # 导入CORS以处理跨域请求

from api import api_bp  # 导入API蓝图
from config import Config  # 导入配置文件
from extensions import db, cache, sess, db_session  # 导入数据库和缓存扩展
from utils.jwt import jwt  # 导入JWT扩展


# 工厂函数，用于创建Flask应用实例
def create_app(config_class=Config):
    """
    创建并配置一个Flask应用实例。
    :param config_class: 配置类，默认为Config
    :return: Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    # 从配置对象中加载配置
    app.config.from_object(config_class)

    # 明确关闭调试模式，确保生产环境安全
    app.debug = False
    app.config['DEBUG'] = False

    # --- Flask-JWT-Extended 兼容性补丁 ---
    # Flask 2.2+版本后，json_encoder 属性被弃用，改用 app.json。
    # Flask-JWT-Extended 4.3.1 仍然依赖旧的 json_encoder。
    # 为了兼容性，这里提供一个自定义的JSON编码器。
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            # 如果对象是datetime类型，则格式化为ISO 8601字符串
            if isinstance(obj, datetime):
                return obj.isoformat()
            # 其他类型使用默认编码器处理
            return super().default(obj)

    # 将自定义编码器赋值给旧的json_encoder属性以兼容旧扩展
    app.json_encoder = CustomJSONEncoder

    # 尝试为新版本的Flask配置JSON provider
    try:
        from flask.json.provider import DefaultJSONProvider

        class CustomJSONProvider(DefaultJSONProvider):
            def default(self, obj):
                # 同样处理datetime对象
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        # 为应用配置新的JSON Provider
        app.json = CustomJSONProvider(app)
    except ImportError:
        # 如果是旧版本的Flask，没有DefaultJSONProvider，则忽略
        pass

    # --- SQL日志配置 ---
    # 如果应用配置为调试模式，则开启SQLAlchemy的日志记录，方便调试
    if app.config.get('DEBUG', False):
        app.config['SQLALCHEMY_ECHO'] = True

    # --- 初始化扩展 ---
    db.init_app(app)  # 初始化数据库
    jwt.init_app(app)  # 初始化JWT
    cache.init_app(app)  # 初始化缓存
    sess.init_app(app)  # 初始化Session
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # 配置CORS，允许所有来源访问/api/路径

    # --- JWT错误处理回调函数 ---
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token过期时的回调函数"""
        return jsonify({"message": "Token已过期"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Token无效时的回调函数"""
        return jsonify({"message": "无效的Token"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """请求中缺少Token时的回调函数"""
        return jsonify({"message": f"缺少Token: {error}"}), 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        """向JWT中添加额外声明，这里为空"""
        return {}

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """定义用户身份的加载方式"""
        return user
    
    # --- 注册蓝图 ---
    # 将API蓝图注册到应用，并添加URL前缀/api
    app.register_blueprint(api_bp, url_prefix='/api')

    # --- 全局错误处理 ---
    @app.errorhandler(404)
    def not_found(error):
        """处理404 Not Found错误"""
        return jsonify({"message": "资源不存在"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """处理500 Internal Server Error错误"""
        db_session.rollback()  # 发生内部错误时回滚数据库会话，防止数据不一致
        return jsonify({"message": "服务器内部错误"}), 500
    
    @app.route('/test-session')
    def test_session():
        from flask import session
        session['test_key'] = 'hello_redis'
        return "Session value set! Please check your Redis."

    # 返回配置好的应用实例
    return app

# 创建应用实例
app = create_app()

# 当该脚本作为主程序运行时
if __name__ == '__main__':
    # 明确设置环境变量为生产环境
    import os
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'

    # 在应用上下文中执行操作
    with app.app_context():
        # 创建所有定义的数据库表
        db.create_all()

    # 运行应用
    # debug=False: 关闭调试模式
    # host='0.0.0.0': 监听所有网络接口
    # port=5000: 监听5000端口
    # use_reloader=False: 禁用自动重载，适用于生产环境
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
