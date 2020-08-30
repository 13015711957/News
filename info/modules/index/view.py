from sqlalchemy import text

from . import index_blue
from info import redis_store
from flask import render_template, current_app, session, jsonify, request, g

from ...models import *
from ...utils.commons import user_login_data
from ...utils.response_code import RET


@index_blue.route('/newslist')
def newslist():
    """
    请求路径: /newslist
    请求方式: GET
    请求参数: cid,page,per_page
    返回值: data数据
    """
    # 1. 获取参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    # 2. 参数类型转换
    try:
        page=int(page)
        per_page=int(per_page)
    except Exception as e:
        page=1
        per_page=10
        
    # 3. 分页查询
    try:
        filters=[]
        if cid!='1':
            filters.append(News.category_id==cid)
        paginate=News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4. 获取到分页对象中的属性,总页数,当前页,当前页的对象列表
    totalPage=paginate.pages
    currentPage=paginate.page
    items=paginate.items

    # 5. 将对象列表转成字典列表
    newslist=[]
    for i in items:
        newslist.append(i.to_dict())

    # 6. 携带数据,返回响应
    return jsonify(errno=RET.OK, errmsg='获取新闻成功',totalPage=totalPage,currentPage=currentPage,newsList=newslist)



@index_blue.route('/', methods=['GET', 'POST'])
@user_login_data
def index():
    # # 1.获取用户登录信息
    # user_id = session.get('user_id')
    #
    # # 2.通过user_id取出用户对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 3.查询热门新闻，查询点击量前十的新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4.将新闻列表转成字典
    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 5.查询所有分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

    # 6.将分类列表转成字典
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 3.拼接用户数据，渲染页面
    data = {
        'user_info': g.user.to_dict() if g.user else "",
        'news': news_list,
        'category_list': category_list
    }

    return render_template('news/index.html', data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')
