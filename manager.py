
from flask_wtf.csrf import CSRFProtect
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from config import Config
app=Flask(__name__)



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