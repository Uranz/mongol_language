# Utils Package

This folder contains utility scripts for the Mongolian Language Learning App.

## Files

### `word_utilities.py`
Multiple meanings management for Mongolian words.
- Add/update words with multiple meanings
- Search and list words
- Test answer checking
- Word statistics

### `generate_questions.py`
Question generation utilities.
- Generate MCQ questions
- Generate fill-in-the-blank questions
- Generate all question types

### `backup_questions.py`
Database backup utilities.
- Backup questions table
- Backup words table
- Backup all tables with timestamps

### `main.py`
Main utility runner with interactive menus.

## Usage

### Interactive Mode
```bash
# Run from the root directory
python utils/main.py

# Or run individual utilities
python utils/word_utilities.py
python utils/generate_questions.py
python utils/backup_questions.py
```

### Command Line Mode
```bash
# Word management
python utils/main.py words
python utils/word_utilities.py test
python utils/word_utilities.py stats

# Question generation
python utils/main.py questions
python utils/generate_questions.py

# Database backup
python utils/main.py backup
python utils/backup_questions.py all
```

### Import in Python
```python
from utils.word_utilities import add_multiple_meanings_to_word
from utils.generate_questions import generate_all_questions
from utils.backup_questions import backup_all_tables
```

## Features

- **Multiple Meanings**: Handle words with multiple English translations
- **Question Generation**: Auto-generate various question types
- **Database Backup**: Timestamped CSV backups
- **Interactive Menus**: User-friendly command-line interface
- **Command Line**: Direct function calls for automation 