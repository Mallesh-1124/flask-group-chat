from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
import warnings

app = Flask(__name__)

# --- Security: warn if SECRET_KEY is missing ---
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    warnings.warn(
        "SECRET_KEY environment variable is not set. "
        "Using an insecure default — set it in your .env file before deploying!",
        RuntimeWarning
    )
    secret_key = 'change-me-in-production-please'

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        'instance', 'site.db'
    )
)
app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'static/uploads'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)  # Global CSRF protection for all POST forms

from app import routes, models, events