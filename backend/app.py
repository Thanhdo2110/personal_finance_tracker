from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from database import init_db
import os

# 1. Import hàm khởi tạo từ file gộp monitoring.py của bạn
from monitoring import init_monitoring

# Load environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)

    # ==========================
    # Configuration
    # ==========================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    # ==========================
    # Kích hoạt Monitoring Tập Trung
    # ==========================
    # Gọi hàm này để tự động cài đặt hệ thống đo Latency 
    # và mở luôn endpoint `/metrics`
    init_monitoring(app)

    # ==========================
    # Initialize Extensions
    # ==========================
    Bcrypt(app)
    JWTManager(app)
    CORS(app)

    # ==========================
    # Database
    # ==========================
    init_db()

    # ==========================
    # Register Blueprints
    # ==========================
    from routes.auth_routes import auth_bp
    from routes.transaction_routes import transaction_bp
    from routes.category_routes import category_bp
    from routes.budget_routes import budget_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(transaction_bp, url_prefix="/api/transactions")
    app.register_blueprint(category_bp, url_prefix="/api/categories")
    app.register_blueprint(budget_bp, url_prefix="/api/budgets")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(report_bp, url_prefix="/api/reports")

    # ==========================
    # Health Check
    # ==========================
    @app.route("/health")
    def health():
        return {
            "status": "UP",
            "application": "Finance Tracker",
            "environment": os.getenv("FLASK_ENV", "development"),
        }, 200

    @app.route("/api/health")
    def api_health():
        return {"status": "API OK"}, 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)