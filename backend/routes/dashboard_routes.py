from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

def get_user_id():
    return int(get_jwt_identity())

@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    user_id = get_user_id()
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Total income and expense for the month
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
            FROM transactions
            WHERE user_id = %s AND MONTH(transaction_date) = %s AND YEAR(transaction_date) = %s
        """, (user_id, month, year))
        monthly = cursor.fetchone()
        monthly['total_income'] = float(monthly['total_income'])
        monthly['total_expense'] = float(monthly['total_expense'])
        monthly['balance'] = monthly['total_income'] - monthly['total_expense']

        # Total balance (all time)
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0) as balance
            FROM transactions
            WHERE user_id = %s
        """, (user_id,))
        total_balance_row = cursor.fetchone()
        total_balance = float(total_balance_row['balance'])

        # Monthly chart data (last 6 months)
        cursor.execute("""
            SELECT
                MONTH(transaction_date) as month,
                YEAR(transaction_date) as year,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as expense
            FROM transactions
            WHERE user_id = %s
            AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY YEAR(transaction_date), MONTH(transaction_date)
            ORDER BY year, month
        """, (user_id,))
        monthly_chart = cursor.fetchall()
        for m in monthly_chart:
            m['income'] = float(m['income'])
            m['expense'] = float(m['expense'])

        # Category breakdown for current month (expenses only)
        cursor.execute("""
            SELECT c.name, c.color, c.icon, COALESCE(SUM(t.amount), 0) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s AND t.type = 'expense'
            AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s
            GROUP BY c.id, c.name, c.color, c.icon
            ORDER BY total DESC
        """, (user_id, month, year))
        category_breakdown = cursor.fetchall()
        for c in category_breakdown:
            c['total'] = float(c['total'])

        # Recent transactions (last 5)
        cursor.execute("""
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date,
                   c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT 5
        """, (user_id,))
        recent = cursor.fetchall()
        for r in recent:
            r['amount'] = float(r['amount'])
            if hasattr(r['transaction_date'], 'isoformat'):
                r['transaction_date'] = r['transaction_date'].isoformat()

        return jsonify({
            'total_balance': total_balance,
            'monthly': monthly,
            'monthly_chart': monthly_chart,
            'category_breakdown': category_breakdown,
            'recent_transactions': recent
        }), 200

    finally:
        cursor.close()
        conn.close()
