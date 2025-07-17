import csv
import sqlite3
from datetime import datetime

def backup_questions():
    "up questions table to CSV file
    conn = sqlite3.connect('instance/test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'questions_backup_{timestamp}.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)

    conn.close()
    print(f"Backup complete! Saved as {filename}")

def backup_words():
 Backup words table to CSV file
    conn = sqlite3.connect('instance/test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'words_backup_{timestamp}.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)

    conn.close()
    print(f"Backup complete! Saved as {filename}")

def backup_all_tables():ckup all important tables"bles = ['questions', 'words', 'tests', 'users']
    
    for table in tables:
        try:
            conn = sqlite3.connect('instance/test.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]

            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{table}_backup_{timestamp}.csv'

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(column_names)
                writer.writerows(rows)

            conn.close()
            print(f"Backup complete for {table}! Saved as {filename}")
        except Exception as e:
            print(f"Error backing up {table}: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "questions":
            backup_questions()
        elif command == "words":
            backup_words()
        elif command == "all":
            backup_all_tables()
        else:
            print("Usage:")
            print("  python backup_questions.py questions")
            print("  python backup_questions.py words")
            print("  python backup_questions.py all")
    else:
        # Default to backing up questions
        backup_questions() 