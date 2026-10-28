
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Это поле будет хранить длинную строку $argon2id$...
    password_hash = db.Column(db.String(255), nullable=False) 
    
    # Игровые данные (оставляем как было)
    mmr = db.Column(db.Integer, default=0)
    roles = db.Column(db.String(120))
    has_mic = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    timezone = db.Column(db.String(50))
    playtime = db.Column(db.String(100))
    telegram = db.Column(db.String(255))
    discord = db.Column(db.String(255))

    def __repr__(self):
        return f"<User {self.nickname}>"