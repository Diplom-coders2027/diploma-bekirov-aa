import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from models import db, User

# 1. Загружаем секреты из .env файла
load_dotenv()

app = Flask(__name__)
# Берем SECRET_KEY из .env. Если его нет, используем заглушку (для локальной разработки)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-fallback-key')

# 2. Настройка базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
default_db = 'sqlite:///' + os.path.join(basedir, 'dota_tinder.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 3. Инициализация Argon2 (настройки по умолчанию безопасны и современны)
ph = PasswordHasher()

# 4. Настройка Flask-Login (управление сессиями)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Если не залогинен, перекинет сюда

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return f"<h1>Привет, {current_user.nickname}! Ты в системе.</h1><a href='/logout'>Выйти</a>"
    return "<h1>Главная страница.</h1><a href='/login'>Войти</a> | <a href='/register'>Регистрация</a>"

# --- РЕГИСТРАЦИЯ ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        # Проверяем, не занят ли email
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'error')
            return redirect(url_for('register'))

        # ХЭШИРОВАНИЕ АРГОНОМ (вот тут создается безопасный хэш)
        hashed_password = ph.hash(password)

        new_user = User(email=email, nickname=nickname, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Успешная регистрация! Теперь войдите.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании: {e}', 'error')

    return render_template("register.html")

# --- ВХОД ---
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                # ПРОВЕРКА АРГОНА: сверяем введенный пароль с хэшем из БД
                ph.verify(user.password_hash, password)
                
                # Если код дошел сюда, пароль верный
                login_user(user)
                return redirect(url_for('index'))
            except VerifyMismatchError:
                flash('Неверный пароль', 'error')
            except Exception as e:
                flash(f'Ошибка проверки: {e}', 'error')
        else:
            flash('Пользователь с таким email не найден', 'error')
            
    return render_template("login.html")

# --- ВЫХОД ---
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Создаем таблицы в БД, если их еще нет
    with app.app_context():
        db.create_all()
    # Запускаем на 0.0.0.0 и порту 8080, как просил препод
    app.run(host='0.0.0.0', port=8080, debug=True)