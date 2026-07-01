from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

budget_bp = Blueprint('budgets', __name__)

def get_user_id():
    return int(get_jwt_identity())

@budget_bp.route('', methods=['GET'])
@jwt_required()
def get_budgets():
    user_id = get_user_id()
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.id, b.amount as budget_amount, b.month, b.year,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon,
                   COALESCE(SUM(t.amount), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON t.user_id = b.user_id
                AND t.category_id = b.category_id
                AND t.type = 'expense'
                AND MONTH(t.transaction_date) = b.month
                AND YEAR(t.transaction_date) = b.year
            WHERE b.user_id = %s AND b.month = %s AND b.year = %s
            GROUP BY b.id, b.amount, b.month, b.year,
                     c.id, c.name, c.color, c.icon
            ORDER BY c.name
        """, (user_id, month, year))

        budgets = cursor.fetchall()
        for b in budgets:
            b['budget_amount'] = float(b['budget_amount'])
            b['spent'] = float(b['spent'])
            b['remaining'] = b['budget_amount'] - b['spent']
            b['percentage'] = round((b['spent'] / b['budget_amount']) * 100, 1) if b['budget_amount'] > 0 else 0

        return jsonify(budgets), 200
    finally:
        cursor.close()
        conn.close()

@budget_bp.route('', methods=['POST'])
@jwt_required()
def create_budget():
    user_id = get_user_id()
    data = request.get_json()

    category_id = data.get('category_id')
    amount = data.get('amount')
    month = data.get('month', datetime.now().month)
    year = data.get('year', datetime.now().year)

    if not category_id or not amount:
        return jsonify({'error': 'Vui lòng chọn danh mục và nhập số tiền'}), 400

    if float(amount) <= 0:
        return jsonify({'error': 'Số tiền phải lớn hơn 0'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Verify category
        cursor.execute(
            "SELECT id, type FROM categories WHERE id = %s AND user_id = %s",
            (category_id, user_id)
        )
        category = cursor.fetchone()
        if not category or category['type'] != 'expense':
            return jsonify({'error': 'Danh mục không hợp lệ'}), 400

        # Upsert: insert or update
        cursor.execute("""
            INSERT INTO budgets (user_id, category_id, amount, month, year)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE amount = VALUES(amount)
        """, (user_id, category_id, amount, month, year))
        conn.commit()

        budget_id = cursor.lastrowid
        cursor.execute("""
            SELECT b.id, b.amount as budget_amount, b.month, b.year,
                   c.id as category_id, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.id = %s
        """, (budget_id,))
        budget = cursor.fetchone()
        budget['budget_amount'] = float(budget['budget_amount'])

        return jsonify(budget), 201
    finally:
        cursor.close()
        conn.close()

@budget_bp.route('/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    user_id = get_user_id()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE id = %s AND user_id = %s", (budget_id, user_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Không tìm thấy ngân sách'}), 404
        conn.commit()
        return jsonify({'message': 'Đã xóa ngân sách thành công'}), 200
    finally:
        cursor.close()
        conn.close()
