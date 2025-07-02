from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

# Assuming db will be initialized in the main app and imported here
from db import db

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Role name: viewer, editor, admin, owner
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Role {self.name}>"

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_paid = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    fluency_level = db.Column(db.String(20), nullable=False, default='Beginner')
    score = db.Column(db.Integer, nullable=False, default=0)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    last_active = db.Column(db.DateTime, nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}, Role {self.role.name}>"

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the stored hash."""
        return check_password_hash(self.password, password)

class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mongolian = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(200), nullable=False)
    part_of_speech = db.Column(db.String(50))
    example_sentence = db.Column(db.Text)
    difficulty = db.Column(db.String(20))  # Using string for flexibility (easy, medium, hard)
    audio_url = db.Column(db.String(255))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Word {self.mongolian} - {self.english}>"

class Test(db.Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    is_sample = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relationship with questions
    questions = db.relationship('Question', backref='test', lazy=True)

    def __repr__(self):
        return f"<Test {self.title}>"

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'), nullable=False)
    question_text = db.Column(db.String(1700), nullable=False)
    option_a = db.Column(db.String(1200), nullable=False)
    option_b = db.Column(db.String(1200), nullable=False)
    option_c = db.Column(db.String(1200), nullable=False)
    option_d = db.Column(db.String(1200), nullable=False)
    option_e = db.Column(db.String(1200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.String(5500), nullable=False)

    def __repr__(self):
        return f"<Question {self.question_id} for Test {self.test_id}>"

class Config(db.Model):
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False) 
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Config {self.key}>"

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # e.g., Beginner, Intermediate, Advanced
    lesson_type = db.Column(db.String(50), nullable=False)  # e.g., flashcard, grammar, quiz
    content = db.Column(db.Text, nullable=False)  # Markdown or HTML
    audio_url = db.Column(db.String(255), nullable=True)  # Optional audio file URL

    def __repr__(self):
        return f"<Lesson {self.title} ({self.level})>"

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique progress record
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # References the user
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)  # References the lesson
    is_completed = db.Column(db.Boolean, default=False, nullable=False)  # True if user finished the lesson
    score = db.Column(db.Integer, default=0, nullable=False)  # Quiz score or performance
    time_spent = db.Column(db.Integer, nullable=True)  # Time spent on lesson (seconds)
    last_accessed = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)  # Last time user accessed the lesson

    # Relationships
    user = db.relationship('User', backref=db.backref('lesson_progress', lazy=True))  # Link to User
    lesson = db.relationship('Lesson', backref=db.backref('progress', lazy=True))  # Link to Lesson

    def __repr__(self):
        return f"<LessonProgress user_id={self.user_id} lesson_id={self.lesson_id} completed={self.is_completed}>"