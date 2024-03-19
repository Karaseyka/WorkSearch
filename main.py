from io import BytesIO
from data.api import user_api
import flask_login
from flask import Flask, render_template, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required
from flask import request
from data.database import db_session
from data.models.user import User

app = Flask(__name__)
app.secret_key = 'some key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///worksearch.db"

db_session.global_init("instance/worksearch.db")

manager = LoginManager(app)
manager.init_app(app)
db_ses = db_session.create_session()


@manager.user_loader
def load_user(user_id):
    return db_ses.query(User).get(user_id)


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
            db_ses.add(user)
            db_ses.commit()
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
        user = db_ses.query(User).filter_by(email=login).first()
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
    print(1, request.method)
    # Проверяем пост запрос либо гет
    if request.method == 'POST':
        # Проверяем чей аккаунт (родителя, чайлда, хэдхантера)
        if flask_login.current_user.role == "option1":
            # Действия с изменением данных аккаунта
            file = request.files["file"]
            txt = request.form["filetxt"]
            name = request.form["staticName"]
            email = request.form["staticEmail"]
            if file:
                if file.filename[-4::] == ".pdf":
                    try:
                        file_bite = file.read()
                        flask_login.current_user.name = name
                        flask_login.current_user.email = email
                        flask_login.current_user.resumetxt = None
                        flask_login.current_user.resume = file_bite
                        db_ses.commit()
                        return "Успешно"
                    except:
                        return "Неудалось добавить файл"
                else:
                    return "Нужен .pdf формат"
            elif len(txt) == 0:
                flask_login.current_user.name = name
                flask_login.current_user.email = email
                db_ses.commit()
                return "Успешно"
            elif txt:
                flask_login.current_user.resume = None
                flask_login.current_user.resumetxt = txt
                db_ses.commit()
                return "Успешно"
        if flask_login.current_user.role == "option2":
            name = request.form["staticName"]
            email = request.form["staticEmail"]
            child = request.form["child"]
            flask_login.current_user.name = name
            flask_login.current_user.email = email
            flask_login.current_user.child = child
            db_ses.commit()
            return "Успешно"

        if flask_login.current_user.role == "option3":
            name = request.form["name"]
            email = request.form["email"]
            us_contacts = flask_login.current_user.contacts
            if us_contacts is not None:
                super_cont = us_contacts.split(', ')
            else:
                super_cont = []
            return render_template("profile_hh.html", current_user=flask_login.current_user, contacts=super_cont)


    else:
        if flask_login.current_user.role == "option1":
            return render_template("profile_child.html", current_user=flask_login.current_user)
        elif flask_login.current_user.role == "option2":
            return render_template("profile_parent.html", current_user=flask_login.current_user)
        elif flask_login.current_user.role == "option3":
            print(1)
            us_contacts = flask_login.current_user.contacts
            if us_contacts is not None:
                super_cont = us_contacts.split(', ')
            else:
                super_cont = []
            return render_template("profile_hh.html", current_user=flask_login.current_user, contacts=super_cont[1:])
        else:
            return "Технические шоколадки"


@app.route("/del_contact", methods=["GET", "POST"])
@login_required
def delete_contact():
    print(165, request.method)
    if request.method == "POST":
        delete = request.form["delete"]
        print(delete)
        us_contacts = flask_login.current_user.contacts
        if us_contacts is not None:
            super_cont = us_contacts.split(', ')
        else:
            super_cont = []
        print(super_cont)
        flask_login.current_user.contacts = flask_login.current_user.contacts.replace(f', {delete}', '')
        db_ses.commit()
        # return render_template("profile_hh.html", current_user=flask_login.current_user, contacts=super_cont)
        return redirect('/profile')


@app.route('/add_cont', methods=["POST"])
@login_required
def add_contact():
    print(666)
    net = request.form['net']
    cont = request.form['way']
    print(net, cont)
    if net != '' and cont != '':
        if flask_login.current_user.contacts is None:
            contacts = f', {net}-{cont}'
        else:
            contacts = flask_login.current_user.contacts + f', {net}-{cont}'
        flask_login.current_user.contacts = contacts
        db_ses.commit()
    return redirect('/profile')


@app.route('/update_data', methods=["POST"])
@login_required
def update_data():
    print("vhbjnkml,;")
    name = request.form["name"]
    email = request.form["email"]
    flask_login.current_user.name = name
    flask_login.current_user.email = email
    db_ses.commit()
    return redirect('/profile')


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


@app.route("/vacancies", methods=["GET"])
@login_required
def vacancies():
    return render_template("vacancies.html")


@app.route("/addvacancy", methods=["GET"])
@login_required
def add_vacancies():
    return render_template("add_vacancy.html")


@app.errorhandler(401)
def unauthorized_request(_):
    return "Для работы с сайтом необходима авторизация"


if __name__ == "__main__":
    app.register_blueprint(user_api.blueprint)
    app.run(debug=True)
