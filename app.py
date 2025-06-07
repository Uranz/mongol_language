import logging
import time
import atexit
import random
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_babel import Babel
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired
from db import db
from db.models import User, Role, Config, Word, Quiz, UserProgress

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Initialize extensions
babel = Babel(app)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class QuizForm(FlaskForm):
    answer = RadioField('Answer', choices=[], validators=[DataRequired()])
    submit = SubmitField('Check Answer')

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Authentication page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Custom Admin Home View
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Custom Admin Views
class WordAdminView(ModelView):
    column_list = ['mongolian', 'english', 'part_of_speech', 'difficulty', 'category']
    column_searchable_list = ['mongolian', 'english', 'category']
    column_filters = ['difficulty', 'category', 'part_of_speech']
    form_columns = ['mongolian', 'english', 'part_of_speech', 'example_sentence', 
                   'difficulty', 'audio_url', 'category']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

class QuizAdminView(ModelView):
    column_list = ['word_id', 'user_id', 'correct_option', 'created_at']
    column_searchable_list = ['correct_option']
    form_columns = ['word_id', 'user_id', 'options', 'correct_option']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

class UserProgressAdminView(ModelView):
    column_list = ['user_id', 'word_id', 'quiz_score', 'last_seen', 'favorite']
    column_searchable_list = ['user_id', 'word_id']
    column_filters = ['favorite', 'quiz_score']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

# Admin setup
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Config, db.session))
admin.add_view(WordAdminView(Word, db.session))
admin.add_view(QuizAdminView(Quiz, db.session))
admin.add_view(UserProgressAdminView(UserProgress, db.session))

# Vocabulary learning routes
@app.route('/learn')
@login_required
def learn():
    # Get a random word from the vocabulary
    word = Word.query.order_by(db.func.random()).first()
    if not word:
        flash('No vocabulary words available. Please add some words first.')
        return redirect(url_for('admin.index'))
    
    # Update user progress
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        word_id=word.id
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, word_id=word.id)
        db.session.add(progress)
    
    progress.last_seen = db.func.now()
    db.session.commit()
    
    return render_template('learn.html', word=word)

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    # Get a random word for the question
    correct_word = Word.query.order_by(db.func.random()).first()
    if not correct_word:
        flash('No vocabulary words available. Please add some words first.')
        return redirect(url_for('admin.index'))
    
    # Get 3 random wrong answers
    wrong_answers = Word.query.filter(
        Word.id != correct_word.id
    ).order_by(db.func.random()).limit(3).all()
    
    # Combine correct and wrong answers and shuffle them
    all_answers = [correct_word.english] + [w.english for w in wrong_answers]
    random.shuffle(all_answers)
    
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        # Update user progress
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            word_id=correct_word.id
        ).first()
        
        if not progress:
            progress = UserProgress(user_id=current_user.id, word_id=correct_word.id)
            db.session.add(progress)
        
        if user_answer == correct_word.english:
            progress.quiz_score += 1
            flash('Correct! Well done!', 'success')
        else:
            flash(f'Incorrect. The correct answer was: {correct_word.english}', 'error')
        
        progress.last_seen = db.func.now()
        db.session.commit()
        
        # Create a new quiz entry
        quiz = Quiz(
            word_id=correct_word.id,
            user_id=current_user.id,
            correct_option=correct_word.english
        )
        quiz.set_options(all_answers)
        db.session.add(quiz)
        db.session.commit()
        
        return redirect(url_for('quiz'))
    
    return render_template('quiz.html', 
                         question=correct_word.mongolian,
                         answers=all_answers,
                         correct_answer=correct_word.english,
                         word_id=correct_word.id)

# Create templates for vocabulary learning
with open('templates/learn.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Learn Mongolian</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Learn Mongolian Vocabulary</h1>
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">{{ word.mongolian }}</h2>
                <p class="card-text">English: {{ word.english }}</p>
                {% if word.part_of_speech %}
                <p class="card-text"><small class="text-muted">Part of Speech: {{ word.part_of_speech }}</small></p>
                {% endif %}
                {% if word.example_sentence %}
                <p class="card-text">Example: {{ word.example_sentence }}</p>
                {% endif %}
                {% if word.audio_url %}
                <audio controls>
                    <source src="{{ word.audio_url }}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
                {% endif %}
            </div>
        </div>
        <div class="mt-3">
            <a href="{{ url_for('learn') }}" class="btn btn-primary">Next Word</a>
            <a href="{{ url_for('quiz') }}" class="btn btn-secondary">Take a Quiz</a>
        </div>
    </div>
</body>
</html>
''')

with open('templates/quiz.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Mongolian Quiz</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Mongolian Vocabulary Quiz</h1>
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">What does "{{ question }}" mean?</h2>
                <form method="POST" action="{{ url_for('quiz') }}">
                    {% for answer in answers %}
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="answer" value="{{ answer }}" id="answer{{ loop.index }}">
                        <label class="form-check-label" for="answer{{ loop.index }}">
                            {{ answer }}
                        </label>
                    </div>
                    {% endfor %}
                    <input type="hidden" name="correct_answer" value="{{ correct_answer }}">
                    <input type="hidden" name="word_id" value="{{ word_id }}">
                    <button type="submit" class="btn btn-primary mt-3">Check Answer</button>
                </form>
            </div>
        </div>
        <div class="mt-3">
            <a href="{{ url_for('learn') }}" class="btn btn-secondary">Back to Learning</a>
        </div>
    </div>
</body>
</html>
''')

if __name__ == '__main__':
    import time
    time.sleep(2)  # Ensure SSH tunnel or other services are ready
    with app.app_context():
        print("Creating database tables...")
        db.create_all()  # This must be called before any queries

        # Import models here to ensure they are registered
        from db.models import Role, User
        from werkzeug.security import generate_password_hash

        # Add default roles if not present
        if not Role.query.first():
            roles = [
                Role(id=1, name='viewer'),
                Role(id=2, name='editor'),
                Role(id=3, name='admin')
            ]
            db.session.bulk_save_objects(roles)
            db.session.commit()

        # Add an admin user for testing (if not present)
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role_id=3  # Assign admin role
            )
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True, port=4242) 