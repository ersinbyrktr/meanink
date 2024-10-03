# app/services/embedding_service.py
import os
import uuid as uid

import nltk
import openai
from llama_index.core import Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import Document

from app import db
from app.models import Embedding, Note

openai.api_key = os.getenv('OPENAI_API_KEY')
nltk.download('punkt')
nltk.download('punkt_tab')


def generate_note_embeddings(note: Note):
    # Delete existing embeddings for the note
    _delete_node_by_id(note)

    root_embedding_vector = Settings.embed_model.get_text_embedding(note.content)

    root_embedding = Embedding(
        id=uid.uuid4(),
        note_id=note.id,
        content_chunk=note.content,
        embedding=root_embedding_vector,
        metadata_json={
            'title': note.title,
            'created_at': note.created_at.isoformat()
        }
    )
    db.session.add(root_embedding)

    # Split content into sentences and paragraphs
    parent_nodes = parse_parent_nodes(note.content)

    # For each parent node, create leaf nodes (sentences)
    for parent_node in parent_nodes:
        # Split parent node text into sentences
        parent_embedding = Embedding(
            id=uid.uuid4(),
            note_id=note.id,
            parent_id=root_embedding.id,
            content_chunk=parent_node.content,
            embedding=parent_node.embedding,
            metadata_json=root_embedding.metadata_json
        )
        db.session.add(parent_embedding)
        sentences = nltk.sent_tokenize(parent_node.get_text())
        for child_content in sentences:
            child_embedding_vector = Settings.embed_model.get_text_embedding(child_content)
            child_embedding = Embedding(
                id=uid.uuid4(),
                note_id=note.id,
                parent_id=parent_embedding.id,
                content_chunk=child_content,
                embedding=child_embedding_vector,
                metadata_json=parent_embedding.metadata_json
            )
            db.session.add(child_embedding)
    db.session.commit()


def _delete_node_by_id(note):
    Embedding.query.filter_by(note_id=note.id).delete()
    db.session.commit()


def parse_parent_nodes(content: str):
    # Read documents from the directory
    doc = Document(text=content)
    # Create parent nodes with larger chunk size
    parent_parser = SimpleNodeParser(chunk_size=256, chunk_overlap=50)
    parent_nodes = parent_parser.get_nodes_from_documents([doc])
    return parent_nodes
