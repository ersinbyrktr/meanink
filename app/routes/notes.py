# app/routes/notes.py
from flask import Blueprint, request, jsonify

from app import db
from app.models import Note, Embedding, Tag
from app.services.embedding_service import generate_note_embeddings

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/', methods=['GET'])
def get_notes():
    notes = Note.query.filter_by().all()
    notes_data = []
    for note in notes:
        notes_data.append({
            'id': str(note.id),
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
            'tags': [tag.name for tag in note.tags],
            'category': note.category.name if note.category else None
        })
    return jsonify(notes_data), 200


@notes_bp.route('/', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags = data.get('tags', [])
    category_id = data.get('category_id')

    note = Note(
        title=title,
        content=content,
        category_id=category_id
    )
    db.session.add(note)
    db.session.commit()

    # Handle tags
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        note.tags.append(tag)
    db.session.commit()

    # Generate embeddings
    generate_note_embeddings(note)

    return jsonify({'msg': 'Note created successfully', 'note_id': str(note.id)}), 201


@notes_bp.route('/<uuid:note_id>', methods=['GET'])
def get_note_by_id(note_id):
    note = Note.query.filter_by(id=note_id).first()
    if note:
        note_data = {
            'id': str(note.id),
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
            'tags': [tag.name for tag in note.tags],
            'category': note.category.name if note.category else None
        }
        return jsonify(note_data), 200
    else:
        return jsonify({'msg': 'Note not found'}), 404


@notes_bp.route('/<uuid:note_id>', methods=['PUT'])
def update_note(note_id):
    note = Note.query.filter_by(id=note_id).first()
    if not note:
        return jsonify({'msg': 'Note not found'}), 404

    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.category_id = data.get('category_id', note.category_id)

    # Handle tags
    tags = data.get('tags', [])
    note.tags.clear()
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        note.tags.append(tag)
    db.session.commit()

    # Regenerate embeddings
    generate_note_embeddings(note)

    return jsonify({'msg': 'Note updated successfully'}), 200


@notes_bp.route('/<uuid:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id).first()
    if not note:
        return jsonify({'msg': 'Note not found'}), 404

    # Delete embeddings
    Embedding.query.filter_by(note_id=note.id).delete()
    db.session.delete(note)
    db.session.commit()

    return jsonify({'msg': 'Note deleted successfully'}), 200
