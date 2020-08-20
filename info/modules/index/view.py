from . import index_blue
from info import redis_store
from flask import render_template,current_app

@index_blue.route('/',methods=['GET','POST'])
def index():

    return render_template('news/index.html')

#处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')