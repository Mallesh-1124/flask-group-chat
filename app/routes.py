from urllib.parse import urlparse
from werkzeug.security import check_password_hash, generate_password_hash

from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.models import User, Group, Message, File
from flask_login import login_user, current_user, logout_user, login_required

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'webp',
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'txt', 'csv', 'zip', 'mp4', 'mp3'
}


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    from app.forms import RegistrationForm
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Fix: use the model's set_password() method instead of hashing manually
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Fix: use the model method check_password() for consistency
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            # Fix: honour the ?next= redirect param, validated against open-redirect attacks
            next_page = request.args.get('next')
            if next_page:
                parsed = urlparse(next_page)
                # Only allow relative redirects (no external host)
                if parsed.netloc == '':
                    return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required  # Fix: guard against calling logout on an anonymous session
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from app.forms import UpdateAccountForm
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.password.data:
            current_user.set_password(form.password.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    user_files = File.query.filter_by(user_id=current_user.id).order_by(File.timestamp.desc()).all()
    return render_template('profile.html', title='Account', form=form, user_files=user_files)


@app.route('/')
@app.route('/home')
@login_required
def home():
    # Fix: show only the groups the current user is a member of (or owns)
    groups = Group.query.filter(
        (Group.owner_id == current_user.id) |
        Group.members.any(id=current_user.id)
    ).all()
    return render_template('home.html', groups=groups)


@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)

    if group.passkey and current_user not in group.members:
        if request.method == 'POST':
            entered_passkey = request.form.get('passkey', '')
            if entered_passkey and check_password_hash(group.passkey, entered_passkey):
                group.members.append(current_user)
                db.session.commit()
                flash('Successfully joined the group!', 'success')
                return redirect(url_for('group_chat', group_id=group.id))
            flash('Incorrect passkey.', 'danger')
        return render_template('enter_passkey.html', group=group)

    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp.asc()).all()
    files = File.query.filter_by(group_id=group.id).order_by(File.timestamp.desc()).all()
    return render_template('group_chat.html', group=group, messages=messages, files=files)


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    from app.forms import CreateGroupForm
    form = CreateGroupForm()
    if form.validate_on_submit():
        hashed_passkey = generate_password_hash(form.passkey.data) if form.passkey.data else None
        group = Group(name=form.name.data, owner_id=current_user.id, passkey=hashed_passkey)
        group.members.append(current_user)
        db.session.add(group)
        db.session.commit()
        flash(f'Group "{form.name.data}" created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_group.html', title='Create Group', form=form)


@app.route('/upload_file/<int:group_id>', methods=['POST'])
@login_required
def upload_file(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure the user is a member of the group before uploading
    if current_user not in group.members and current_user.id != group.owner_id:
        flash('You must be a member of this group to upload files.', 'danger')
        return redirect(url_for('group_chat', group_id=group_id))

    if 'file' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(url_for('group_chat', group_id=group_id))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('group_chat', group_id=group_id))

    # Fix: validate file extension against whitelist before uploading
    if not allowed_file(file.filename):
        flash(
            f'File type not allowed. Permitted types: {", ".join(sorted(ALLOWED_EXTENSIONS))}',
            'danger'
        )
        return redirect(url_for('group_chat', group_id=group_id))

    import os
    import werkzeug.utils
    from app import app
    
    filename = werkzeug.utils.secure_filename(file.filename)
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # The filepath saved in the database should be a relative URL to serve the file
    file_url = url_for('static', filename='uploads/' + filename)

    new_file = File(
        filename=filename,
        filepath=file_url,
        user_id=current_user.id,
        group_id=group_id
    )
    db.session.add(new_file)
    db.session.commit()
    flash('File uploaded successfully!', 'success')
    return redirect(url_for('group_chat', group_id=group_id))


@app.route('/clear_history/<int:group_id>', methods=['POST'])
@login_required
def clear_history(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user.id != group.owner_id:
        flash("You do not have permission to clear this group's history.", 'danger')
        return redirect(url_for('group_chat', group_id=group.id))

    Message.query.filter_by(group_id=group.id).delete()
    db.session.commit()
    flash('Group history cleared!', 'success')
    return redirect(url_for('group_chat', group_id=group.id))


@app.route('/download_file/<int:file_id>')
@login_required
def download_file(file_id):
    file_obj = File.query.get_or_404(file_id)
    group = Group.query.get_or_404(file_obj.group_id)

    if current_user not in group.members and current_user.id != group.owner_id:
        flash('You do not have permission to download this file.', 'danger')
        return redirect(url_for('group_chat', group_id=group.id))

    return redirect(file_obj.filepath)
