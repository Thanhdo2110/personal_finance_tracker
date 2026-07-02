import unittest
from unittest.mock import patch
from flask import Flask
from routes.auth_routes import auth_bp
from mysql.connector.errors import ProgrammingError


class FakeCursor:
    def execute(self, *args, **kwargs):
        raise ProgrammingError("Table 'finance_tracker.users' doesn't exist")

    def close(self):
        return None


class FakeConnection:
    def cursor(self, dictionary=True):
        return FakeCursor()

    def rollback(self):
        return None

    def close(self):
        return None


class RegisterRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp, url_prefix='/api/auth')
        self.client = self.app.test_client()

    @patch('routes.auth_routes.get_db_connection')
    def test_register_returns_json_error_when_db_fails(self, mock_get_db_connection):
        mock_get_db_connection.return_value = FakeConnection()

        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123456'
        })

        self.assertEqual(response.status_code, 500)
        payload = response.get_json()
        self.assertIn('error', payload)
        self.assertIsInstance(payload['error'], str)
        self.assertIn('Lỗi đăng ký', payload['error'])


if __name__ == '__main__':
    unittest.main()
