import logging

from redis import StrictRedis
from datetime import timedelta


# 设置配置信息
class Config(object):
    # 调试信息
    DEBUG = False

    SECRET_KEY = "137946"


    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 自动提交

    # redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session配置信息
    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    # 默认日志级别
    LEVEL_NAME = logging.DEBUG


# 开发环境配置信息
class DevelopConfig(Config):
    DEBUG = True
    pass


# 生产环境配置信息
class ProductConfig(Config):
    DEBUG = False
    LEVEL_NAME = logging.ERROR
    pass


# 测试环境配置信息
class TestConfig(Config):
    pass


# 同一访问入口
config_dict = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'test': TestConfig
}
