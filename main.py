from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///worksearch.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String)
    role = db.Column(db.String)

    def __repr__(self):
        return "<User %r>" % self.id


@app.route("/")
def welcome_page():
    return render_template("welcome_page.html")


@app.route("/registration", methods=["POST"])
def registration_post():
    if request.form['password'] == request.form['passwordSec']:
        user = User(password=request.form["password"], name=request.form["name"],
                    email=request.form["email"], role=request.form['radios'])
        print(user.role)
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


if __name__ == "__main__":
    app.run(debug=True)
