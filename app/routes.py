from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateGroupForm, ConfirmPasskeyForm
import os
from flask import render_template, url_for, flash, redirect, request, send_from_directory
from app import app, db
from app.models import User, Group, Message, File
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
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
    groups = Group.query.all()
    return render_template('home.html', groups=groups)

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)

    if group.passkey and current_user not in group.members:
        if request.method == 'POST':
            entered_passkey = request.form.get('passkey')
            if check_password_hash(group.passkey, entered_passkey):
                group.members.append(current_user)
                db.session.commit()
                flash('Successfully joined the group!', 'success')
                return redirect(url_for('group_chat', group_id=group.id))
            else:
                flash('Incorrect passkey.', 'danger')
        return render_template('enter_passkey.html', group=group)

    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp.asc()).all()
    files = File.query.filter_by(group_id=group.id).order_by(File.timestamp.desc()).all()
    return render_template('group_chat.html', group=group, messages=messages, files=files)

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        hashed_passkey = generate_password_hash(form.passkey.data) if form.passkey.data else None
        group = Group(name=form.name.data, owner_id=current_user.id, passkey=hashed_passkey)
        group.members.append(current_user)
        db.session.add(group)
        db.session.commit()
        flash(f'Group {form.name.data} created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_group.html', title='Create Group', form=form)


@app.route('/upload_file/<int:group_id>', methods=['POST'])
@login_required
def upload_file(group_id):
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_file = File(filename=filename, filepath=filepath, user_id=current_user.id, group_id=group_id)
        db.session.add(new_file)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
    return redirect(url_for('group_chat', group_id=group_id))

@app.route('/download_file/<int:file_id>')
@login_required
def download_file(file_id):
    file_obj = File.query.get_or_404(file_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_obj.filename, as_attachment=True)

@app.route('/clear_history/<int:group_id>', methods=['GET', 'POST'])
@login_required
def clear_history(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user.id != group.owner_id:
        flash('You are not the owner of this group.', 'danger')
        return redirect(url_for('group_chat', group_id=group.id))

    form = ConfirmPasskeyForm()
    if form.validate_on_submit():
        if check_password_hash(group.passkey, form.passkey.data):
            # Delete messages
            Message.query.filter_by(group_id=group.id).delete()
            # Delete files
            files_to_delete = File.query.filter_by(group_id=group.id).all()
            for file in files_to_delete:
                try:
                    os.remove(file.filepath)
                except OSError as e:
                    flash(f'Error deleting file {file.filename}: {e}', 'danger')
            File.query.filter_by(group_id=group.id).delete()
            db.session.commit()
            flash('Chat and file history has been cleared.', 'success')
            return redirect(url_for('group_chat', group_id=group.id))
        else:
            flash('Incorrect passkey.', 'danger')

    return render_template('clear_history.html', title='Clear History', form=form, group=group)
