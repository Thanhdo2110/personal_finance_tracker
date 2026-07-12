"""
monitoring.py

Centralized Prometheus metrics for Personal Finance Tracker.
"""

from prometheus_client import Counter, Histogram, Gauge

# ==========================================================
# Authentication Metrics
# ==========================================================

LOGIN_SUCCESS = Counter(
    "finance_login_success_total",
    "Total successful logins"
)

LOGIN_FAILED = Counter(
    "finance_login_failed_total",
    "Total failed logins"
)

REGISTER_SUCCESS = Counter(
    "finance_register_success_total",
    "Total successful registrations"
)

REGISTER_FAILED = Counter(
    "finance_register_failed_total",
    "Total failed registrations"
)

# ==========================================================
# Transaction Metrics
# ==========================================================

TRANSACTION_CREATED = Counter(
    "finance_transaction_created_total",
    "Total transactions created"
)

TRANSACTION_UPDATED = Counter(
    "finance_transaction_updated_total",
    "Total transactions updated"
)

TRANSACTION_DELETED = Counter(
    "finance_transaction_deleted_total",
    "Total transactions deleted"
)

TRANSACTION_FETCHED = Counter(
    "finance_transaction_fetched_total",
    "Total transaction queries"
)

# ==========================================================
# Budget Metrics
# ==========================================================

BUDGET_CREATED = Counter(
    "finance_budget_created_total",
    "Total budgets created"
)

BUDGET_UPDATED = Counter(
    "finance_budget_updated_total",
    "Total budgets updated"
)

BUDGET_DELETED = Counter(
    "finance_budget_deleted_total",
    "Total budgets deleted"
)

# ==========================================================
# Category Metrics
# ==========================================================

CATEGORY_CREATED = Counter(
    "finance_category_created_total",
    "Total categories created"
)

CATEGORY_UPDATED = Counter(
    "finance_category_updated_total",
    "Total categories updated"
)

CATEGORY_DELETED = Counter(
    "finance_category_deleted_total",
    "Total categories deleted"
)

# ==========================================================
# Dashboard & Reports
# ==========================================================

DASHBOARD_REQUESTS = Counter(
    "finance_dashboard_requests_total",
    "Dashboard API requests"
)

REPORT_REQUESTS = Counter(
    "finance_report_requests_total",
    "Report API requests"
)

# ==========================================================
# HTTP Request Latency
# ==========================================================

API_LATENCY = Histogram(
    "finance_api_latency_seconds",
    "API response time",
    ["endpoint", "method"]
)

# ==========================================================
# SQL Query Latency
# ==========================================================

DATABASE_QUERY_LATENCY = Histogram(
    "finance_database_query_duration_seconds",
    "Database query execution time",
    ["query_type"]
)

# ==========================================================
# Active Users
# ==========================================================

ACTIVE_USERS = Gauge(
    "finance_active_users",
    "Currently active users"
)