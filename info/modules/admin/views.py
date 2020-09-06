from flask import render_template, request, current_app, session, redirect, g, jsonify
import time
from datetime import datetime,timedelta

from info import constants, db
from info.models import User, News, Category
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import admin_blue

@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """
    请求路径: /admin/news_edit_detail
    请求方式: GET, POST
    请求参数: GET, news_id, POST(news_id,title,digest,content,index_image,category_id)
    @return:
    """
    # 1.判断请求方式,如果是GET
    if request.method == "GET":
        # 2.获取新闻编号
        news_id = request.args.get("news_id")

        # 3.通过新闻编号查询新闻对象,并判断新闻对象是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="新闻获取失败")

        if not news:
            return render_template("admin/news_edit_detail.html", errmsg="该新闻不存在")

        # 3.1获取分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("", errmsg="分类获取失败")

        # 3.2将分类对象列表数据,转成字典数据
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        # 4.携带新闻数据和分类数据, 渲染页面
        return render_template("admin/news_edit_detail.html", news=news.to_dict(), category_list=category_list)

    # 5.如果是POST请求,获取参数(news_id,title,digest,content,index_image,category_id)
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    # 6.参数校验,为空校验
    if not all([news_id, title, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 7.根据新闻的编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 8.上传新闻图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="图片上传失败")

    # 9.设置新闻对象的属性
    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id

    # 10.返回响应
    return jsonify(errno=RET.OK, errmsg="编辑成功")
@admin_blue.route('/news_edit')
def news_edit():
    """
    请求路径: /admin/news_edit
    请求方式: GET
    请求参数: GET, p, keywords
    返回值:GET,渲染news_edit.html页面,data字典数据
    @return:
    """
    # 1. 获取参数,p,keywords
    page = request.args.get('p', '1')
    keywords = request.args.get('keywords', '')

    # 2. 参数类型转换
    try:
        page=int(page)
    except Exception as e:
        page=1

    # 3. 分页查询用户数据
    try:

        # 3.1判断是否有填写搜索关键
        filters = []
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_edit.html", errmsg="获取新闻失败")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template("admin/news_edit.html", data=data)

@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
    """
    请求路径: /admin/news_review_detail
    请求方式: GET,POST
    请求参数: GET, news_id, POST,news_id, action
    返回值:GET,渲染news_review_detail.html页面,data字典数据
    @return:
    """
    # 1.判断请求方式,如果是GET
    if request.method=='GET':
        # 2.获取新闻编号
        news_id=request.args.get('news_id')

        # 3.获取新闻对象,并判断新闻对象是否存在
        try:
            news=News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_review_detail.html',errmsg='该新闻获取失败')

        if not news:
            return render_template('admin/news_review_detail.html', errmsg='该新闻不存在')

        # 4.携带新闻对象的数据渲染页面
        return render_template('admin/news_review_detail.html', news=news.to_dict())

    # 5.如果是POST请求,获取参数
    action=request.json.get('action')
    news_id=request.json.get('news_id')

    # 6.校验操作类型
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    if not action in ['accept','reject']:
        return jsonify(errno=RET.DATAERR,errmsg='操作类型有误')
    
    # 7.根据编号,获取新闻对象,判断新闻对象是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    if not news:
        return jsonify(errno=RET.DBERR, errmsg='该新闻不存在')

    # 8.根据操作类型改变新闻的状态
    if action=='accept':
        news.status=0
    else:
        news.status=-1
        news.reason=request.json.get('reason','')

    # 9.返回响应
    return jsonify(errno=RET.OK, errmsg='操作成功')

@admin_blue.route('/news_review')
def news_review():
    """
    请求路径: /admin/news_review
    请求方式: GET
    请求参数: GET, p,keyword
    返回值:渲染user_list.html页面,data字典数据
    @return:
    """
    # 1. 获取参数,p,keywords
    page = request.args.get('p', '1')
    keywords=request.args.get('keywords','')

    # 2. 参数类型转换
    try:
        page=int(page)
    except Exception as e:
        page=1

    # 3. 分页查询用户数据
    try:
        filters=[News.status!=0]
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 3, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/news_review.html', errmsg='获取新闻失败')

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6. 拼接数据,渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list
    }
    return render_template('admin/news_review.html', data=data)

@admin_blue.route('/user_list')
def user_list():
    """
    请求路径: /admin/user_list
    请求方式: GET
    请求参数: p
    返回值:渲染user_list.html页面,data字典数据
    @return:
    """
    # 1. 获取参数,p
    page=request.args.get('p','1')

    # 2. 参数类型转换
    try:
        page=int(page)
    except Exception as e:
        page=1

    # 3. 分页查询用户数据
    try:
        paginate=User.query.filter(User.is_admin==False).order_by(User.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_list.html', errmsg='获取用户失败')

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage=paginate.pages
    currentPage=paginate.page
    items=paginate.items

    # 5. 将对象列表,转成字典列表
    user_list=[]
    for user in items:
        user_list.append(user.to_admin_dict())

    # 6. 拼接数据,渲染页面
    data={
        'totalPage':totalPage,
        'currentPage':currentPage,
        'user_list':user_list
    }
    return render_template('admin/user_list.html', data=data)


@admin_blue.route('/user_count')
def user_count():
    """
    请求路径: /admin/user_count
    请求方式: GET
    请求参数: 无
    返回值:渲染页面user_count.html,字典数据
    @return:
    """
    #1.获取用户总数
    try:
        total_count=User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html',errmsg='获取总人数失败')
    
    #2.获取月活人数
    localtime=time.localtime()
    try:
        #2.1先获取本月1号0点的字符串数据
        month_start_time_str="%s-%s-01"%(localtime.tm_year,localtime.tm_mon)

        #2.2根据字符串格式化日期对象
        month_start_time_date=datetime.strptime(month_start_time_str,"%Y-%m-%d")

        #2.3最后一次登录时间大于本月1号0点的人数
        month_count=User.query.filter(User.last_login>=month_start_time_date,User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html', errmsg='获取月活人数失败')

    #3.获取日活人数
    try:
        #2.1先获取本日的0点，字符串数据
        day_start_time_str="%s-%s-%s"%(localtime.tm_year,localtime.tm_mon,localtime.tm_mday)

        #2.2根据字符串格式化日期对象
        day_start_time_date = datetime.strptime(day_start_time_str, "%Y-%m-%d")

        # 2.3最后一次登录时间大于本月1号0点的人数
        day_count = User.query.filter(User.last_login >= day_start_time_date, User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_count.html', errmsg='获取日活人数失败')

    #4.获取活跃时间段内对应的活跃人数
    active_date=[]
    active_count=[]
    for i in range(0,31):
        begin_date=day_start_time_date-timedelta(days=i)
        end_date=day_start_time_date-timedelta(days=i-1)
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        everyday_active_count=User.query.filter(User.is_admin==False,User.last_login>=begin_date,User.last_login<=end_date).count()
        active_count.append(everyday_active_count)

    active_count.reverse()
    active_date.reverse()
    # 5.携带数据渲染页面
    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
    }
    return render_template("admin/user_count.html", data=data)

@admin_blue.route('/index')
@user_login_data
def admin_index():
    """
    请求路径: /admin/index
    请求方式: GET
    请求参数: 无
    返回值:渲染页面index.html,user字典数据
    @return:
    """
    data = {
        "user_info":g.user.to_dict() if g.user else ""
    }
    return render_template("admin/index.html",data=data)

@admin_blue.route('/login',methods=["GET","POST"])
def admin_login():
    """
    请求路径: /admin/login
    请求方式: GET,POST
    请求参数:GET,无, POST,username,password
    返回值: GET渲染login.html页面, POST,login.html页面,errmsg
    """
    # 1.判断请求方式,如果是GET,直接渲染页面
    if request.method=='GET':
        #判断管理员是否已经登录过，如果登录过滤直接跳转到首页
        if session.get('is_admin'):
            return redirect('/admin/index')
        return render_template('admin/login.html')

    # 2.如果是POST请求,获取参数
    username=request.form.get('username')
    password=request.form.get('password')

    # 3.校验参数,为空校验
    if not all([username, password]):
        return render_template('admin/login.html',errmsg='参数不全')

    # 4.根据用户名取出管理员对象,判断管理员是否存在
    try:
        admin=User.query.filter(User.mobile==username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html',errmsg='用户查询失败')

    if not admin:
        return render_template('admin/login.html', errmsg='管理员用户不存在')

    # 5.判断管理员的密码是否正确
    if not admin.check_password(password):
        return render_template('admin/login.html', errmsg='密码错误')

    # 6.管理的session信息记录
    session['user_id']=admin.id
    session['is_admin']=True

    # 7.重定向到首页展示
    return redirect('/admin/index')
