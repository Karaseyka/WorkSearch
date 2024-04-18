import flask
from flask import jsonify, make_response

from server import User
from ..database import db_session
from ..models.vacancy import Vacancy

db = db_session.create_session()

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_user():
    db_sess = db
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'email', 'role', 'resume', 'resumetxt', 'child', 'parent', 'child'))
                 for item in users]
        }
    )


@blueprint.route('/api/vacancies')
def get_vacancies():
    db_sess = db
    vacancies = db_sess.query(Vacancy).all()
    return jsonify(
        {
            'vacancies':
                [item.to_dict(only=('id', 'name', 'description', 'description', 'salary', 'minimal_age'))
                 for item in vacancies]
        }
    )


@blueprint.route('/api/vacancy/<int:vacancy_id>', methods=['GET'])
def get_one_vacancy(vacancy_id):
    db_ses = db
    vacancies = db_ses.query(Vacancy).get(vacancy_id)
    if not vacancies:
        return "No such vacancy"
    return jsonify(
        {
            'vacancy': vacancies.to_dict(only=(
                'id', 'name', 'owner', 'description', 'salary', 'address'))
        }
    )


@blueprint.route('/api/vacancy/salary/from<int:salary1>to<int:salary2>', methods=['GET'])
def get_range_salary(salary1, salary2):
    db_ses = db
    vacancies = db.query(Vacancy).filter(Vacancy.salary >= salary1).filter(Vacancy.salary <= salary2).all()
    if not vacancies:
        return "No such vacancy"
    return jsonify(
        {
            'vacancy': [item.to_dict(only=(
                'id', 'name', 'owner', 'description', 'salary', 'address')) for item in vacancies]
        }
    )
@blueprint.route('/api/vacancy/min_age/<int:min_age>', methods=['GET'])
def get_min_age(min_age):
    db_ses = db
    vacancies = db.query(Vacancy).filter(Vacancy.minimal_age >= min_age).all()
    if not vacancies:
        return "No such vacancy"
    return jsonify(
        {
            'vacancy': [item.to_dict() for item in vacancies]
        }
    )
