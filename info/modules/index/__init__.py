from flask import Blueprint
#创建蓝图对象
index_blue=Blueprint('index',__name__)

from . import view
