from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
 
login = LoginManager()
db = SQLAlchemy()
 
class UserModel(UserMixin, db.Model):#UserMixin, db.Model):
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    posts = db.relationship('Posts', backref='owner', lazy='dynamic') 
    profile = db.relationship('Profile', backref='owner', lazy='dynamic') 
    followers = db.relationship('Followers', backref='owner', lazy='dynamic') 
    following= db.relationship('Following', backref='owner', lazy='dynamic') 
    profile_image = db.relationship('Profile_image', backref='owner', lazy='dynamic')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(1000))
    date = db.Column(db.String(40))
    image = db.Column(db.LargeBinary)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    bio = db.Column(db.String(120))
    gender = db.Column(db.String(40))
    website = db.Column(db.String(40))
    image = db.Column(db.LargeBinary)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Profile_image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    file_name = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Followers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_user = db.Column(db.String(80))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    following_user = db.Column(db.String(80))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))