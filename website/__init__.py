from flask import Flask
from werkzeug.utils import secure_filename

SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thesis'

    from .views import views
    from .auth import auth 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')



    return app


#user_db.execute("create Table User(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, password1 TEXT NOT NULL)")    
#print('Table Created')

