#配置数据库连接信息
USER = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'test'
uri ='mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USER, PASSWORD, HOST, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = uri

#配置session信息
SECRET_KEY = 'fhielghri'