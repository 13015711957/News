from flask import current_app, render_template, jsonify, abort, session

from . import news_blue
from ...models import News, User
from ...utils.response_code import RET


@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    """
    请求路径: /news/<int:news_id>
    请求方式: GET
    请求参数:news_id
    返回值: detail.html页面, 用户data字典数据
    """
    #1.获取用户数据
    user_id=session.get('user_id')
    user=None
    if user_id:
        try:
            user=User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
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

    #4.携带数据，渲染页面
    data={
        'news_info':news.to_dict(),
        'user_info':user.to_dict() if user else '',
        'news':click_news_list

    }
    return render_template('news/detail.html', data=data)