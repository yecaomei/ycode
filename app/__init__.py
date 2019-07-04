from flask import Flask
from .ext import db
from flask_wtf import CSRFProtect
from .models import User,Role,Project,Module,Version,Api,Case

import config
# bootstrap = Bootstrap()
csrfprotect = CSRFProtect()



def create_app():
    app = Flask(__name__, static_folder='static', static_url_path ='')
    csrfprotect.init_app(app)
    app.config.from_object(config)
    # bootstrap.init_app(app)
    db.init_app(app)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api')


    return app