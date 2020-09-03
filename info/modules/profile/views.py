from . import profile_blue
from flask import render_template, jsonify, redirect, g, request, current_app

from ... import constants
from ...utils.commons import user_login_data
from ...utils.image_storage import image_storage
from ...utils.response_code import RET


@profile_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """
    请求路径: /profile/pass_info
    请求方式:GET,POST
    请求参数:GET无, POST有参数,old_password, new_password
    返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
    """
    # 1. 判断请求方式,如果是get请求
    if request.method == 'GET':
        # 2. 直接渲染页面
        return render_template('news/user_pass_info.html')

    # 3. 如果是post请求,获取参数
    old_password=request.json.get('old_password')
    new_password=request.json.get('new_password')

    # 4. 校验参数,为空校验
    if not all([old_password, old_password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 5. 判断老密码是否正确
    if not g.user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg='老密码错误')

    # 6. 设置新密码
    g.user.password=new_password

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')

@profile_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """
    请求路径: /profile/pic_info
    请求方式:GET,POST
    请求参数:无, POST有参数,avatar
    返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
    """
    # 1. 判断请求方式,如果是get请求
    if request.method == 'GET':
        # 2. 携带用户数据,渲染页面
        return render_template('news/user_pic_info.html', user_info=g.user.to_dict())

    # 3. 如果是post请求
    # 4. 获取参数
    avatar=request.files.get('avatar')

    # 5. 校验参数,为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='图片不能为空')

    # 6. 上传图像,判断图片是否上传成功
    try:
        image_name=image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 7. 将图片设置到用户对象
    g.user.avatar_url=image_name

    # 8. 返回响应
    data={
        'avatar_url':constants.QINIU_DOMIN_PREFIX+image_name
    }
    return jsonify(errno=RET.OK, errmsg='上传成功',data=data)


@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """
    请求路径: /profile/base_info
    请求方式:GET,POST
    请求参数:POST请求有参数,nick_name,,gender
    返回值:errno,errmsg
    """
    # 1. 判断请求方式,如果是get请求
    if request.method == 'GET':
        # 2. 携带用户数据,渲染页面
        return render_template('news/user_base_info.html', user_info=g.user.to_dict())

    # 3. 如果是post请求
    # 4. 获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    # 5. 校验参数,为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    if not gender in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.DATAERR, errmsg='性别异常')

    # 6. 修改用户的数据
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')


@profile_blue.route('/info')
@user_login_data
def user_index():
    """
    请求路径: /profile/info
    请求方式:GET
    请求参数:无
    返回值: user.html页面,用户字典data数据
    """
    # 1. 判断用户是否有登陆
    if not g.user:
        return redirect('/')

    # 2.携带数据渲染页面
    data = {
        'user_info': g.user.to_dict()
    }
    return render_template("news/user.html", data=data)
