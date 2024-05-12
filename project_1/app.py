import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
from application import config
from application.database import db
from application.config import LocalDevelopmentConfig
from application.api import api,SectionApi,BookApi
from flask_migrate import Migrate

app=None

def create_app():
    app=Flask(__name__,template_folder="templates")
    if os.getenv('ENV',"development")=="production":
        raise Exception("Currently no os production config is setup")
    else:
        print('Starting local Development')
        app.config.from_object(LocalDevelopmentConfig)
        app.config['SECRET_KEY']="This Does'nt Concern me"
        db.init_app(app)
        api.init_app(app)
        app.app_context().push()
        return app
    
app=create_app()
migrate=Migrate(app,db,command='migrate')
    
with app.app_context():
    db.create_all()
    
from application.user_controllers import *
from application.book_controllers import *
from application.librarian_controllers import *
from application.section_controllers import *




if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
    
