from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workSearch.db"
db = SQLAlchemy(app)


# class User(db.Model):
#     pass


@app.route("/")
def welcome_page():
    return render_template("welcome_page.html")


@app.route("/registration")
def registration():
    return render_template("registration.html")


if __name__ == "__main__":
    app.run(debug=True)
