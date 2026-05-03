# Flask Group Chat Application

A real-time group chat application built with **Flask**, **Flask-SocketIO**, and **Flask-SQLAlchemy** — featuring secure authentication, group creation with optional passkeys, real-time messaging, file sharing, a modern responsive UI, and full light/dark theme support.

---

## ✨ Features

- **User Registration & Login** — Secure authentication with password hashing via Werkzeug
- **Group Creation** — Create public or passkey-protected private groups
- **Real-time Messaging** — Instant WebSocket-powered chat via Flask-SocketIO
- **Typing Indicators** — Live "user is typing…" indicators in chat
- **File Sharing** — Upload and share files (images, PDFs, docs, etc.) within groups
- **File Type Validation** — Only whitelisted file extensions are accepted for upload
- **Read Receipts** — Messages track who has read them
- **User Profiles** — View and update username, email, and password
- **Clear Chat History** — Group owners can wipe the entire message history
- **Responsive UI** — Fully mobile-optimised with a collapsible file sidebar on small screens
- **Light / Dark Theme** — Persistent theme switching saved to localStorage
- **Toast Notifications** — Auto-dismissing flash messages for all user actions

---

## 🔒 Security

- **CSRF Protection** — All forms (including raw HTML forms) protected via Flask-WTF `CSRFProtect`
- **XSS Prevention** — Chat messages rendered with `textContent` (never `innerHTML`)
- **Authenticated WebSocket Handlers** — All SocketIO events verify `current_user.is_authenticated`
- **Safe Redirect Handling** — `?next=` redirects after login validated against open-redirect attacks
- **File Upload Whitelist** — Blocks executable/script uploads
- **Passkey Hashing** — Group passkeys stored as hashes, never in plaintext
- **SECRET_KEY Warning** — App warns at startup if `SECRET_KEY` is not set in the environment

---

## 🛠 Technologies Used

### Backend
| Package | Purpose |
|---------|---------|
| [Flask 3.0](https://flask.palletsprojects.com/) | Web framework |
| [Flask-SocketIO 5.3](https://flask-socketio.readthedocs.io/) | Real-time WebSocket communication |
| [Flask-SQLAlchemy 3.1](https://flask-sqlalchemy.palletsprojects.com/) | ORM (SQLAlchemy 2 compatible) |
| [Flask-Login 0.6](https://flask-login.readthedocs.io/) | Session management |
| [Flask-WTF 1.2](https://flask-wtf.readthedocs.io/) | Form handling & CSRF protection |
| [Flask-Migrate 4.0](https://flask-migrate.readthedocs.io/) | Database schema migrations |
| [Werkzeug 3.0](https://werkzeug.palletsprojects.com/) | Password hashing, WSGI utilities |
| [Cloudinary](https://cloudinary.com/documentation) | Cloud file storage |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable loading |
| [Gunicorn](https://gunicorn.org/) | Production WSGI server |

### Frontend
| Library | Purpose |
|---------|---------|
| [Bootstrap 5.3](https://getbootstrap.com/) | Responsive layout & components |
| [Font Awesome 6.5](https://fontawesome.com/) | Icon library |
| [Inter (Google Fonts)](https://fonts.google.com/specimen/Inter) | Primary typeface |
| [Socket.IO Client 4.0](https://socket.io/docs/v4/) | Real-time WebSocket client |

### Database
- **SQLite** — Development (auto-created at `instance/site.db`)
- **PostgreSQL** — Recommended for production

---

## 📁 Folder Structure

```
flask-group-chat/
├── app/
│   ├── __init__.py          # App factory, extensions, global config
│   ├── routes.py            # URL routes and view functions
│   ├── models.py            # Database models (User, Group, Message, File, MessageReadReceipt)
│   ├── forms.py             # WTForms form classes
│   ├── events.py            # Socket.IO event handlers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Design system (tokens, components, responsive)
│   │   └── uploads/         # Local upload directory (dev only)
│   └── templates/
│       ├── base.html        # Base layout (navbar, flash toasts, theme toggle)
│       ├── home.html        # Group listing with hero banner
│       ├── login.html       # Login page
│       ├── register.html    # Registration page
│       ├── profile.html     # User profile & file history
│       ├── create_group.html # Group creation form
│       ├── group_chat.html  # Chat interface with file sidebar
│       ├── enter_passkey.html # Passkey entry for private groups
│       └── clear_history.html # Clear history confirmation
├── instance/
│   └── site.db              # SQLite database (dev, git-ignored)
├── .gitignore               # Excludes venv, .env, instance/, __pycache__
├── requirements.txt         # Python dependencies
├── run.py                   # App entry point
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Mallesh-1124/flask-group-chat.git
cd flask-group-chat
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_long_random_secret_key_here
FLASK_DEBUG=true

# Required for file uploads (get free keys at cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Optional: PostgreSQL for production
# SQLALCHEMY_DATABASE_URI=postgresql://user:password@host/dbname
```

### 5. Initialise the Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('DB created')"
```

### 6. Run the App

```bash
python run.py
```

Open **http://localhost:5000** in your browser.

---

## 🚀 Deployment on Render

### 1. Push to GitHub

```bash
git add .
git commit -m "deploy"
git push origin main
```

### 2. Create a Web Service on Render

- Go to [Render Dashboard](https://dashboard.render.com/) → **New +** → **Web Service**
- Connect your GitHub repo

### 3. Configure the Service

| Setting | Value |
|---------|-------|
| Environment | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --worker-class eventlet -w 1 run:app` |

### 4. Add a PostgreSQL Database

- Render Dashboard → **New +** → **PostgreSQL**
- Copy the **Internal Connection URL**

### 5. Set Environment Variables (Render → Environment tab)

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | A long random string |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL internal connection URL |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret |

---

## 📋 Changelog

### v2.0.0 — Security & UI Overhaul *(May 2026)*

#### 🔴 Critical Bug Fixes
- Fixed `User.query.get()` → `db.session.get()` (removed in SQLAlchemy 2 — caused crash on every page load)
- Fixed duplicate password hashing in the register route; now correctly uses `user.set_password()`
- Fixed login to use `user.check_password()` instead of calling `check_password_hash` directly
- Fixed **XSS vulnerability** in real-time chat: replaced `innerHTML` with `textContent` for all incoming messages
- Fixed all SocketIO event handlers to verify `current_user.is_authenticated` (anonymous connections previously caused a server crash)
- Fixed `?next=` redirect after login (was silently ignored); now safely validated against open-redirect attacks

#### 🟠 Deprecation Fixes
- Fixed `lazy='dynamic'` on all relationships → `lazy='select'` (deprecated in SQLAlchemy 2)
- Fixed `MessageReadReceipt`/`Message` relationship conflict — replaced mixed `backref`/`back_populates` with explicit `back_populates` on both sides
- Fixed all Bootstrap 4 class usage (`btn-block`, `custom-file`, `custom-file-input`, `input-group-append`) → Bootstrap 5 equivalents

#### 🔒 Security Improvements
- Added global **CSRF protection** (`CSRFProtect`) — all forms, including raw HTML upload/clear-history forms, now include CSRF tokens
- Added **file extension whitelist** to uploads (blocks `.exe`, `.php`, `.html`, etc.)
- Added **group membership check** before allowing file upload
- Added `@login_required` decorator to the `logout` route
- Added `RuntimeWarning` at startup if `SECRET_KEY` is not set in the environment
- Added `SQLALCHEMY_TRACK_MODIFICATIONS = False` to suppress SQLAlchemy warnings

#### ✨ New UI Features
- **Complete UI redesign** with Inter font, indigo/violet design system, and curated dark/light color tokens
- **Smart theme toggle** with sun/moon icon that persists across sessions
- **Toast-style flash messages** with auto-dismiss after 4.5 seconds and icon-per-category
- **Responsive chat layout** — two-column (messages + file sidebar) on desktop, collapsible sidebar on mobile
- **Chat header** with group avatar (initial letter), member count, and quick-action buttons
- **Home page** redesigned with hero banner, group cards with avatar initials, owner badge, and private group lock indicator
- **Auth pages** (login/register) with centred card layout, password show/hide toggle, and inline field validation
- **Profile page** with sticky sidebar, group/file stats, and responsive two-column settings form
- **Create Group** and **Enter Passkey** pages with action-card layout, passkey hint, and password visibility toggle
- **File sidebar** with smart file-type icons (image, PDF, Word, Excel, ZIP, video, audio)
- **Typing indicators** shown in real-time when other users are typing
- Added confirmation dialog to the destructive Clear History button
- `run.py` now reads `FLASK_DEBUG` and `PORT` from environment variables

#### 🔵 Code Quality
- Moved `import cloudinary.uploader` to top of `routes.py` (was inside function body)
- Home route now queries only the current user's groups (was returning all groups in the DB)
- Added `.gitignore` excluding `venv/`, `.env`, `instance/`, `__pycache__/`, and `app/static/uploads/`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open-source. Feel free to use and modify it.