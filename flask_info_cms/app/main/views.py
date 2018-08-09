# Author: Jason Lu

from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import copy_current_request_context

from app import app, col_users, csrf
#from manage import app, mongo
from app.main.forms_login import LoginForm
from controller.user import UserController
from controller.ipmanager import ManagerProxyIP as MGIH

# 引入模型
# from models.user import User
# from models.device import Device1


@app.route('/')
@app.route('/index')
def index():

    return render_template(
        'index.html',
        title = 'Home',
        info = session['info']
    )

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    # 接受表单数据
    if form.validate_on_submit():
        if form.username.data is not None:
            session['info'] = {
                'username':form.username.data,
                'password':form.password.data,
                'rememberme':form.remember_me.data
            }

            # 清空数据
            form.username.data = ''
            form.password.data = ''
            form.remember_me.data = False

            return redirect(url_for('index'))

    return render_template(
        'login.html',
        form = form,
        info = session.get('info')
    )

@app.route('/logout')
def logout():
    # logout_user()
    return redirect(url_for('login'))

################################################################
# 爬虫相关页面
@app.route('/spider_manager')
def spider_manager():
    json_users = UserController().get_users(0)
    return render_template('spider_manager.html', title='爬虫管理',
                           users=json_users['users'])

@csrf.exempt # 移除csrf验证
@app.route('/spider_ip_manager', methods=['GET', 'POST'])
def spider_ip_manager():

    if request.method == 'POST':
        if 'btn_download' in request.form:
            print(request.form)
            start_page = request.form['start_page']
            end_page = request.form['end_page']
            MGIH.config(debug=True)
            MGIH.init_grab_ip_html(start_page, end_page)
            # 方法一：使用线程子类下载网页
            #MGIH.start_grab_ip_html()

            # 方法二：使用底层_thread线程下载网页
            MGIH.start_parse_ip_use_thread()
        elif 'btn_show_list' in request.form:
            print("show list...")

    print(">>:返回模版页面...")
    return render_template('spider_ip_manager.html',
                           title='IP地址管理',
                           download_precent = MGIH.download_precent,
                           show_download_info = MGIH.show_precent)

@app.route('/download_task', methods=['GET', 'POST'])
def download_task():
    print("page from:")


################################################################
# 数据相关页面
@app.route('/data_manager')
def data_manager():
    return render_template('data_manager.html', title='数据管理')



################################################################
############################接口相关####################################
@csrf.exempt
@app.route('/todo/api/v1.0/tasks', methods=['GET', 'POST'])
def get_tasks():
    return jsonify({
        'task':'test'
    })

from flask import abort
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, 'test')
    try:
        info = task.__next__()
    except StopIteration as e:
        abort(404)

    return jsonify({'task': info})

from flask import make_response
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


"""
MongoDB数据库操作, api接口地址
"""

# 添加数据
@app.route('/todo/api/v1/add', methods=['GET', 'POST'])
def add():
    user = col_users#mongo.db.users
    if not 'username' in request.form or\
            not 'password' in request.form:
        print(request)
        abort(404)

    # user = mongo.db.users
    username = request.form['username']
    password = request.form['password']
    user.insert({'username':username,'password':password})

    return jsonify({'code':1, 'msg':'success'})


# 查找数据
@app.route('/todo/api/v1/find', methods=['POST'])
def find():
    p_filter = int(request.form['filter'])
    p_username = request.form['username']

    ret = UserController().get_users(p_filter, p_username)

    code = int(ret['code'])
    if code == 404:
        return abort(404)

    return jsonify(ret)


# 修改数据
@app.route('/todo/api/v1/update', methods=['GET', 'POST'])
def update():
    print("request>>:%s"%request.form['username'])
    if not 'username' in request.form or\
            not 'password' in request.form:
        print(request)
        abort(404)

    user = col_users#mongo.db.users
    username = request.form['username']
    someone = user.find_one({
        'username': username
    })

    if someone is None:
        return abort(404)

    someone['password'] = request.form['password']
    user.save(someone)

    return jsonify({'code':1, 'msg':'success'})


# 删除数据
@app.route('/todo/api/v1/del/<string:username>', methods=['GET'])
def delete(username):
    user = col_users#mongo.db.users
    someone = user.find_one({'username':username})

    if someone is not None:
        user.remove(someone)
        return jsonify({'code':1, 'msg':'success'})

    return abort(404)


