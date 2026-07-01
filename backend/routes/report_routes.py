from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import csv
import io

report_bp = Blueprint('reports', __name__)

def get_user_id():
    return int(get_jwt_identity())

@report_bp.route('/monthly', methods=['GET'])
@jwt_required()
def get_monthly_report():
    user_id = get_user_id()
    year = request.args.get('year', datetime.now().year, type=int)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                MONTH(transaction_date) as month,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as expense
            FROM transactions
            WHERE user_id = %s AND YEAR(transaction_date) = %s
            GROUP BY MONTH(transaction_date)
            ORDER BY month
        """, (user_id, year))
        report = cursor.fetchall()
        for r in report:
            r['income'] = float(r['income'])
            r['expense'] = float(r['expense'])
            r['balance'] = r['income'] - r['expense']

        return jsonify({'year': year, 'data': report}), 200
    finally:
        cursor.close()
        conn.close()

@report_bp.route('/category', methods=['GET'])
@jwt_required()
def get_category_report():
    user_id = get_user_id()
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    type_ = request.args.get('type', 'expense')

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.name, c.color, c.icon, COALESCE(SUM(t.amount), 0) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s AND t.type = %s
            AND MONTH(t.transaction_date) = %s AND YEAR(t.transaction_date) = %s
            GROUP BY c.id, c.name, c.color, c.icon
            ORDER BY total DESC
        """, (user_id, type_, month, year))
        report = cursor.fetchall()
        for r in report:
            r['total'] = float(r['total'])

        return jsonify({'month': month, 'year': year, 'type': type_, 'data': report}), 200
    finally:
        cursor.close()
        conn.close()

@report_bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_csv():
    user_id = get_user_id()
    type_filter = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT t.amount, t.type, t.description, t.transaction_date,
                   c.name as category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s
        """
        params = [user_id]

        if type_filter:
            query += " AND t.type = %s"
            params.append(type_filter)
        if start_date:
            query += " AND t.transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t.transaction_date <= %s"
            params.append(end_date)

        query += " ORDER BY t.transaction_date DESC"
        cursor.execute(query, params)
        transactions = cursor.fetchall()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ngày', 'Loại', 'Danh mục', 'Số tiền', 'Mô tả'])
        for t in transactions:
            date_str = t['transaction_date'].isoformat() if hasattr(t['transaction_date'], 'isoformat') else str(t['transaction_date'])
            writer.writerow([
                date_str,
                'Thu nhập' if t['type'] == 'income' else 'Chi tiêu',
                t['category_name'],
                f"{t['amount']:,.2f}",
                t['description'] or ''
            ])

        output.seek(0)
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=transactions_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    finally:
        cursor.close()
        conn.close()
