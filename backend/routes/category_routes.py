from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity

category_bp = Blueprint('categories', __name__)

def get_user_id():
    return int(get_jwt_identity())

@category_bp.route('', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_user_id()
    type_filter = request.args.get('type')

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, type, color, icon, is_default FROM categories WHERE user_id = %s"
        params = [user_id]

        if type_filter:
            query += " AND type = %s"
            params.append(type_filter)

        query += " ORDER BY type, name"
        cursor.execute(query, params)
        categories = cursor.fetchall()
        return jsonify(categories), 200
    finally:
        cursor.close()
        conn.close()

@category_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    user_id = get_user_id()
    data = request.get_json()

    name = data.get('name', '').strip()
    type_ = data.get('type')
    color = data.get('color', '#6B7280')
    icon = data.get('icon', '📌')

    if not name or not type_:
        return jsonify({'error': 'Vui lòng điền tên và loại danh mục'}), 400

    if type_ not in ('income', 'expense'):
        return jsonify({'error': 'Loại danh mục không hợp lệ'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM categories WHERE user_id = %s AND name = %s AND type = %s",
            (user_id, name, type_)
        )
        if cursor.fetchone():
            return jsonify({'error': 'Danh mục này đã tồn tại'}), 400

        cursor.execute(
            "INSERT INTO categories (user_id, name, type, color, icon) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, type_, color, icon)
        )
        category_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            "SELECT id, name, type, color, icon, is_default FROM categories WHERE id = %s",
            (category_id,)
        )
        category = cursor.fetchone()
        return jsonify(category), 201
    finally:
        cursor.close()
        conn.close()

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    user_id = get_user_id()
    data = request.get_json()

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM categories WHERE id = %s AND user_id = %s",
            (category_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Không tìm thấy danh mục'}), 404

        updates = []
        params = []

        if 'name' in data:
            updates.append("name = %s")
            params.append(data['name'].strip())
        if 'color' in data:
            updates.append("color = %s")
            params.append(data['color'])
        if 'icon' in data:
            updates.append("icon = %s")
            params.append(data['icon'])

        if not updates:
            return jsonify({'error': 'Không có dữ liệu để cập nhật'}), 400

        params.extend([category_id, user_id])
        cursor.execute(f"UPDATE categories SET {', '.join(updates)} WHERE id = %s AND user_id = %s", params)
        conn.commit()

        cursor.execute(
            "SELECT id, name, type, color, icon, is_default FROM categories WHERE id = %s",
            (category_id,)
        )
        category = cursor.fetchone()
        return jsonify(category), 200
    finally:
        cursor.close()
        conn.close()

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user_id = get_user_id()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT is_default FROM categories WHERE id = %s AND user_id = %s",
            (category_id, user_id)
        )
        cat = cursor.fetchone()
        if not cat:
            return jsonify({'error': 'Không tìm thấy danh mục'}), 404
        if cat['is_default']:
            return jsonify({'error': 'Không thể xóa danh mục mặc định'}), 400

        cursor.execute("DELETE FROM categories WHERE id = %s AND user_id = %s", (category_id, user_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Không tìm thấy danh mục'}), 404
        conn.commit()
        return jsonify({'message': 'Đã xóa danh mục thành công'}), 200
    finally:
        cursor.close()
        conn.close()
