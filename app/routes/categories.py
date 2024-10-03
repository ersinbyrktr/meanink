# app/routes/categories.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Category

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by().all()
    categories_data = [{'id': str(cat.id), 'name': cat.name} for cat in categories]
    return jsonify(categories_data), 200


@categories_bp.route('/', methods=['POST'])
def create_category():
    name = request.json.get('name')
    if not name:
        return jsonify({'msg': 'Category name is required'}), 400

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({'msg': 'Category created', 'id': str(category.id)}), 201


@categories_bp.route('/<uuid:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'msg': 'Category not found'}), 404

    name = request.json.get('name', category.name)
    category.name = name
    db.session.commit()

    return jsonify({'msg': 'Category updated'}), 200


@categories_bp.route('/<uuid:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({'msg': 'Category not found'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({'msg': 'Category deleted'}), 200
