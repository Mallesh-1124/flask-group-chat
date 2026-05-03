"""
wsgi.py — Production entry point for Gunicorn.
Gunicorn does not call run.py's __main__ block, so we expose
the app object directly here for it to use.
"""
from dotenv import load_dotenv
load_dotenv()

from app import app, db

# Create all tables on first deploy (safe to call repeatedly)
with app.app_context():
    db.create_all()

# Gunicorn imports 'app' from this module
if __name__ == '__main__':
    app.run()
