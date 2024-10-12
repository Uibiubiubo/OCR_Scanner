from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from bluePrint.upload_img import bp as upload_img_bp
from bluePrint.register import bp as register_bp
from bluePrint.login import bp as login_bp
from bluePrint.find import bp as find_bp
from bluePrint.userManagement import bp as um_bp

from extend import db


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
#挂载用户管理蓝图
app.register_blueprint(um_bp)
#挂载注册蓝图
app.register_blueprint(register_bp)
#挂载登录蓝图
app.register_blueprint(login_bp)
#挂载图片处理蓝图
app.register_blueprint(upload_img_bp)
#挂载搜索蓝图
app.register_blueprint(find_bp)

if __name__ == '__main__':
    app.run()