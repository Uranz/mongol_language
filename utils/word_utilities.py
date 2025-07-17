from db import db
from db.models import Word, Question, Test
from app import app

def create_questions_for_word(mongolian_word, meanings_list, part_of_speech=None, example_sentence=None):
    with app.app_context():
        word = Word.query.filter_by(mongolian=mongolian_word).first()
        test = Test.query.first()
        if not word or not test:
            print("Word or test not found")
            return
        # Mongolian to English
        q_text = f"Translate '{word.mongolian}' to English"
        existing = Question.query.filter_by(test_id=test.test_id, question_text=q_text).first()
        if not existing:
            correct_answers = word.english
            if '|' in word.english:
                meanings = [m.strip() for m in word.english.split('|')]
                explanation = f"'{word.mongolian}' can mean: {', '.join(meanings)}"
            else:
                explanation = f"'{word.mongolian}' means '{word.english}'."
            q = Question(
                test_id=test.test_id,
                question_text=q_text,
                question_type='translation',
                correct_answer_text=correct_answers,
                explanation=explanation
            )
            db.session.add(q)
            db.session.commit()
        # English to Mongolian
        if '|' in word.english:
            meanings = [m.strip() for m in word.english.split('|')]
            for meaning in meanings:
                q_text_reverse = f"Translate '{meaning}' to Mongolian"
                existing_reverse = Question.query.filter_by(test_id=test.test_id, question_text=q_text_reverse).first()
                if not existing_reverse:
                    q_reverse = Question(
                        test_id=test.test_id,
                        question_text=q_text_reverse,
                        question_type='translation',
                        correct_answer_text=word.mongolian,
                        explanation=f"'{meaning}' means '{word.mongolian}'."
                    )
                    db.session.add(q_reverse)
            db.session.commit()
        else:
            q_text_reverse = f"Translate '{word.english}' to Mongolian"
            existing_reverse = Question.query.filter_by(test_id=test.test_id, question_text=q_text_reverse).first()
            if not existing_reverse:
                q_reverse = Question(
                    test_id=test.test_id,
                    question_text=q_text_reverse,
                    question_type='translation',
                    correct_answer_text=word.mongolian,
                    explanation=f"'{word.english}' means '{word.mongolian}'."
                )
                db.session.add(q_reverse)
                db.session.commit()
        # Context-based
        if word.example_sentence and word.mongolian in word.example_sentence:
            sentence_parts = word.example_sentence.split(word.mongolian, 1)
            if len(sentence_parts) == 2:
                before_word = sentence_parts[0].strip()
                after_word = sentence_parts[1].strip()
                q_text_context = f"In the sentence '{word.example_sentence}', what word goes in the blank: '{before_word} ___ {after_word}'"
            else:
                q_text_context = word.example_sentence.replace(word.mongolian, "___")
            existing_blank = Question.query.filter_by(test_id=test.test_id, question_text=q_text_context).first()
            if not existing_blank:
                q_blank = Question(
                    test_id=test.test_id,
                    question_text=q_text_context,
                    question_type='translation',
                    correct_answer_text=word.mongolian,
                    explanation=f"In the context '{word.example_sentence}', the correct word is '{word.mongolian}'."
                )
                db.session.add(q_blank)
                db.session.commit()

def add_multiple_meanings_to_word(mongolian_word, meanings_list, part_of_speech=None, example_sentence=None, difficulty=None, category=None):
    with app.app_context():
        try:
            existing_word = Word.query.filter_by(mongolian=mongolian_word).first()
            if existing_word:
                print(f"Updating existing word: {mongolian_word}")
                existing_word.english = '|'.join(meanings_list)
                if part_of_speech:
                    existing_word.part_of_speech = part_of_speech
                if example_sentence:
                    existing_word.example_sentence = example_sentence
                if difficulty:
                    existing_word.difficulty = difficulty
                if category:
                    existing_word.category = category
                db.session.commit()
                test = Test.query.first()
                if test:
                    existing_questions = Question.query.filter_by(test_id=test.test_id).filter(
                        Question.question_text.contains(mongolian_word)
                    ).all()
                    for q in existing_questions:
                        db.session.delete(q)
                    db.session.commit()
                create_questions_for_word(mongolian_word, meanings_list, part_of_speech, example_sentence)
            else:
                print(f"Creating new word: {mongolian_word}")
                new_word = Word(
                    mongolian=mongolian_word,
                    english='|'.join(meanings_list),
                    part_of_speech=part_of_speech,
                    example_sentence=example_sentence,
                    difficulty=difficulty,
                    category=category
                )
                db.session.add(new_word)
                db.session.commit()
                create_questions_for_word(mongolian_word, meanings_list, part_of_speech, example_sentence)
            print(f"Successfully processed: {mongolian_word} -> {', '.join(meanings_list)}")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback() 