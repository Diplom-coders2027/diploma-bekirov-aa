from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Этап 0: Проверка веток работает! Скоро здесь будет тиндер для дотеров"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)