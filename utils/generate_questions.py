import random
from db import db
from db.models import Word, Question, Test

def generate_word_questions():
    # Get the first test (or create one if none exists)
    test = Test.query.first()
    if not test:
        test = Test(title="Auto-generated Vocabulary Test", is_sample=True)
        db.session.add(test)
        db.session.commit()

    words = Word.query.all()
    if len(words) < 4:
        print("Not enough words to generate questions (need at least 4).")
    else:
        for word in words:
            # Get3random distractors (other words)
            distractors = [w.english for w in Word.query.filter(Word.id != word.id).order_by(db.func.random()).limit(3)]
            options = distractors + [word.english]
            random.shuffle(options)
            correct_answer = chr(options.index(word.english) + ord('A'))  #A,Br D           # Check if a question for this word already exists to avoid duplicates
            existing = Question.query.filter_by(test_id=test.test_id, question_text=f"What is the English translation of {word.mongolian}'?").first()
            if existing:
                continue

            q = Question(
                test_id=test.test_id,
                question_text=f"What is the English translation of {word.mongolian}'?",
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                option_e="",
                correct_answer=correct_answer,
                explanation=f"{word.mongolian}' means '{word.english}."     )
            db.session.add(q)

        db.session.commit()
        print("Multiple-choice translation questions generated and added to the test!)
def generate_fill_in_blank_questions():
    # Get or create a test
    test = Test.query.first()
    if not test:
        test = Test(title="Auto-generated Fill-in-the-Blank Test", is_sample=True)
        db.session.add(test)
        db.session.commit()

    words = Word.query.filter(Word.example_sentence != None).all()
    if len(words) < 4:
        print("Not enough words with example sentences to generate questions (need at least 4).")
        return

    for word in words:
        sentence = word.example_sentence
        if not sentence or word.mongolian not in sentence:
            continue  # Skip if no example or word not in sentence

        # Create the fill-in-the-blank sentence
        blank_sentence = sentence.replace(word.mongolian, "___", 1)

        # Prepare distractors
        distractors = [w.mongolian for w in Word.query.filter(Word.id != word.id).order_by(db.func.random()).limit(3)]
        options = distractors + [word.mongolian]
        random.shuffle(options)
        correct_answer = chr(options.index(word.mongolian) + ord('A'))  #A,B, or 'D# Avoid duplicates
        existing = Question.query.filter_by(
            test_id=test.test_id,
            question_text=blank_sentence
        ).first()
        if existing:
            continue

        q = Question(
            test_id=test.test_id,
            question_text=blank_sentence,
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            option_e="",
            correct_answer=correct_answer,
            explanation=f"The correct word is {word.mongolian}'."
        )
        db.session.add(q)

    db.session.commit()
    print(Fill-in-the-blank questions generated and added to the test!")

def generate_all_questions():
    generate_word_questions()
    generate_fill_in_blank_questions()
    print("All question types generated!") 