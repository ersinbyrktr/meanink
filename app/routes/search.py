# app/routes/search.py
import openai
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['POST'])
@jwt_required()
def search_notes():
    user_id = get_jwt_identity()
    query = request.json.get('query')
    if not query:
        return jsonify({'msg': 'Query is required'}), 400

    # Generate embedding for the query
    response = openai.Embedding.create(
        input=query,
        engine='text-embedding-ada-002'
    )
    query_vector = response['data'][0]['embedding']

    # Perform similarity search using pgvector
    sql = """
    SELECT embeddings.note_id, embeddings.content_chunk, embeddings.chunk_index,
           1 - (embeddings.embedding <=> cube(%s)) AS similarity
    FROM embeddings
    JOIN notes ON embeddings.note_id = notes.id
    WHERE notes.user_id = %s
    ORDER BY embeddings.embedding <=> cube(%s) LIMIT 10;
    """
    params = [query_vector, user_id, query_vector]
    result = db.session.execute(sql, params)

    search_results = []
    for row in result:
        search_results.append({
            'note_id': str(row[0]),
            'content_chunk': row[1],
            'chunk_index': row[2],
            'similarity': row[3]
        })
    return jsonify(search_results), 200
