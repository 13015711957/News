from . import index_blue
from info import redis_store

@index_blue.route('/',methods=['GET','POST'])
def index():
    redis_store.set("name","hbw")
    print(redis_store.get("name"))
    #
    # session['name']='hhh'
    # print(session.get('name'))
    return "helloworld"