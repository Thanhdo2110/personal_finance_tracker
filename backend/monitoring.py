import time
from flask import request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

# ==========================================
# 1. ĐỊNH NGHĨA CÁC METRICS (Giữ nguyên của bạn)
# ==========================================

# Các Counter cho Auth
LOGIN_SUCCESS = Counter("finance_login_success_total", "Total successful logins")
LOGIN_FAILED = Counter("finance_login_failed_total", "Total failed logins")
REGISTER_SUCCESS = Counter("finance_register_success_total", "Total successful registrations")
REGISTER_FAILED = Counter("finance_register_failed_total", "Total failed registrations")

# Các Counter cho Transaction
TRANSACTION_CREATED = Counter(
    "finance_transaction_created_total", 
    "Total transactions created", 
    ["type"]  # label để phân biệt income/expense
)
TRANSACTION_UPDATED = Counter("finance_transaction_updated_total", "Total transactions updated")
TRANSACTION_DELETED = Counter("finance_transaction_deleted_total", "Total transactions deleted")
TRANSACTION_FETCHED = Counter("finance_transaction_fetched_total", "Total transactions retrieved")

# Các Counter cho Category
CATEGORY_CREATED = Counter("finance_category_created_total", "Total categories created")
CATEGORY_UPDATED = Counter("finance_category_updated_total", "Total categories updated")
CATEGORY_DELETED = Counter("finance_category_deleted_total", "Total categories deleted")

# Các Counter cho Budget
BUDGET_CREATED = Counter("finance_budget_created_total", "Total budgets created")
BUDGET_UPDATED = Counter("finance_budget_updated_total", "Total budgets updated")
BUDGET_DELETED = Counter("finance_budget_deleted_total", "Total budgets deleted")

# Các Counter cho Dashboard & Report
DASHBOARD_REQUESTS = Counter("finance_dashboard_requests_total", "Total dashboard views")
REPORT_REQUESTS = Counter("finance_report_requests_total", "Total report generations")

# Histogram tự động đo Latency cho toàn bộ các API
API_LATENCY = Histogram(
    "finance_api_latency_seconds",
    "Application response latency in seconds",
    ["method", "endpoint", "status_code"]
)

# ==========================================
# 2. HÀM KHỞI TẠO MONITORING CHO FLASK
# ==========================================

def init_monitoring(app):
    """
    Hàm này dùng để cấu hình tự động tích hợp Prometheus vào ứng dụng Flask.
    Nó sẽ quản lý middleware đo latency và tạo sẵn route `/metrics`.
    """
    
    # Middleware 1: Ghi lại thời gian bắt đầu nhận request
    @app.before_request
    def start_timer():
        request._start_time = time.time()

    # Middleware 2: Tính toán latency sau khi request xử lý xong và push vào Histogram
    @app.after_request
    def record_latency(response):
        # Bỏ qua không đo latency cho chính endpoint lấy metric để tránh rác dữ liệu
        if request.path == '/metrics':
            return response
            
        if hasattr(request, '_start_time'):
            latency = time.time() - request._start_time
            # Lấy endpoint dạng mẫu (ví dụ: /api/transactions/<int:id> thay vì id cụ thể)
            endpoint = request.url_rule.rule if request.url_rule else request.path
            
            API_LATENCY.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).observe(latency)
            
        return response

    # Tạo endpoint /metrics tập trung tại đây luôn
    @app.route('/metrics')
    def metrics():
        return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}