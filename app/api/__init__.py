from flask import Blueprint,session,g

api = Blueprint('api', __name__, static_folder='', static_url_path ='')


@api.before_request
def login_before_request():
    user = session.get('user')
    g.user = user