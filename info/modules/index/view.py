from . import index_blue
from info import redis_store
from flask import render_template

@index_blue.route('/',methods=['GET','POST'])
def index():

    return render_template()