#!/usr/bin/env python3ain utility runner for the Mongolian Language Learning App.
This script provides access to all utility functions from one place.
"""

import sys
import os

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from word_utilities import *
from generate_questions import *
from backup_questions import *

def show_main_menu():
  w the main utility menu"  print("Mongolian Language Learning - Utility Suite)
    print("=" *50print("\nAvailable Utilities:")
    print("1 Word Management (Multiple Meanings)")
    print("2. Question Generation")
    print("3Database Backup")
    print("4)
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice ==1
        show_word_management_menu()
    elif choice == 2     show_question_generation_menu()
    elif choice ==3
        show_backup_menu()
    elif choice == 4:       print("Goodbye!")
        return False
    else:
        print("Invalid choice. Please try again.)  
    return True

def show_word_management_menu():
    """Show word management menu"""
    print(nWord Management Menu)
    print("-" *30
    print("1d/update word with multiple meanings")
    print(2. List all words with multiple meanings")
    print("3. Search word meanings")
    print("4. Create sample words with multiple meanings")
    print("5. Test multiple meanings functionality")
    print("6. Test answer checking")
    print("7. Show word statistics")
    print("8. Back to main menu)
    
    choice = input("\nEnter your choice (1-8): ").strip()
    
    if choice ==1
        mongolian = input("Enter Mongolian word: ).strip()
        meanings_input = input("Enter English meanings (separated by commas): ).strip()
        meanings = [m.strip() for m in meanings_input.split(',')]
        
        part_of_speech = input("Part of speech (optional): ).strip() or None
        example_sentence = input("Example sentence (optional): ).strip() or None
        difficulty = input(Difficulty (beginner/intermediate/advanced, optional): ).strip() or None
        category = input("Category (optional): ).strip() or None
        
        add_multiple_meanings_to_word(mongolian, meanings, part_of_speech, example_sentence, difficulty, category)
        
    elif choice ==2        list_words_with_multiple_meanings()
        
    elif choice ==3
        mongolian = input("Enter Mongolian word to search: ).strip()
        search_word_meanings(mongolian)
        
    elif choice == 4:   print("Creating sample words with multiple meanings...")
        create_sample_multiple_meaning_words()
        print("Sample words created successfully!")
        
    elif choice ==5
        test_multiple_meanings()
        
    elif choice ==6
        mongolian = input("Enter Mongolian word: ).strip()
        answer = input("Enter English answer to test: ).strip()
        test_answer_checking(mongolian, answer)
        
    elif choice ==7
        show_word_statistics()
        
    elif choice == '8:        return
    else:
        print("Invalid choice. Please try again.")

def show_question_generation_menu():
  uestion generation menu"""
    print("\nQuestion Generation Menu)
    print("-" *30print("1. Generate word questions (MCQ)")
    print("2. Generate fill-in-the-blank questions")
    print("3. Generate all question types")
    print("4. Back to main menu)
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        generate_word_questions()
    elif choice == '2':
        generate_fill_in_blank_questions()
    elif choice == '3':
        generate_all_questions()
    elif choice == '4:        return
    else:
        print("Invalid choice. Please try again.")

def show_backup_menu():
ow backup menu"""
    print(nDatabase Backup Menu)
    print("-" *30  print("1. Backup questions table")
    print("2. Backup words table")
    print("3. Backup all tables")
    print("4. Back to main menu)
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1:  backup_questions()
    elif choice == '2      backup_words()
    elif choice == '3        backup_all_tables()
    elif choice == '4:        return
    else:
        print("Invalid choice. Please try again.")

def main():
  Main function   while show_main_menu():
        pass

if __name__ ==__main__":
    # You can also run specific functions from command line
    if len(sys.argv) > 1
        command = sys.argv[1]
        if command == "words":
            show_word_management_menu()
        elif command == "questions":
            show_question_generation_menu()
        elif command == "backup":
            show_backup_menu()
        elif command == "test":
            test_multiple_meanings()
        elif command == "generate":
            generate_all_questions()
        elif command == "backup-all":
            backup_all_tables()
        else:
            print("Usage:")
            print("  python main.py words")
            print("  python main.py questions")
            print("  python main.py backup")
            print("  python main.py test")
            print("  python main.py generate")
            print("  python main.py backup-all")
            print( python main.py  # Interactive menu")
    else:
        main() 