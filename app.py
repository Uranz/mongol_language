import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from db import db
from db.models import User, Role, Config, Word, Test, Question, UserProgress

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
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in to access this page."
csrf = CSRFProtect(app)

# Temporarily disable CSRF protection for debugging
app.config['WTF_CSRF_ENABLED'] = False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom Admin Views
class WordAdminView(ModelView):
    column_list = ['mongolian', 'english', 'part_of_speech', 'difficulty', 'category']
    column_searchable_list = ['mongolian', 'english', 'category']
    column_filters = ['difficulty', 'category', 'part_of_speech']
    form_columns = ['mongolian', 'english', 'part_of_speech', 'example_sentence', 
                   'difficulty', 'audio_url', 'category']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

class TestAdminView(ModelView):
    column_list = ['title', 'is_sample', 'created_at']
    column_searchable_list = ['title']
    form_columns = ['title', 'is_sample']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

class QuestionAdminView(ModelView):
    column_list = ['test_id', 'question_text', 'correct_answer']
    column_searchable_list = ['question_text']
    form_columns = ['test_id', 'question_text', 'option_a', 'option_b', 'option_c', 
                   'option_d', 'option_e', 'correct_answer', 'explanation']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

class UserProgressAdminView(ModelView):
    column_list = ['user_id', 'word_id', 'quiz_score', 'last_seen', 'favorite']
    column_searchable_list = ['user_id', 'word_id']
    column_filters = ['favorite', 'quiz_score']
    
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user.role, 'name', None) == 'admin'

# Admin setup
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Config, db.session))
admin.add_view(WordAdminView(Word, db.session))
admin.add_view(TestAdminView(Test, db.session))
admin.add_view(QuestionAdminView(Question, db.session))
admin.add_view(UserProgressAdminView(UserProgress, db.session))

# Register blueprints
from routes.test_routes import test_bp
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp

app.register_blueprint(test_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True) 