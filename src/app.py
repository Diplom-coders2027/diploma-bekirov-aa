
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from models import db, User
from dotenv import load_dotenv 
load_dotenv() 
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

# Секретный ключ нужен для шифрования сессионных куки (чтобы хакер не подделал твой вход)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_key')

# Настройка БД (оставляем с возможностью переключения на Postgres через .env)
basedir = os.path.abspath(os.path.dirname(__file__))
default_db = 'sqlite:///' + os.path.join(basedir, 'dota_tinder.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- ИНИЦИАЛИЗАЦИЯ БЕЗОПАСНОСТИ ---
ph = PasswordHasher() # Это наш Аргон

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Если кто-то без входа зайдет на закрытую страницу, его кинет сюда

@login_manager.user_loader
def load_user(user_id):
    # Эта функция говорит Flask-Login, как достать юзера из БД по его ID
    return User.query.get(int(user_id))

# --- МАРШРУТЫ ---

@app.route("/")
def index():
    if current_user.is_authenticated:
        return f"<h1>Привет, {current_user.nickname}! Ты в системе. <a href='/logout'>Выйти</a></h1>"
    return "<h1>Главная страница. Ты не авторизован. <a href='/login'>Войти</a> или <a href='/register'>Регистрация</a></h1>"

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        # --- 1. ПРОВЕРКА ФОРМАТА EMAIL (вот тот блок) ---
        try:
            validate_email(email) 
        except EmailNotValidError as e:
            flash(f'Некорректный email: {str(e)}', 'error')
            return redirect(url_for('register'))

        # --- 2. ПРОВЕРКА НА ЗАНЯТОСТЬ EMAIL ---
        if User.query.filter_by(email=email).first():
            flash('Этот email уже занят!', 'error')
            return redirect(url_for('register'))
            
        # --- 3. ПРОВЕРКА НА ЗАНЯТОСТЬ НИКНЕЙМА ---
        if User.query.filter_by(nickname=nickname).first():
            flash('Этот никнейм уже занят другим дотером!', 'error')
            return redirect(url_for('register'))

        # --- 4. ХЭШИРОВАНИЕ ПАРОЛЯ ---
        hashed_password = ph.hash(password)

        # --- 5. СОХРАНЕНИЕ В БАЗУ ---
        new_user = User(
            email=email, 
            nickname=nickname, 
            password_hash=hashed_password
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Успешная регистрация! Войдите в систему.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании: {e}', 'error')

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        # ПРОВЕРКА ПАРОЛЯ
        if user:
            try:
                # ph.verify берет хэш из БД и введенный пароль, и проверяет их
                ph.verify(user.password_hash, password)
                
                # Если ошибки нет, значит пароль верный
                login_user(user) 
                return redirect(url_for('index'))
                
            except VerifyMismatchError:
                # Эта ошибка ловится, если пароль не совпал
                flash('Неверный пароль', 'error')
            except Exception as e:
                flash(f'Ошибка проверки: {e}', 'error')
        else:
            flash('Пользователь с таким email не найден', 'error')
            
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)