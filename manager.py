from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
#设置配置信息
class Config(object):
    #调试信息
    DEGUG=True

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)

db=SQLAlchemy(app)

@app.route('/')
def index():
    return "helloworld"

if __name__ == '__main__':
    app.run()