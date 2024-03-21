from io import BytesIO
from data.api import api
import flask_login
from flask import Flask, render_template, redirect, send_file, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import request
from data.database import db_session
from data.models.user import User
from data.models.vacancy import Vacancy

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


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('welcome_page'))


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
            login_user(user)
            return redirect("/")
        except:
            db_ses.rollback()
            return "Такой email уже существует"

    else:
        return "Пароли не совпадают"


@app.route("/registration", methods=["GET"])
def registration_get():
    return render_template("registration.html")


@app.route("/enter", methods=["POST"])
def enter_post():
    login = request.form.get("email")
    pw = request.form.get("password")
    if login and pw:
        user = db_ses.query(User).filter_by(email=login).first()
        if user and check_password_hash(user.password, pw):
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
        # child
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
        # parent
        if flask_login.current_user.role == "option2":
            name = request.form["staticName"]
            email = request.form["staticEmail"]
            child = request.form["child"]
            flask_login.current_user.name = name
            flask_login.current_user.email = email
            flask_login.current_user.child = child
            db_ses.commit()
            return "Успешно"
        # hh
        if flask_login.current_user.role == "option3":
            # name = request.form["name"]
            # email = request.form["email"]
            us_contacts = flask_login.current_user.contacts
            if us_contacts is not None:
                super_cont = us_contacts.split(', ')
            else:
                super_cont = []
            data_works = []
            works = list(
                map(int, flask_login.current_user.works.split(", ")[1:]))
            for e in works:
                work = db_ses.query(Vacancy).filter(Vacancy.id == e).first()
                one_work = (
                    work.name, work.minimal_age, work.town, work.salary,
                    len(work.description), work.id)
                data_works.append(one_work)
            return render_template("profile_hh.html",
                                   current_user=flask_login.current_user,
                                   contacts=super_cont[1:],
                                   vacancies=data_works,
                                   count=len(data_works))

    else:
        if flask_login.current_user.role == "option1":
            return render_template("profile_child.html", current_user=flask_login.current_user,
                                   db_ses=db_ses, User=User)
        elif flask_login.current_user.role == "option2":
            return render_template("profile_parent.html", current_user=flask_login.current_user,
                                   db_ses=db_ses, User=User)
        elif flask_login.current_user.role == "option3":
            print(1)
            us_contacts = flask_login.current_user.contacts
            if us_contacts is not None:
                super_cont = us_contacts.split(', ')
            else:
                super_cont = []

            data_works = []
            works = []
            if flask_login.current_user.works:
                works = list(
                    map(int, flask_login.current_user.works.split(", ")[1:]))
            for e in works:
                work = db_ses.query(Vacancy).filter(Vacancy.id == e).first()
                print(work)
                one_work = (work.name, work.minimal_age, work.town, work.salary, len(work.description), work.id)
                data_works.append(one_work)
            return render_template("profile_hh.html", current_user=flask_login.current_user, contacts=super_cont[1:],
                                   vacancies=data_works,
                                   count=len(data_works),
                                   db_ses=db_ses,
                                   User=User)
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


@app.route("/create_vacancy", methods=["POST"])
@login_required
def new_vacancy():
    print(12929)
    return render_template('add_vacancy.html')


@app.route("/vacancies", methods=["GET", "POST"])
@login_required
def vacancies():
    if request.method == 'POST':
        data_works = []
        works = []
        fil = request.form['find']
        works = db_ses.query(Vacancy).all()
        for e in works:
            work = e
            one_work = (work.name, work.minimal_age, work.town, work.salary,
                        len(work.description), work.id)
            if fil.lower() in work.name.lower() or fil.lower() in work.town.lower():
                data_works.append(one_work)

        if fil:
            return render_template('vacancies.html',
                                   filter=fil, vacancies=data_works, count=len(data_works))
        return render_template('vacancies.html',
                               filter='', vacancies=data_works, count=len(data_works))
    else:
        data_works = []
        works = []
        if flask_login.current_user.role == "option1" and flask_login.current_user.parent:
            if flask_login.current_user.works:
                works = list(
                    map(int, flask_login.current_user.works.split(", ")[1:]))
            for e in works:
                work = db_ses.query(Vacancy).filter(Vacancy.id == e).first()
                one_work = (work.name, work.minimal_age, work.town, work.salary, len(work.description), work.id)
                data_works.append(one_work)
        else:
            works = db_ses.query(Vacancy).all()
            for e in works:
                work = e
                one_work = (work.name, work.minimal_age, work.town, work.salary, len(work.description), work.id)
                data_works.append(one_work)
        return render_template("vacancies.html", vacancies=data_works, count=len(data_works))


@app.route('/go_to_vacancy', methods=['post'])
@login_required
def go_vacancy():
    action, vacancy_id = list(request.form)[0].split('-')
    vacancy_id = int(vacancy_id)
    print(vacancy_id)
    if action == 'go':
        return redirect(url_for('vacancy', vacancy_id=vacancy_id))
    elif action == 'del':
        db_ses.query(Vacancy).filter(Vacancy.id == vacancy_id).delete()
        flask_login.current_user.works = flask_login.current_user.works.replace(f', {vacancy_id}', '')
        db_ses.commit()
        return redirect('/profile')


@app.route('/redact_form', methods=['post'])
@login_required
def redact_form():
    ids = request.form['id']
    name = request.form["name1"]
    age = request.form["age"]
    text = request.form["Text1"]
    salary = request.form["salary"]
    address = request.form["address"]
    town = request.form["town"]
    vacanciy = db_ses.query(Vacancy).filter_by(id=ids).first()
    vacanciy.name = name
    vacanciy.owner = flask_login.current_user.id
    vacanciy.minimal_age = age
    vacanciy.description = text
    vacanciy.salary = salary
    vacanciy.address = address
    vacanciy.town = town
    # db_sess = db_session.create_session()
    db_ses.add(vacanciy)
    db_ses.commit()

    return redirect(url_for('vacancy', vacancy_id=ids))


@app.route("/vacancy", methods=["GET", "POST"])
@login_required
def vacancy():

    date = request.args.get('vacancy_id', None)
    if request.method == "POST":
        vac = db_ses.query(Vacancy).filter_by(id=date).first()
        print(vac)
        if flask_login.current_user.works:
            db_ses.query(User).filter_by(id=flask_login.current_user.child).first().works += f', {vac.id}'
        else:
            db_ses.query(User).filter_by(id=flask_login.current_user.child).first().works = f', {vac.id}'
        db_ses.commit()
        data_works = []
        works = db_ses.query(Vacancy).all()
        for e in works:
            work = e
            one_work = (work.name, work.minimal_age, work.town, work.salary, len(work.description), work.id)
            data_works.append(one_work)
        return render_template("vacancies.html", vacancies=data_works, count=len(data_works))
    else:
        vac = db_ses.query(Vacancy).filter_by(id=date).first()
        owner = db_ses.query(User).filter_by(id=vac.owner).first()
        db_ses.commit()
        contacts = owner.contacts.split(', ')[1:]
        return render_template("vacancy.html", contacts=contacts, vac=vac, current_user=flask_login.current_user, owner=owner)


@app.route("/add_vacancies", methods=["POST", "GET"])
@login_required
def add_vacancies():
    print(1818)
    if request.method == 'GET':
        pass
    else:
        name = request.form["name1"]
        age = request.form["age"]
        text = request.form["Text1"]
        salary = request.form["salary"]
        address = request.form["address"]
        town = request.form["town"]
        print(name, age, text, salary, address, town)

        vacanciy = Vacancy()
        vacanciy.name = name
        vacanciy.owner = flask_login.current_user.id
        vacanciy.minimal_age = age
        vacanciy.description = text
        vacanciy.salary = salary
        vacanciy.address = address
        vacanciy.town = town
        # db_sess = db_session.create_session()
        db_ses.add(vacanciy)
        db_ses.commit()
        if flask_login.current_user.works:
            flask_login.current_user.works += f', {vacanciy.id}'
        else:
            flask_login.current_user.works = f', {vacanciy.id}'
        db_ses.commit()
        return redirect('/vacancies')


@app.route("/request_to_child", methods=["POST"])
@login_required
def request_to_child():
    login = request.form["child"]
    print(login)
    user = db_ses.query(User).filter_by(email=login).first()
    user.parentreq = flask_login.current_user.id
    db_ses.commit()
    return redirect('/profile')


@app.route("/accept_parent", methods=["POST"])
@login_required
def accept_parent():
    login = request.form
    print(list(login)[0])
    if list(login)[0] == "delete":
        flask_login.current_user.parentreq = None
    elif list(login)[0] == "accept":
        db_ses.query(User).filter_by(id=flask_login.current_user.parentreq).first().child = flask_login.current_user.id
        flask_login.current_user.parent = flask_login.current_user.parentreq
        flask_login.current_user.parentreq = None
        db_ses.commit()
    return redirect('/profile')


@app.errorhandler(401)
def unauthorized_request(_):
    return "Для работы с сайтом необходима авторизация"


if __name__ == "__main__":
    app.register_blueprint(api.blueprint)
    app.run(debug=True)
