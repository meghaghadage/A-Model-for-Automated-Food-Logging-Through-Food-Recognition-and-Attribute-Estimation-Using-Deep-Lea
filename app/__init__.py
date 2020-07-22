from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)


from .models import FoodUser

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return FoodUser.query.get(user_id)

from app import routes
