from dotenv import load_dotenv
load_dotenv()

import os
from app import app, socketio

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    socketio.run(
        app,
        debug=debug_mode,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        allow_unsafe_werkzeug=True   # required for Flask-SocketIO 5.x dev server
    )
