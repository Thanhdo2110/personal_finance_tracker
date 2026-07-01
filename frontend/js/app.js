const API_BASE = '/api';

let currentUser = null;
let token = null;

// Load token from localStorage
function loadAuth() {
    token = localStorage.getItem('token');
    currentUser = JSON.parse(localStorage.getItem('user') || 'null');
}

// Save auth to localStorage
function saveAuth(tokenData, userData) {
    token = tokenData;
    currentUser = userData;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
}

// Clear auth
function clearAuth() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Check if authenticated
function isAuthenticated() {
    return !!token;
}

// API call helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || 'Có lỗi xảy ra');
    }
    return result;
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 ${
        type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Check auth on page load
function requireAuth() {
    loadAuth();
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
    }
}

// Logout
function logout() {
    clearAuth();
    window.location.href = 'login.html';
}
