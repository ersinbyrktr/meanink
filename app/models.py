# app/models.py
import uuid
from datetime import datetime, UTC

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID

from app import db


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), nullable=False)


class Embedding(db.Model):
    __tablename__ = 'embeddings'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = db.Column(UUID(as_uuid=True), db.ForeignKey('notes.id'), nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), nullable=True, default=uuid.uuid4)
    content_chunk = db.Column(db.Text, nullable=False)
    vector = db.Column(Vector(1536), nullable=False)  # Assuming 1536 dimensions for OpenAI embeddings
    metadata_json = db.Column(JSONB, default={})

    __table_args__ = (
        Index('ix_embedding_vector', 'vector', postgresql_using='ivfflat'),
    )


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=True)
    title: str = db.Column(db.String(255))
    content: str = db.Column(db.Text)  # Markdown content
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(UTC))
    embeddings = db.relationship('Embedding', backref='note', lazy=True)
    tags = db.relationship('Tag', secondary='note_tags', backref=db.backref('notes', lazy='dynamic'))
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=True)


class NoteTag(db.Model):
    __tablename__ = 'note_tags'
    note_id = db.Column(UUID(as_uuid=True), db.ForeignKey('notes.id'), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tags.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(UTC))


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    notes = db.relationship('Note', backref='category', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(UTC))
