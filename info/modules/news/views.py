from flask import current_app, render_template, jsonify, abort, session, g, request

from . import news_blue
from ...models import News, User
from ...utils.commons import user_login_data
from ...utils.response_code import RET

@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    """
    请求路径: /news/news_collect
    请求方式: POST
    请求参数:news_id,action, g.user
    返回值: errno,errmsg
    """
    # 1. 判断用户是否登陆了
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg='用户未登录')

    # 2. 获取参数
    news_id=request.json.get('news_id')
    action=request.json.get('action')

    # 3. 参数校验,为空校验
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4. 操作类型校验
    if not action in ['collect','cancel_collect']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型有误')

    # 5. 根据新闻的编号取出新闻对象
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻获取失败')

    # 6. 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 7. 根据操作类型,进行收藏&取消收藏操作
    if action=='collect':
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        if news in g.user.collection_news:
            g.user.collection_news.remove(news)

    # 8. 返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')




@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    请求路径: /news/<int:news_id>
    请求方式: GET
    请求参数:news_id
    返回值: detail.html页面, 用户data字典数据
    """
    #1.根据新闻编号，查询新闻对象
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取新闻失败')

    if not news:
        abort(404)

    #2.获取前6热门新闻
    try:
        click_news=News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    #3.将热门新闻转成字典
    click_news_list=[]
    for i in click_news:
        click_news_list.append(i.to_dict())

    #4.判断用户是否收藏过该新闻
    is_collected=False
    if g.user:
        if news in g.user.collection_news:
            is_collected=True

    #4.携带数据，渲染页面
    data={
        'news_info':news.to_dict(),
        'user_info':g.user.to_dict() if g.user else '',
        'news':click_news_list,
        'is_collected':is_collected

    }
    return render_template('news/detail.html', data=data)