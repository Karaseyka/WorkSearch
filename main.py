from io import BytesIO

import flask_login
from flask import Flask, render_template, request, redirect, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BLOB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required

app = Flask(__name__)
app.secret_key = 'some key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///worksearch.db"
db = SQLAlchemy(app)
manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String)
    resume = db.Column(BLOB, default=None)
    resumetxt = db.Column(db.String)

    def __repr__(self):
        return "<User %r>" % self.id


@manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route("/")
def welcome_page():
    return render_template("welcome_page.html")


@app.route("/registration", methods=["POST"])
def registration_post():
    if request.form['password'] == request.form['passwordSec']:
        pw = generate_password_hash(request.form["password"])
        user = User(password=str(pw), name=request.form["name"],
                    email=request.form["email"], role=request.form['radios'])
        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            return "Технические шоколадки"

    else:
        return render_template("registration.html")


@app.route("/registration", methods=["GET"])
def registration_get():
    return render_template("registration.html")


@app.route("/enter", methods=["POST"])
def enter_post():
    login = request.form.get("email")
    pw = request.form.get("password")
    if login and pw:
        user = User.query.filter_by(email=login).first()
        if check_password_hash(user.password, pw):
            login_user(user)
            return render_template("welcome_page.html")
        else:
            return render_template("enter.html")

    else:
        return render_template("enter.html")


@app.route("/enter", methods=["GET"])
def enter_get():
    return render_template("enter.html")


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    if request.method == 'POST':
        file = request.files["file"]
        txt = request.form["filetxt"]
        if file:
            if file.filename[-4::] == ".pdf":
                try:
                    file_bite = file.read()
                    flask_login.current_user.resumetxt = None
                    flask_login.current_user.resume = file_bite
                    db.session.commit()
                    return "Успешно"
                except:
                    return "Неудалось добавить файл"
            else:
                return "Нужен .pdf формат"
        elif txt:
            flask_login.current_user.resume = None
            flask_login.current_user.resumetxt = txt
            db.session.commit()
            return "Успешно"
    else:
        if flask_login.current_user.role == "option1":
            return render_template("profile_child.html", current_user=flask_login.current_user)
        elif flask_login.current_user.role == "option2":
            return render_template("profile_parent.html", current_user=flask_login.current_user)
        elif flask_login.current_user.role == "option3":
            return render_template("profile_hh.html", current_user=flask_login.current_user)
        else:
            return "Технические шоколадки"


@app.route("/resume", methods=["GET"])
@login_required
def resume():
    img = flask_login.current_user.resume
    txt = flask_login.current_user.resumetxt
    if img:
        return send_file(BytesIO(img),
                         download_name="resume.pdf", as_attachment=True)
    elif txt:
        return txt
    else:
        return "Резюме не найдено"


if __name__ == "__main__":
    app.run(debug=True)
