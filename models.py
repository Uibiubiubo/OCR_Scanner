from extend import db
#用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
#内容模型
class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    birth = db.Column(db.String(20), nullable=False)
    id_card_number = db.Column(db.String(20), nullable=False)
    nation = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    image =db.Column(db.LargeBinary, nullable=False)
#用户内容关联模型
class UserContent(db.Model):
    __tablename__ = 'user_content'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)

    user = db.relationship('User', backref=db.backref('user_contents', lazy=True))
    content = db.relationship('Content', backref=db.backref('user_contents', lazy=True))

