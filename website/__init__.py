from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_admin import Admin
#from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename


SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thesis'
    #app.config['FLASK_ADMIN_SWATCH'] = 'lumen'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Criszelle/Desktop/THESIS/system.db'
    
    #db = SQLAlchemy(app)
    #admin = Admin(app, name='FOMO: Admin Panel', template_mode='bootstrap3')

    #class User(db.Model):
        #id = db.Column(db.Integer, primary_key = True)
        #email = db.Column(db.String, unique = True)
        #password = db.Column(db.String)
        #password1 = db.Column(db.String)

    #admin.add_view(ModelView(User, db.session))

    #class Candlestick(db.Model):
        #id = db.Column(db.Integer, primary_key = True)
        #title = db.Column(db.String)
        #description = db.Column(db.String)

    #admin.add_view(ModelView(Candlestick, db.session))

    from .views import views
    from .auth import auth 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')



    return app



#user_db.execute("create Table User(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, password1 TEXT NOT NULL)")    
#print('Table Created')

