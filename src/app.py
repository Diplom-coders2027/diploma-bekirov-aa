import os
from flask import Flask
# Импортируем нашу базу и модель из файла models.py
from models import db, User

app = Flask(__name__)

# Настраиваем, где будет лежать файл базы данных (в папке src)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dota_tinder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Привязываем базу к приложению
db.init_app(app)

@app.route("/")
def index():
    return "<h1>Привет, дотер! Сайт работает.</h1>"

# --- ТЕСТОВЫЙ МАРШРУТ ДЛЯ ПРОВЕРКИ БАЗЫ ---
@app.route("/test-db")
def test_db():
    with app.app_context():
        # Создаем таблицы в базе данных (если их еще нет)
        db.create_all()
        
        # Проверяем, есть ли уже тестовый юзер
        user = User.query.filter_by(nickname="TestDoter").first()
        
        if not user:
            # Если нет, создаем нового
            new_user = User(
                nickname="TestDoter", 
                email="test@dota.ru", 
                mmr=5000, 
                roles="Carry",
                has_mic=True,
                age=22,
                timezone="UTC+3",
                playtime="Evening",
                telegram="@test_doter",
                discord="test#1234"
            )
            db.session.add(new_user) # Добавляем в базу
            db.session.commit()      # Сохраняем
            return "<h1>Тестовый пользователь создан и добавлен в БД!</h1>"
        
        # Если юзер уже есть, показываем его данные
        return f"<h1>Пользователь найден: {user.nickname}, MMR: {user.mmr}, Телега: {user.telegram}</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=8080)