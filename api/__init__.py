from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from api.models.db import db
from config import Config

# ============ Import Models ============
from api.models.toy import Association
from api.models.feeding import Feeding
from api.models.toy import Toy
from api.models.cat import Cat
from api.models.user import User
from api.models.profile import Profile

# ============ Import Views ============
from api.views.toys import toys
from api.views.cats import cats
from api.views.auth import auth

cors = CORS()
migrate = Migrate() 
list = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE', 'LINK']

def create_app(config):
  app = Flask(__name__)
  app.config.from_object(config)

  db.init_app(app)
  migrate.init_app(app, db)
  cors.init_app(app, supports_credentials=True, methods=list)

  # ============ Register Blueprints ============
  app.register_blueprint(toys, url_prefix='/api/toys')
  app.register_blueprint(cats, url_prefix='/api/cats')
  app.register_blueprint(auth, url_prefix='/api/auth') 

  return app

app = create_app(Config)