from flask import Blueprint, redirect, url_for, render_template, request, abort
from markupsafe import Markup
from db.models import Lesson, Word
from jinja2 import Template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html')

@main_bp.route('/lesson/<int:lesson_id>')
def lesson_view(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    words = []
    # If the lesson is a flashcard type and uses dynamic data, fetch words by category
    if lesson.lesson_type == 'flashcard':
        # Try to infer category from title or content, fallback to all words
        # For now, use 'greeting' for the Basic Greetings lesson
        if 'greeting' in lesson.title.lower():
            words = Word.query.filter_by(category='greeting').all()
        else:
            words = Word.query.all()
    # Render the lesson content as a Jinja2 template string
    
    rendered_content = Template(lesson.content).render(words=words)
    return render_template('lesson.html', lesson=lesson, rendered_content=Markup(rendered_content)) 

@main_bp.route('/lessons')
def lessons_list():
    lessons = Lesson.query.all()
    return render_template('lessons/list.html', lessons=lessons) 