from flask import Blueprint,session,g

main = Blueprint('main', __name__, static_folder='', static_url_path ='')

from . import view, exescript, frontgetdata,testcaseview
from ..models import Permission

@main.before_request
def login_before_request():
    user = session.get('user')
    g.user = user

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
