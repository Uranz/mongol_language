from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import db
from db.models import Test, Question

test_bp = Blueprint('test_routes', __name__)

@test_bp.route('/tests')
@login_required
def list_tests():
    tests = Test.query.all()
    return render_template('tests/list.html', tests=tests)

@test_bp.route('/test/<int:test_id>')
@login_required
def take_test(test_id):
    test = Test.query.get_or_404(test_id)
    questions = Question.query.filter_by(test_id=test_id).all()
    return render_template('tests/take.html', test=test, questions=questions)

@test_bp.route('/submit', methods=['POST'])
@login_required
def submit_test():
    test_id = request.form.get('test_id')
    test = Test.query.get_or_404(test_id)
    questions = Question.query.filter_by(test_id=test_id).all()
    
    # Process answers and calculate score
    score = 0
    total = len(questions)
    results = []
    
    for question in questions:
        user_answer = request.form.get(f'question_{question.question_id}')
        is_correct = user_answer == question.correct_answer
        if is_correct:
            score += 1
            
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    
    return render_template('tests/results.html', 
                         test=test,
                         results=results,
                         score=score,
                         total=total) 