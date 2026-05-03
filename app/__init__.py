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

# --- Database: use DATABASE_URL / SQLALCHEMY_DATABASE_URI env var in production ---
# Render/Heroku provide DATABASE_URL with "postgres://" prefix; SQLAlchemy needs "postgresql://"
_db_url = (
    os.environ.get('DATABASE_URL') or
    os.environ.get('SQLALCHEMY_DATABASE_URI')
)
if _db_url:
    _db_url = _db_url.strip()
    # If the user accidentally copy-pasted the instructions as the value
    if "Auto-set" in _db_url or "PostgreSQL" in _db_url or not "://" in _db_url:
        print(f"❌ ERROR: Invalid DATABASE_URL detected: '{_db_url}'")
        print("Falling back to local SQLite database.")
        _db_url = None
    elif _db_url.startswith('postgres://') or _db_url.startswith('postgresql://'):
        # Force SQLAlchemy to use the new psycopg v3 driver
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg://', 1)
        _db_url = _db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    
if _db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
else:
    # Local development: SQLite
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

# Use eventlet in production (when gunicorn/eventlet worker is active),
# fall back to default threading mode for local dev
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent' if os.environ.get('DATABASE_URL') else None
)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)  # Global CSRF protection for all POST forms

from app import routes, models, events