from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

transaction_bp = Blueprint('transactions', __name__)

def get_user_id():
    return int(get_jwt_identity())

@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    user_id = get_user_id()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date, t.created_at,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = %s AND t.user_id = %s
        """, (transaction_id, user_id))
        transaction = cursor.fetchone()
        if not transaction:
            return jsonify({'error': 'Không tìm thấy giao dịch'}), 404

        if isinstance(transaction['transaction_date'], (date, datetime)):
            transaction['transaction_date'] = transaction['transaction_date'].isoformat()
        if isinstance(transaction['created_at'], (date, datetime)):
            transaction['created_at'] = transaction['created_at'].isoformat()
        transaction['amount'] = float(transaction['amount'])

        return jsonify(transaction), 200
    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_user_id()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page

        # Filters
        type_filter = request.args.get('type')
        category_id = request.args.get('category_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        search = request.args.get('search', '').strip()

        query = """
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date, t.created_at,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s
        """
        params = [user_id]
        count_query = "SELECT COUNT(*) as total FROM transactions t WHERE t.user_id = %s"
        count_params = [user_id]

        if type_filter:
            query += " AND t.type = %s"
            params.append(type_filter)
            count_query += " AND t.type = %s"
            count_params.append(type_filter)

        if category_id:
            query += " AND t.category_id = %s"
            params.append(category_id)
            count_query += " AND t.category_id = %s"
            count_params.append(category_id)

        if start_date:
            query += " AND t.transaction_date >= %s"
            params.append(start_date)
            count_query += " AND t.transaction_date >= %s"
            count_params.append(start_date)

        if end_date:
            query += " AND t.transaction_date <= %s"
            params.append(end_date)
            count_query += " AND t.transaction_date <= %s"
            count_params.append(end_date)

        if month and year:
            query += " AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s"
            params.extend([month, year])
            count_query += " AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s"
            count_params.extend([month, year])
        elif year:
            query += " AND YEAR(t.transaction_date) = %s"
            params.append(year)
            count_query += " AND YEAR(t.transaction_date) = %s"
            count_params.append(year)

        if search:
            query += " AND t.description LIKE %s"
            params.append(f'%{search}%')
            count_query += " AND t.description LIKE %s"
            count_params.append(f'%{search}%')

        query += " ORDER BY t.transaction_date DESC, t.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        # Get total count
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        # Format dates
        for t in transactions:
            if isinstance(t['transaction_date'], (date, datetime)):
                t['transaction_date'] = t['transaction_date'].isoformat()
            if isinstance(t['created_at'], (date, datetime)):
                t['created_at'] = t['created_at'].isoformat()
            t['amount'] = float(t['amount'])

        return jsonify({
            'transactions': transactions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        }), 200

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    user_id = get_user_id()
    data = request.get_json()

    category_id = data.get('category_id')
    amount = data.get('amount')
    type_ = data.get('type')
    description = data.get('description', '').strip()
    transaction_date = data.get('transaction_date')

    if not category_id or not amount or not type_ or not transaction_date:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400

    if type_ not in ('income', 'expense'):
        return jsonify({'error': 'Loại giao dịch không hợp lệ'}), 400

    if float(amount) <= 0:
        return jsonify({'error': 'Số tiền phải lớn hơn 0'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Verify category belongs to user
        cursor.execute(
            "SELECT id, type FROM categories WHERE id = %s AND user_id = %s",
            (category_id, user_id)
        )
        category = cursor.fetchone()
        if not category:
            return jsonify({'error': 'Danh mục không hợp lệ'}), 400

        if category['type'] != type_:
            return jsonify({'error': 'Loại giao dịch không khớp với danh mục'}), 400

        cursor.execute(
            """INSERT INTO transactions (user_id, category_id, amount, type, description, transaction_date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, category_id, amount, type_, description, transaction_date)
        )
        transaction_id = cursor.lastrowid
        conn.commit()

        # Return the created transaction with category info
        cursor.execute("""
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date, t.created_at,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = %s
        """, (transaction_id,))
        transaction = cursor.fetchone()
        if isinstance(transaction['transaction_date'], (date, datetime)):
            transaction['transaction_date'] = transaction['transaction_date'].isoformat()
        if isinstance(transaction['created_at'], (date, datetime)):
            transaction['created_at'] = transaction['created_at'].isoformat()
        transaction['amount'] = float(transaction['amount'])

        return jsonify(transaction), 201

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    user_id = get_user_id()
    data = request.get_json()

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Verify ownership
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Không tìm thấy giao dịch'}), 404

        # Build update query dynamically
        updates = []
        params = []

        if 'category_id' in data:
            # Verify new category
            cursor.execute(
                "SELECT id, type FROM categories WHERE id = %s AND user_id = %s",
                (data['category_id'], user_id)
            )
            cat = cursor.fetchone()
            if not cat:
                return jsonify({'error': 'Danh mục không hợp lệ'}), 400
            updates.append("category_id = %s")
            params.append(data['category_id'])
            if 'type' in data:
                updates.append("type = %s")
                params.append(data['type'])
                if cat['type'] != data['type']:
                    return jsonify({'error': 'Loại giao dịch không khớp với danh mục'}), 400

        if 'amount' in data:
            if float(data['amount']) <= 0:
                return jsonify({'error': 'Số tiền phải lớn hơn 0'}), 400
            updates.append("amount = %s")
            params.append(data['amount'])

        if 'description' in data:
            updates.append("description = %s")
            params.append(data['description'].strip())

        if 'transaction_date' in data:
            updates.append("transaction_date = %s")
            params.append(data['transaction_date'])

        if not updates:
            return jsonify({'error': 'Không có dữ liệu để cập nhật'}), 400

        params.extend([transaction_id, user_id])
        cursor.execute(f"UPDATE transactions SET {', '.join(updates)} WHERE id = %s AND user_id = %s", params)
        conn.commit()

        # Return updated transaction
        cursor.execute("""
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date, t.created_at,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = %s
        """, (transaction_id,))
        transaction = cursor.fetchone()
        if isinstance(transaction['transaction_date'], (date, datetime)):
            transaction['transaction_date'] = transaction['transaction_date'].isoformat()
        if isinstance(transaction['created_at'], (date, datetime)):
            transaction['created_at'] = transaction['created_at'].isoformat()
        transaction['amount'] = float(transaction['amount'])

        return jsonify(transaction), 200

    finally:
        cursor.close()
        conn.close()

@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    user_id = get_user_id()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, user_id)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'Không tìm thấy giao dịch'}), 404
        conn.commit()
        return jsonify({'message': 'Đã xóa giao dịch thành công'}), 200
    finally:
        cursor.close()
        conn.close()
