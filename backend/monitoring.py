import time
from flask import request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY


LOGIN_SUCCESS = Counter("finance_login_success_total", "Total successful logins")
LOGIN_FAILED = Counter("finance_login_failed_total", "Total failed logins")
REGISTER_SUCCESS = Counter("finance_register_success_total", "Total successful registrations")
REGISTER_FAILED = Counter("finance_register_failed_total", "Total failed registrations")


TRANSACTION_CREATED = Counter(
    "finance_transaction_created_total", 
    "Total transactions created", 
    ["type"]  
)
TRANSACTION_UPDATED = Counter("finance_transaction_updated_total", "Total transactions updated")
TRANSACTION_DELETED = Counter("finance_transaction_deleted_total", "Total transactions deleted")
TRANSACTION_FETCHED = Counter("finance_transaction_fetched_total", "Total transactions retrieved")


CATEGORY_CREATED = Counter("finance_category_created_total", "Total categories created")
CATEGORY_UPDATED = Counter("finance_category_updated_total", "Total categories updated")
CATEGORY_DELETED = Counter("finance_category_deleted_total", "Total categories deleted")


BUDGET_CREATED = Counter("finance_budget_created_total", "Total budgets created")
BUDGET_UPDATED = Counter("finance_budget_updated_total", "Total budgets updated")
BUDGET_DELETED = Counter("finance_budget_deleted_total", "Total budgets deleted")


DASHBOARD_REQUESTS = Counter("finance_dashboard_requests_total", "Total dashboard views")
REPORT_REQUESTS = Counter("finance_report_requests_total", "Total report generations")


API_LATENCY = Histogram(
    "finance_api_latency_seconds",
    "Application response latency in seconds",
    ["method", "endpoint", "status_code"]
)



def init_monitoring(app):
    """
    Hàm này dùng để cấu hình tự động tích hợp Prometheus vào ứng dụng Flask.
    Nó sẽ quản lý middleware đo latency và tạo sẵn route `/metrics`.
    """
    

    @app.before_request
    def start_timer():
        request._start_time = time.time()

   
    @app.after_request
    def record_latency(response):
    
        if request.path == '/metrics':
            return response
            
        if hasattr(request, '_start_time'):
            latency = time.time() - request._start_time
            
            endpoint = request.url_rule.rule if request.url_rule else request.path
            
            API_LATENCY.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).observe(latency)
            
        return response


    @app.route('/metrics')
    def metrics():
        return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}