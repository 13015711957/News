from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from config import config_dict
import logging

from info.utils.commons import hot_news_filter

redis_store = None
db = SQLAlchemy()


def creat_app(config_name):
    app = Flask(__name__)

    # 根据传入的配置类名称，取出对于的配置类
    config = config_dict.get(config_name)

    # 加载日志
    log_file(config.LEVEL_NAME)

    # 加载配置类
    app.config.from_object(config)

    # 创建SQLAlchemy对象，关联app
    db.init_app(app)

    # 创建Redis对象
    global redis_store
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 创建Session对象，读取APP中session配置信息
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    # 将首页蓝图index_blue注册到app中
    from .modules.index import index_blue
    app.register_blueprint(index_blue)

    # 将认证蓝图passport_blue注册到app中
    from .modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    # 将新闻蓝图news_blue注册到app中
    from .modules.news import news_blue
    app.register_blueprint(news_blue)

    # 将用户蓝图news_blue注册到app中
    from .modules.profile import profile_blue
    app.register_blueprint(profile_blue)

    # 将管理员蓝图admin_blue,注册到app中
    from .modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    # 将函数添加到系统默认的过滤器列表
    app.add_template_filter(hot_news_filter, 'my_filter')

    # 使用请求钩子拦截所有请求，在cookie中设置csrf_token
    @app.after_request
    def after_request(resp):
        csrf_token = generate_csrf()

        resp.set_cookie('csrf_token', csrf_token)
        return resp
    return app


def log_file(LEVEL_NAME):
    # 设置日志的记录等级
    logging.basicConfig(level=LEVEL_NAME)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录个数，日志等级，输入日志信息的文件名，行数，日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
