from flask_sqlalchemy import SQLAlchemy

# Создаем объект базы данных
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users' # Название таблицы в БД

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False) # Ник в доте
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Игровые данные
    mmr = db.Column(db.Integer, default=0)
    roles = db.Column(db.String(120)) # Например: "Carry, Mid" (пока строкой)
    has_mic = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    
    # Удобства
    timezone = db.Column(db.String(50)) # Например: "UTC+3"
    playtime = db.Column(db.String(100)) # Например: "Вечером"
    
    # Контакты для связи
    telegram = db.Column(db.String(100))
    discord = db.Column(db.String(100))

    def __repr__(self):
        # Это нужно для удобного вывода в консоль
        return f"<User {self.nickname}, MMR: {self.mmr}>"