from flask import Blueprint, request,  jsonify, current_app
from models import User

bp = Blueprint('login', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # 获取登录信息
        data = request.get_json()
        username = data['userId']
        password = data['password']
        # 验证登录信息是否为空
        if not username or not password:
            return jsonify({"id":5,"error":"请正确填写登录信息"})

        name_key = User.query.filter_by(username=username).first()
        pass_key = User.query.filter_by(password=password).first()

        # 验证登录信息是否正确
        if name_key and pass_key and name_key==pass_key:
            # 获取登录成功的用户id
            id_key = User.query.filter_by(id=name_key.id).first()
            current_app.config['USER_ID'] = id_key.id
            return jsonify({"id":1,"error":""}) # 登录check成功
        elif not name_key:
            return jsonify({"id":2,"error":"用户名不存在"})  # 用户名不存在

        else:
            return jsonify({"id":3,"error":"密码错误"})  # 密码错误

    except Exception as e:
        print(e)
        return jsonify({"id":4,"error":"未知错误"})  # 未知错误



