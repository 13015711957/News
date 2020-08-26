from . import index_blue
from info import redis_store
from flask import render_template, current_app, session, jsonify

from ...models import *
from ...utils.response_code import RET


@index_blue.route('/', methods=['GET', 'POST'])
def index():
    # 1.获取用户登录信息
    user_id = session.get('user_id')

    # 2.通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 3.查询热门新闻，查询点击量前十的新闻
    try:
        news=News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取新闻失败')

    # 4.将新闻列表转成字典
    news_list=[]
    for item in news:
        news_list.append(item.to_dict())

    # 5.查询所有分类数据
    try:
        categories=Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

    # 6.将分类列表转成字典
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 3.拼接用户数据，渲染页面
    data = {
        'user_info': user.to_dict() if user else "",
        'news': news_list,
        'category_list':category_list
    }

    return render_template('news/index.html', data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')
