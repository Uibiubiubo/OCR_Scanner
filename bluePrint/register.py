from flask import Blueprint,  jsonify
from flask import request
from extend import db
from models import User

bp = Blueprint('register', __name__)

@bp.route('/register', methods=[ 'POST'])
def register():
    try:
        data=request.json
        u = data.get('username')
        p = data.get('password')
        if not u or not p:
            return jsonify({'error': 'Username and password are required!'}), 400
        user=User(username=u,password=p)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({'error': '该账号已存在'})
    return jsonify({"code":200,"msg":"注册成功"})
