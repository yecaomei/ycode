#!venv/bin/python
from flask_script import Manager
from app import create_app,db
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manage = Manager(app)

migrate = Migrate(app,db)
manage.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manage.run()
