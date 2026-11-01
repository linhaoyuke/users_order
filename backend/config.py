# 导入os模块用于处理文件路径和环境变量
import os

import redis
# 导入load_dotenv用于从.env文件中加载环境变量
from dotenv import load_dotenv

# 获取当前文件所在的目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))
# 加载.env文件中的环境变量
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    应用配置类。
    包含应用所需的所有配置项，如密钥、数据库URI、JWT设置等。
    """
    # --- 通用配置 ---
    # Flask应用的密钥，用于加密session等，应该是一个复杂的、难以猜测的字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # --- 数据库配置 ---
    # SQLAlchemy数据库连接URI
    # 优先使用环境变量中的DATABASE_URL，否则使用默认的PostgreSQL连接字符串
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://devuser:devpass@47.121.117.190:6789/mydb'
    # 关闭SQLAlchemy的事件通知系统，以减少开销
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 是否在控制台打印执行的SQL语句，True为开启，生产环境建议关闭
    SQLALCHEMY_ECHO = True  # 在生产环境中通常设置为False

    # --- 应用行为配置 ---
    # 是否开启调试模式，生产环境中必须为False
    DEBUG = False
    # 是否开启测试模式
    TESTING = False

    # --- JWT（JSON Web Token）配置 ---
    # JWT签名密钥
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    # Access Token的过期时间（秒），这里是1小时
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    # Refresh Token的过期时间（秒），这里是1天
    JWT_REFRESH_TOKEN_EXPIRES = 86400

    # --- 缓存配置 (Flask-Caching) ---
    # 缓存类型，这里使用Redis
    CACHE_TYPE = 'redis'
    # Redis服务器的连接URL
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://:qqwwee@47.121.117.190:7890/0'
    # 默认的缓存超时时间（秒）
    CACHE_DEFAULT_TIMEOUT = 1200

    # --- Session配置 (用于验证码) ---
    # Session的存储类型，这里使用redis
    SESSION_TYPE = 'redis'
    # 指定session存储所用的redis实例
    SESSION_REDIS = redis.from_url(CACHE_REDIS_URL)
    # Session是否永久有效
    SESSION_PERMANENT = False
    # 是否对Session ID进行签名，增加安全性
    SESSION_USE_SIGNER = True
    # Session键的前缀
    SESSION_KEY_PREFIX = 'captcha:'

    def __init__(self):
        """
        构造函数，在实例化时强制设置环境变量，确保应用在生产模式下运行。
        """
        # 确保Flask的调试模式环境变量为'0'（关闭）
        os.environ['FLASK_DEBUG'] = '0'
        # 确保Flask的环境变量为'production'
        os.environ['FLASK_ENV'] = 'production'
