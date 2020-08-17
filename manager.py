from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session

app=Flask(__name__)
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


app.config.from_object(Config)

db=SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

Session(app)

CSRFProtect(app)
@app.route('/')
def index():
    redis_store.set("name","hbw")
    print(redis_store.get("name"))

    session['name']='hhh'
    print(session.get('name'))
    return "helloworld"

if __name__ == '__main__':
    app.run()