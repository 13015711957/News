from flask import current_app, render_template, jsonify, abort, session, g, request

from . import news_blue
from ...models import *
from ...utils.commons import user_login_data
from ...utils.response_code import RET


@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """
    请求路径: /news/comment_like
    请求方式: POST
    请求参数:news_id,comment_id,action,g.user
    返回值: errno,errmsg
    """
    # 1. 判断用户是否有登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2. 获取参数
    action = request.json.get('action')
    comment_id = request.json.get('comment_id')

    # 3. 参数校验,为空校验
    if not all([action, comment_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4. 操作类型进行校验
    if not action in ['add', 'remove']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型有误')

    # 5. 通过评论编号查询评论对象,并判断是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻评论失败')

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论不存在')

    # 6. 根据操作类型点赞取消点赞
    try:
        if action == 'add':
            # 判断是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment.id).first()
            if not comment_like:
                comment_like = CommentLike()
                comment_like.user_id = g.user.id
                comment_like.comment_id = comment_id

                db.session.add(comment_like)
                comment.like_count += 1
                db.session.commit()
        else:
            # 判断是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment.id).first()
            if comment_like:
                db.session.delete(comment_like)
                if comment.like_count > 0:
                    comment.like_count -= 1
                db.session.commit()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='操作失败')

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')

@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """
    请求路径: /news/news_comment
    请求方式: POST
    请求参数:news_id,comment,parent_id, g.user
    返回值: errno,errmsg,评论字典
    """
    # 1. 判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2. 获取请求参数
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3. 校验参数,为空校验
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4. 根据新闻编号取出新闻对象,判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻获取失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 5. 创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id

    # 6. 保存评论对象到数据库中
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论失败')

    # 7. 返回响应,携带评论的数据
    return jsonify(errno=RET.OK, errmsg='评论成功', data=comment.to_dict())


@news_blue.route('/news_collect', methods=['POST'])
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
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2. 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3. 参数校验,为空校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 4. 操作类型校验
    if not action in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.DATAERR, errmsg='操作类型有误')

    # 5. 根据新闻的编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻获取失败')

    # 6. 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 7. 根据操作类型,进行收藏&取消收藏操作
    if action == 'collect':
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
    # 1.根据新闻编号，查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    if not news:
        abort(404)

    # 2.获取前6热门新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 3.将热门新闻转成字典
    click_news_list = []
    for i in click_news:
        click_news_list.append(i.to_dict())

    # 4.判断用户是否收藏过该新闻
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 5.查询数据库评论
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取评论失败')

    # 6.点赞
    try:
        commentlikes = []
        if g.user:
            commentlikes = CommentLike.query.filter(CommentLike.user_id == g.user.id).all()
        mylike_comment_ids = []
        for i in commentlikes:
            mylike_comment_ids.append(i.comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取点赞失败')

    # 6.评论对象转列表
    comments_list = []
    for comment in comments:
        comm_dict = comment.to_dict()
        comm_dict['is_like'] = False
        if g.user and comment.id in mylike_comment_ids:
            comm_dict['is_like'] = True
        comments_list.append(comm_dict)

    # 4.携带数据，渲染页面
    data = {
        'news_info': news.to_dict(),
        'user_info': g.user.to_dict() if g.user else '',
        'news': click_news_list,
        'is_collected': is_collected,
        'comments': comments_list

    }
    return render_template('news/detail.html', data=data)
