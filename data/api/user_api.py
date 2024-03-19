import flask
from flask import jsonify

from main import User
from ..database import db_session

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
                [item.to_dict(only=('id', 'name', 'email', 'role', 'resume', 'resumetxt'))
                 for item in users]
        }
    )


