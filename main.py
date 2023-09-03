from flask import Flask

app = Flask(__name__)


@app.route("/")
def welcome_page():
    return "Доборо пожаловать на сайт для поиска работы подросткам"


if __name__ == "__main__":
    app.run(debug=True)
