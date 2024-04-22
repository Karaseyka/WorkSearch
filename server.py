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
from requests import get

app = Flask(__name__)
app.secret_key = 'some key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///worksearch.db"

db_session.global_init("instance/worksearch.db")

manager = LoginManager(app)
manager.init_app(app)
db_ses = db_session.create_session()


# загрузка ползователя
@manager.user_loader
def load_user(user_id):
    return db_ses.query(User).get(user_id)


# выход из акка ползователя
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('welcome_page'))


# стартовый экран
@app.route("/")
def welcome_page():
    return render_template("welcome_page.html", db_ses=db_ses, Vacancy=Vacancy, User=User)


# экран инструкции
@app.route("/instruction")
def instruction():
    return render_template("instruction.html", db_ses=db_ses, Vacancy=Vacancy, User=User)


# экран регистрации
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
            return redirect("/profile")
        except:
            db_ses.rollback()
            return "Такой email уже существует"

    else:
        return "Пароли не совпадают"


@app.route("/registration", methods=["GET"])
def registration_get():
    return render_template("registration.html")


# экран входа
@app.route("/enter", methods=["POST"])
def enter_post():
    login = request.form.get("email")
    pw = request.form.get("password")
    if login and pw:
        user = db_ses.query(User).filter_by(email=login).first()
        if user and check_password_hash(user.password, pw):
            login_user(user)

            return render_template("instruction.html", db_ses=db_ses, Vacancy=Vacancy, User=User)
        else:
            return render_template("enter.html")

    else:
        return render_template("enter.html")


@app.route("/enter", methods=["GET"])
def enter_get():
    return render_template("enter.html")


# экран профиля
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
                        return render_template("profile_child.html",
                                               current_user=flask_login.current_user,
                                               db_ses=db_ses, Vacancy=Vacancy, User=User)
                    except:
                        return "Неудалось добавить файл"
                else:
                    return "Нужен .pdf формат"
            elif len(txt) == 0:
                flask_login.current_user.name = name
                flask_login.current_user.email = email
                db_ses.commit()
                return render_template("profile_child.html",
                                       current_user=flask_login.current_user,
                                       db_ses=db_ses, Vacancy=Vacancy, User=User)
            elif txt:
                flask_login.current_user.name = name
                flask_login.current_user.email = email
                flask_login.current_user.resume = None
                flask_login.current_user.resumetxt = txt
                db_ses.commit()
                return render_template("profile_child.html",
                                       current_user=flask_login.current_user,
                                       db_ses=db_ses, Vacancy=Vacancy, User=User)
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
                                   count=len(data_works),
                                   db_ses=db_ses, Vacancy=Vacancy, User=User)

    else:
        if flask_login.current_user.role == "option1":
            data_works = []
            works = []
            if flask_login.current_user.otkliks:
                works = list(map(int, flask_login.current_user.otkliks.split(", ")[1:]))

            for a in works:
                work = db_ses.query(Vacancy).filter(Vacancy.id == a).first()
                print(work)
                one_work = (work.name, work.minimal_age, work.town, work.salary, len(work.description), work.id)
                data_works.append(one_work)

            return render_template("profile_child.html", current_user=flask_login.current_user,
                                   db_ses=db_ses, User=User, Vacancy=Vacancy, vacancies=data_works,
                                   count=len(data_works))
        elif flask_login.current_user.role == "option2":
            data_works = []
            works = []
            if flask_login.current_user.child:
                if db_ses.query(User).filter_by(id=flask_login.current_user.child).first().worksfromparent:
                    works = list(
                        map(int, db_ses.query(User).filter_by(
                            id=flask_login.current_user.child).first().worksfromparent.split(", ")[1:]))

            for a in works:
                work = db_ses.query(Vacancy).filter(Vacancy.id == a).first()
                print(work)
                one_work = (
                    work.name, work.minimal_age, work.town, work.salary,
                    len(work.description), work.id)
                data_works.append(one_work)
            return render_template("profile_parent.html", current_user=flask_login.current_user,
                                   db_ses=db_ses, User=User, Vacancy=Vacancy, vacancies=data_works,
                                   count=len(data_works))
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
                                   db_ses=db_ses, Vacancy=Vacancy, User=User)
        else:
            return "Технические шоколадки"


# удаление контактов
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


# добавить контакы
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


# обновление данных профиля
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


# скачивание резюме
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


# скачивание чужого резюме
@app.route("/resume/<user>", methods=["GET"])
@login_required
def resume_user(user):
    img = db_ses.query(User).filter_by(id=user).first().resume
    txt = db_ses.query(User).filter_by(id=user).first().resumetxt
    if img:
        return send_file(BytesIO(img),
                         download_name="resume.pdf", as_attachment=True)
    elif txt:
        return txt
    else:
        return "Резюме не найдено"


# экран создания новой вакансии
@app.route("/create_vacancy", methods=["POST"])
@login_required
def new_vacancy():
    print(12929)
    return render_template('add_vacancy.html', db_ses=db_ses, Vacancy=Vacancy, User=User)


# Список вакансий
@app.route("/vacancies", methods=["GET", "POST"])
@login_required
def vacancies():
    vacancies_all = get_vacancies()
    if request.method == 'POST':
        data_works = []
        works = []
        fil = request.form['find']
        works = db_ses.query(Vacancy).all()
        print(vacancies_all)
        for e in works:
            work = e
            one_work = (work.name, work.minimal_age, work.town, work.salary,
                        len(work.description), work.id)
            if fil.lower() in work.name.lower() or fil.lower() in work.town.lower():
                if not flask_login.current_user.parent or str(
                        work.id) in flask_login.current_user.worksfromparent.split(", "):
                    data_works.append(one_work)

        if fil:
            return render_template('vacancies.html',
                                   filter=fil, vacancies=data_works, count=len(data_works), db_ses=db_ses,
                                   Vacancy=Vacancy, User=User)
        return render_template('vacancies.html',
                               filter='', vacancies=data_works, count=len(data_works), db_ses=db_ses, Vacancy=Vacancy,
                               User=User)
    else:
        data_works = []
        works = []
        if flask_login.current_user.role == "option1" and flask_login.current_user.parent:
            if flask_login.current_user.worksfromparent:
                works = list(
                    map(int, flask_login.current_user.worksfromparent.split(", ")[1:]))
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
        return render_template("vacancies.html", vacancies=data_works, count=len(data_works), db_ses=db_ses,
                               Vacancy=Vacancy, User=User)


# переход к вакансии
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
        s = flask_login.current_user.otkliks.split(', ')
        new_otkliks = []
        print(s)
        for e in s[1:]:
            print(vacancy_id, int(e.split('-')[-1]))
            if vacancy_id != int(e.split('-')[-1]):
                new_otkliks.append(e)
            else:
                for user in db_ses.query(User).filter(User.role == 'option1').all():
                    print(user.otkliks, 91910190)
                    if user.otkliks:
                        a = user.otkliks.split(', ')
                        for vac in a[1:]:
                            if int(vac.split('-')[-1]) == vacancy_id:
                                user.otkliks = user.otkliks.replace(f', {vac}', '')

        flask_login.current_user.otkliks = ', ' + ', '.join(new_otkliks)

        db_ses.commit()
        return redirect('/profile')


# редактирование вакансии
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


# экран вакансии
@app.route("/vacancy", methods=["GET", "POST"])
@login_required
def vacancy():
    date = request.args.get('vacancy_id', None)
    if not flask_login.current_user.otkliks:
        flask_login.current_user.otkliks = ''
    if request.method == "POST":
        vac = db_ses.query(Vacancy).filter_by(id=date).first()
        print(vac, flask_login.current_user.role)
        if flask_login.current_user.role == "option2":
            print("qwertyuiop")
            if db_ses.query(User).filter_by(id=flask_login.current_user.child).first().worksfromparent:
                print("qwertyuio")
                db_ses.query(User).filter_by(id=flask_login.current_user.child).first().worksfromparent += f', {vac.id}'
            else:
                print("qwertyuiol;'")
                db_ses.query(User).filter_by(id=flask_login.current_user.child).first().worksfromparent = f', {vac.id}'
            db_ses.commit()
            return redirect('/vacancies')
        else:
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
        return render_template("vacancy.html", contacts=contacts, vac=vac, current_user=flask_login.current_user,
                               owner=owner, db_ses=db_ses, Vacancy=Vacancy, User=User, ids=str(vac.id))


# экран просмотра чужого профиля
@app.route("/profile_review/<int:user>")
def profile_review(user):
    return render_template("profile_review.html", db_ses=db_ses, Vacancy=Vacancy, User=User,
                           user=db_ses.query(User).filter_by(id=user).first())


# добавление вакансии
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


# отклик на вакансию
@app.route('/otklik', methods=['POST'])
@login_required
def oklik():
    ids = request.form['id']
    vacanciy = db_ses.query(Vacancy).filter_by(id=ids).first()
    owner = vacanciy.owner
    user = db_ses.query(User).filter_by(id=owner).first()
    print(user.otkliks)
    if user.otkliks:

        user.otkliks += ', ' + str(flask_login.current_user.id) + '-' + str(ids)
    else:
        user.otkliks = ', ' + str(flask_login.current_user.id) + '-' + str(ids)
    print(-11010)
    flask_login.current_user.otkliks += ', ' + str(ids)

    db_ses.commit()
    return redirect('/vacancies')


# Запрос к ребёнку
@app.route("/request_to_child", methods=["POST"])
@login_required
def request_to_child():
    login = request.form["child"]
    print(login)
    user = db_ses.query(User).filter_by(email=login).first()
    user.parentreq = flask_login.current_user.id
    db_ses.commit()
    return redirect('/profile')


# Принятие родителем ребёнка
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


# Если юзер не авторизован
@app.errorhandler(401)
def unauthorized_request(_):
    return "Для работы с сайтом необходима авторизация"


def get_vacancies():
    return get('https://worckserch.glitch.me/api/vacancies').json()


if __name__ == "__main__":
    app.register_blueprint(api.blueprint)
    app.run(debug=True)
