from . import index_blue

@index_blue.route('/')
def index():
    # redis_store.set("name","hbw")
    # print(redis_store.get("name"))
    #
    # session['name']='hhh'
    # print(session.get('name'))
    return "helloworld"