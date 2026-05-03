from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    # Fix: db.session.get() replaces the deprecated Query.get() (removed in SQLAlchemy 2)
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text)
    messages = db.relationship('Message', backref='author', lazy=True)
    files = db.relationship('File', backref='uploader', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    passkey = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='owned_groups', lazy=True)
    # Fix: lazy='dynamic' is deprecated in SQLAlchemy 2 → use 'select' (default eager list)
    members = db.relationship(
        'User', secondary='group_members',
        backref=db.backref('chat_groups', lazy='select')
    )
    messages = db.relationship('Message', backref='group', lazy=True)
    files = db.relationship('File', backref='group', lazy=True)

    def __repr__(self):
        return f"Group('{self.name}')"


group_members = db.Table(
    'group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class MessageReadReceipt(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Fix: use explicit back_populates on both sides to avoid backref/back_populates conflict
    user = db.relationship(
        'User',
        backref=db.backref('message_read_receipts', lazy='select')
    )
    message = db.relationship('Message', back_populates='read_by_users')

    def __repr__(self):
        return (
            f"MessageReadReceipt(User ID: {self.user_id}, "
            f"Message ID: {self.message_id}, Read At: {self.timestamp})"
        )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    # Fix: explicit back_populates, no overlaps conflict, no lazy='dynamic'
    read_by_users = db.relationship(
        'MessageReadReceipt',
        back_populates='message',
        lazy='select'
    )

    def __repr__(self):
        return f"Message('{self.content}', '{self.timestamp}')"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    def __repr__(self):
        return f"File('{self.filename}', '{self.timestamp}')"
