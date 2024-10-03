import os
from typing import List
from uuid import uuid4

from app import db
from app.models import Note


def note_from_files(folder_path, user_id):
    notes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            title = filename[:-4]  # Remove the .txt extension to get the title
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                new_note = Note(
                    user_id=user_id,
                    title=title,
                    content=file.read()
                )
                notes.append(new_note)
    return notes


def store_notes(notes: List[Note]):
    db.session.add_all(notes)


def init_notes():
    notes = note_from_files('notepad_data', uuid4())
    store_notes(notes)
