from flask import Flask, request, redirect, url_for, session, render_template
from flask import Blueprint, jsonify
from extend import db
from models import User, UserContent, Content
from flask_cors import cross_origin
bp = Blueprint('user_management', __name__)

@bp.route('/userManagement/um_page', methods=['POST', 'GET'])
def user_management_page():
    return render_template('userManagement.html')

@bp.route('/userManagement/login', methods=['POST', 'GET'])
def user_management_login():
    return render_template('login.html')
#初始化用户管理页面时，获取所有用户数据
@bp.route('/userManagement/init_data', methods=['POST', 'GET'])
def user_management():
    users=User.query.all()
    json_user = []
    index = 1
    for user in users:
        json_user.append({'id': user.id, 'username': user.username, 'password': user.password})
        index+=1
        session['init_data'] = json_user
    return jsonify(json_user)


#添加用户
@bp.route('/userManagement/add_user', methods=['POST', 'GET',"OPTIONS"])
def add_user():
    if request.method == "OPTIONS":
        return jsonify({'ok': 'ok'})
    print(1)
    if request.is_json:
        print(28)
    else:
        print(29)
    data = request.get_json()
    username = data['username']
    password = data['password']
    print(2)
    print(username)
    print(password)
    try:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'ok': 'ok'})
    except Exception as e:
        print(e)  # 打印异常信息
        db.session.rollback()  # 把会话回滚到插入之前
        return jsonify({'status': 'error', 'message': str(e)})

#删除用户
@bp.route('/userManagement/delete_user', methods=['POST', 'GET',"OPTIONS"])
def delete_user():
    if request.method == "OPTIONS":
        return jsonify({'ok': 'ok'})
    data = request.get_json()
    user_id = data['id']
    print(user_id)
    user_content = UserContent.query.filter_by(user_id=user_id).all()
    for content in user_content:
        cot=Content.query.filter_by(id=content.content_id).first()
        db.session.delete(content)
        db.session.delete(cot)
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'ok': 'ok'})

#更新用户
@bp.route('/userManagement/update_user', methods=['POST', 'GET',"OPTIONS"])
def update_user():
    if request.method == "OPTIONS":
        return jsonify({'ok': 'ok'})
    data = request.get_json()
    user_id = data['id']
    username = data['username']
    password = data['password']
    user = User.query.filter_by(id=user_id).first()
    user.username = username
    user.password = password
    db.session.commit()
    return jsonify({'ok': 'ok'})
