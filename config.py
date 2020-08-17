from redis import StrictRedis
from datetime import timedelta
#设置配置信息
class Config(object):
    #调试信息
    DEGUG=True

    SECRET_KEY="137946"

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis配置信息
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

    #session配置信息
    SESSION_TYPE="redis"
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER= True
    PERMANENT_SESSION_LIFETIME=timedelta(days=2)

#开发环境配置信息
class DevelopConfig(Config):
    pass

#生产环境配置信息
class ProductConfig(Config):
    pass

#测试环境配置信息
class TestConfig(Config):
    pass

#同一访问入口
config_dict = {
    'develop':DevelopConfig,
    'product':ProductConfig,
    'test':TestConfig
}