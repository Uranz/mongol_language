from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from sqlalchemy import event

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
    
    def get_all_meanings(self):
        """Get all possible meanings for this Mongolian word"""
        # Check if this word has multiple meanings defined
        if '|' in self.english:
            return [meaning.strip() for meaning in self.english.split('|')]
        else:
            return [self.english]
    
    def get_primary_meaning(self):
        """Get the primary (first) meaning of the word"""
        meanings = self.get_all_meanings()
        return meanings[0] if meanings else self.english
    
    def has_multiple_meanings(self):
        """Check if this word has multiple meanings"""
        return '|' in self.english
    
    def get_formatted_meanings(self):
        """Get a formatted string of all meanings for display"""
        meanings = self.get_all_meanings()
        if len(meanings) == 1:
            return meanings[0]
        else:
            return f"{meanings[0]} (also: {', '.join(meanings[1:])})"

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
    option_a = db.Column(db.String(1200), nullable=True)
    option_b = db.Column(db.String(1200), nullable=True)
    option_c = db.Column(db.String(1200), nullable=True)
    option_d = db.Column(db.String(1200), nullable=True)
    option_e = db.Column(db.String(1200), nullable=True)
    correct_answer = db.Column(db.String(1), nullable=True)
    explanation = db.Column(db.String(5500), nullable=False)
    correct_answer_text = db.Column(db.String(1200), nullable=True)
    question_type = db.Column(db.String(50), nullable=True)
    # Removed explicit test relationship to avoid backref conflict

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

def create_questions_for_new_word(mapper, connection, target):
    from db.models import Word, Question, Test
    import random
    from db import db
    
    try:
        # Ensure there are at least 4 words for distractors
        words = Word.query.all()
        if len(words) < 4:
            return

        # Get or create a test
        test = Test.query.first()
        if not test:
            test = Test(title="Auto-generated Vocabulary Test", is_sample=True)
            db.session.add(test)
            # Don't commit here - let Flask-Admin handle the transaction

        # --- Translation question (Mongolian to English) - Multiple correct answers ---
        q_text = f"Translate {target.mongolian}' to English"
        existing = Question.query.filter_by(test_id=test.test_id, question_text=q_text).first()
        if not existing:
            # Use the word's multiple meanings if available
            correct_answers = target.english  # This already contains pipe-separated meanings if they exist
            
            # Create explanation that shows all meanings
            if target.has_multiple_meanings():
                meanings = target.get_all_meanings()
                explanation = f"{target.mongolian} can mean: {', '.join(meanings)}"
            else:
                explanation = f"{target.mongolian}' means {target.english}'."
            
            q = Question(
                test_id=test.test_id,
                question_text=q_text,
                question_type='translation',
                correct_answer_text=correct_answers,
                explanation=explanation
            )
            db.session.add(q)
            # Don't commit here - let Flask-Admin handle the transaction

        # --- Translation question (English to Mongolian) - Multiple questions for multiple meanings ---
        if target.has_multiple_meanings():
            # Create separate questions for each meaning
            meanings = target.get_all_meanings()
            for meaning in meanings:
                q_text_reverse = f"Translate '{meaning}' to Mongolian"
                existing_reverse = Question.query.filter_by(test_id=test.test_id, question_text=q_text_reverse).first()
                if not existing_reverse:
                    q_reverse = Question(
                        test_id=test.test_id,
                        question_text=q_text_reverse,
                        question_type='translation',
                        correct_answer_text=target.mongolian,
                        explanation=f"'{meaning}' means '{target.mongolian}'."
                    )
                    db.session.add(q_reverse)
            # Don't commit here - let Flask-Admin handle the transaction
        else:
            # Single meaning - create one question
            q_text_reverse = f"Translate {target.english}' to Mongolian"
            existing_reverse = Question.query.filter_by(test_id=test.test_id, question_text=q_text_reverse).first()
            if not existing_reverse:
                q_reverse = Question(
                    test_id=test.test_id,
                    question_text=q_text_reverse,
                    question_type='translation',
                    correct_answer_text=target.mongolian,
                    explanation=f"{target.english} means {target.mongolian}'."
                )
                db.session.add(q_reverse)
                # Don't commit here - let Flask-Admin handle the transaction

        # --- Context-based fill-in-the-blank question (if example_sentence exists) ---
        if target.example_sentence and target.mongolian in target.example_sentence:
            # Create context-based question
            sentence_parts = target.example_sentence.split(target.mongolian,1)
            if len(sentence_parts) == 2:
                before_word = sentence_parts[0].strip()
                after_word = sentence_parts[1].strip()
                q_text_context = f"In the sentence '{target.example_sentence}', what word goes in the blank: '{before_word} ___ {after_word}'"
            else:
                # Fallback to simple replacement if split doesn't work as expected
                q_text_context = target.example_sentence.replace(target.mongolian, "___")
            
            existing_blank = Question.query.filter_by(test_id=test.test_id, question_text=q_text_context).first()
            if not existing_blank:
                q_blank = Question(
                    test_id=test.test_id,
                    question_text=q_text_context,
                    question_type='translation',
                    correct_answer_text=target.mongolian,
                    explanation=f"In the context '{target.example_sentence}', the correct word is '{target.mongolian}'."
                )
                db.session.add(q_blank)
                # Don't commit here - let Flask-Admin handle the transaction

    except Exception as e:
        print(f"Error creating questions for word {target.mongolian}: {e}")  # Don't rollback - let Flask-Admin handle the transaction

# Register the event listener for after_insert on Word
from db.models import Word

event.listen(Word, 'after_insert', create_questions_for_new_word)