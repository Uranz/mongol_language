from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from db.models import User, Role
from db import db
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = Role.query.filter_by(name='viewer').first()
        if not role:
            flash('Default role not found.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        user = User(username=username, email=email, role_id=role.id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

class UserAdminView(ModelView):
    form_columns = [
        'is_paid', 'username', 'email', 'password', 'role_id', 'created_at', 'updated_at',
        'fluency_level', 'score', 'is_admin', 'last_active', 'avatar_url'
    ] 