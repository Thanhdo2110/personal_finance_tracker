from flask import Blueprint, request, jsonify
from database import get_db_connection
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from mysql.connector import Error
import re

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({'error': 'Dữ liệu đăng ký không hợp lệ'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400

    if len(username) < 3 or len(username) > 30:
        return jsonify({'error': 'Tên đăng nhập phải từ 3-30 ký tự'}), 400

    if not is_valid_email(email):
        return jsonify({'error': 'Email không hợp lệ'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({'error': 'Tên đăng nhập hoặc email đã tồn tại'}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Create default categories for new user
        default_categories = [
            (user_id, 'Lương', 'income', '#10B981', '💰'),
            (user_id, 'Thưởng', 'income', '#34D399', '🎁'),
            (user_id, 'Đầu tư', 'income', '#6EE7B7', '📈'),
            (user_id, 'Khác (Thu nhập)', 'income', '#A7F3D0', '💵'),
            (user_id, 'Ăn uống', 'expense', '#EF4444', '🍔'),
            (user_id, 'Đi lại', 'expense', '#F87171', '🚗'),
            (user_id, 'Nhà ở', 'expense', '#DC2626', '🏠'),
            (user_id, 'Mua sắm', 'expense', '#FCA5A5', '🛒'),
            (user_id, 'Giải trí', 'expense', '#FB923C', '🎬'),
            (user_id, 'Sức khỏe', 'expense', '#F97316', '🏥'),
            (user_id, 'Học tập', 'expense', '#FDBA74', '📚'),
            (user_id, 'Hóa đơn', 'expense', '#FED7AA', '📄'),
            (user_id, 'Khác (Chi tiêu)', 'expense', '#D1D5DB', '📌'),
        ]
        cursor.executemany(
            "INSERT INTO categories (user_id, name, type, color, icon, is_default) VALUES (%s, %s, %s, %s, %s, TRUE)",
            default_categories
        )
        conn.commit()

        return jsonify({
            'message': 'Đăng ký thành công!',
            'user': {'id': user_id, 'username': username, 'email': email}
        }), 201

    except Exception as e:
        if conn is not None:
            conn.rollback()
        return jsonify({'error': f'Lỗi đăng ký: {str(e)}'}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Vui lòng nhập tên đăng nhập và mật khẩu'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or not bcrypt.check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401

        access_token = create_access_token(identity=str(user['id']))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Lỗi kết nối database'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Không tìm thấy người dùng'}), 404
        return jsonify(user), 200
    finally:
        cursor.close()
        conn.close()
