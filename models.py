from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

    user = db.relationship('User', backref=db.backref('feedbacks', lazy=True))

    def __init__(self, title, content, username):
        self.title = title
        self.content = content
        self.username = username