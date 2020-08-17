from flask_wtf.csrf import CSRFProtect
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from config import config_dict
from .modules.index import index_blue
def creat_app(config_name):
    app=Flask(__name__)

    #根据传入的配置类名称，取出对于的配置类
    config=config_dict.get(config_name)

    #加载配置类
    app.config.from_object(config)

    #创建SQLAlchemy对象，关联app
    db=SQLAlchemy(app)

    #创建Redis对象
    redis_store = StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)

    #创建Session对象，读取APP中session配置信息
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    #将首页蓝图注册到app中
    app.register_blueprint(index_blue)

    return app