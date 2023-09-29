from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
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


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


def redirect_to_enter(url):
    if flask_login.current_user.is_authenticated:
        return render_template("enter.html")
    else:
        return render_template(url)


if __name__ == "__main__":
    app.run(debug=True)
