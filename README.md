# Flask Group Chat Application

A real-time group chat application built with Flask, Flask-SocketIO, and Flask-SQLAlchemy, featuring user authentication, group creation with optional passkeys, real-time messaging, file sharing, and a responsive user interface with theme toggling.

## Features

*   **User Registration and Login:** Secure user authentication system.
*   **Group Creation:** Users can create their own chat groups.
*   **Optional Passkeys for Group Access:** Groups can be protected with a passkey for exclusive access.
*   **Real-time Group Chat:** Instant messaging within groups using WebSockets (Flask-SocketIO).
*   **File Sharing:** Users can upload and share files within their groups.
*   **User Profiles:** View and update user account information.
*   **Clear Chat and File History:** Group owners can clear the entire chat and file history of a group after confirming their passkey.
*   **Responsive Design:** User interface adapts to various screen sizes (desktops, tablets, mobile).
*   **Light/Dark Theme Toggling:** Switch between light and dark themes for personalized viewing.

## Technologies Used

*   **Backend:**
    *   [Flask](https://flask.palletsprojects.com/): Web framework.
    *   [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/): Integrates Socket.IO with Flask for real-time communication.
    *   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.1/): ORM for database interactions.
    *   [Flask-Login](https://flask-login.readthedocs.io/en/latest/): Manages user sessions.
    *   [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.2.x/): Integration with WTForms for web forms.
    *   [Werkzeug](https://werkzeug.palletsprojects.com/en/3.0.x/): WSGI utility library (used for password hashing).
    *   [python-engineio](https://python-engineio.readthedocs.io/en/latest/): Low-level Engine.IO server.
    *   [python-socketio](https://python-socketio.readthedocs.io/en/latest/): Python Socket.IO client and server.
*   **Frontend:**
    *   [Socket.IO Client](https://socket.io/docs/v4/client-api/): JavaScript library for real-time communication.
    *   [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/): CSS framework for responsive and modern UI components.
    *   [Font Awesome](https://fontawesome.com/): Icon library.
*   **Database:**
    *   SQLite (default, for development)
    *   PostgreSQL (for production)

## Screenshots

*(Please add screenshots of the application here to showcase the UI and features.)*

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd FLASK
```

### 2. Create a Python Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

*   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 5. Database Setup

The application uses SQLite for local development. The database file (`instance/site.db`) is automatically created when the application runs for the first time.

### 6. Set Flask Secret Key

Set a strong secret key for Flask. This is crucial for session security.

*   **Windows (PowerShell):**
    ```powershell
    $env:SECRET_KEY="your_super_secret_key_here"
    ```
*   **macOS/Linux:**
    ```bash
    export SECRET_KEY="your_super_secret_key_here"
    ```
    Replace `"your_super_secret_key_here"` with a long, random string.

## Running the Application

Once the setup is complete, you can run the Flask application:

```bash
flask run
```

The application will typically be available at `http://127.0.0.1:5000/`.

## Deployment on Render

This application is ready to be deployed on Render. Here are the steps to deploy it:

### 1. Push to GitHub

Create a new repository on GitHub and push your code to it.

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your_github_repository_url>
git push -u origin main
```

### 2. Create a Web Service on Render

*   Go to the [Render Dashboard](https://dashboard.render.com/) and click "New +" > "Web Service".
*   Connect your GitHub account and select your repository.
*   Give your service a name.

### 3. Configure the Service

*   **Environment:** Python
*   **Region:** Choose a region close to you.
*   **Branch:** main
*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `gunicorn run:app`

### 4. Add a PostgreSQL Database

*   Go to the [Render Dashboard](https://dashboard.render.com/) and click "New +" > "PostgreSQL".
*   Give your database a name and create it.
*   Copy the "Internal Connection URL" for your database.

### 5. Set Environment Variables

*   Go to your Web Service's "Environment" tab.
*   Add the following environment variables:
    *   `SECRET_KEY`: A long, random string for your Flask secret key.
    *   `SQLALCHEMY_DATABASE_URI`: The internal connection URL of your PostgreSQL database.

### 6. Update the Application for Production

To use PostgreSQL in production, you need to update the `__init__.py` file to use the `SQLALCHEMY_DATABASE_URI` environment variable.

**In `app/__init__.py`:**

```python
import os

# ... other imports

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///../instance/site.db'

# ... rest of the file
```

### 7. Add Gunicorn to requirements.txt

Add `gunicorn` to your `requirements.txt` file:

```
gunicorn
```

After completing these steps, your application should be successfully deployed on Render.

## Folder Structure

```
.
├── app/
│   ├── __init__.py             # Application initialization and configuration
│   ├── routes.py               # Defines URL routes and view functions
│   ├── models.py               # Database models (User, Group, Message, File)
│   ├── forms.py                # Web forms using Flask-WTF
│   ├── events.py               # Socket.IO event handlers
│   ├── static/                 # Static assets (CSS, JS, images)
│   │   ├── css/                # Stylesheets
│   │   └── uploads/            # Directory for uploaded files
│   └── templates/              # HTML templates
│       ├── base.html           # Base template for common layout
│       ├── home.html           # Homepage
│       ├── profile.html        # User profile page
│       ├── login.html          # User login page
│       ├── register.html       # User registration page
│       ├── create_group.html   # Group creation page
│       ├── group_chat.html     # Group chat interface
│       ├── enter_passkey.html  # Passkey entry page for protected groups
│       └── clear_history.html  # Clear history confirmation page
├── instance/
│   └── site.db                 # SQLite database file (for development)
├── requirements.txt            # Python dependencies
└── run.py                      # Entry point to run the application
```