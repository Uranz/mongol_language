from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import db
from db.models import Test, Question
from difflib import SequenceMatcher

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
        
        # Handle different question types
        if question.question_type == 'translation':
            # For translation questions, use fuzzy matching
            if question.correct_answer_text and user_answer:
                # Normalize for comparison (lowercase, strip whitespace)
                user_input = user_answer.lower().strip()
                
                # Check if there are multiple correct answers (pipe-separated)
                if '|' in question.correct_answer_text:
                    # Multiple correct answers
                    correct_answers = [ans.strip().lower() for ans in question.correct_answer_text.split('|')]
                    # Check if user's answer matches any of the correct answers
                    is_correct = any(SequenceMatcher(None, expected, user_input).ratio() >= 0.8 
                                   for expected in correct_answers)
                else:
                    # Single correct answer
                    expected = question.correct_answer_text.lower().strip()
                    similarity = SequenceMatcher(None, expected, user_input).ratio()
                    is_correct = similarity >= 0.8  # 80% similarity threshold
            else:
                is_correct = False
        else:
            # For MCQ questions, exact match with correct_answer
            is_correct = user_answer == question.correct_answer
        
        if is_correct:
            score += 1
            
        # Add additional info for multiple meanings
        correct_answers_display = None
        if question.question_type == 'translation' and question.correct_answer_text and '|' in question.correct_answer_text:
            correct_answers_display = [ans.strip() for ans in question.correct_answer_text.split('|')]
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answers': correct_answers_display
        })
    
    return render_template('tests/results.html', 
                         test=test,
                         results=results,
                         score=score,
                         total=total) 