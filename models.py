from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer,   primary_key=True)
    email         = db.Column(db.String,    unique=True, nullable=False)
    password_hash = db.Column(db.String,    nullable=False)
    transactions  = db.relationship('Transaction', backref='user')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
