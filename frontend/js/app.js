const API_BASE = '/api';

let currentUser = null;
let token = null;

// Load token from localStorage
function loadAuth() {
    token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    currentUser = storedUser ? JSON.parse(storedUser) : null;
}

// Save auth to localStorage
function saveAuth(tokenData, userData) {
    token = tokenData;
    currentUser = userData;
    localStorage.setItem('token', token || '');
    localStorage.setItem('user', JSON.stringify(userData || null));
}

// Clear auth
function clearAuth() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Update the welcome label if the page has one
function updateWelcomeUser() {
    const welcomeElement = document.getElementById('welcomeUser');
    if (welcomeElement) {
        welcomeElement.textContent = `Xin chào, ${currentUser?.username || ''}`;
    }
}

// Check if authenticated
function isAuthenticated() {
    return !!token;
}

// Modal helpers
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.remove('hidden');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
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
    const responseText = await response.text();
    let result = null;

    if (responseText) {
        try {
            result = JSON.parse(responseText);
        } catch (error) {
            throw new Error('Máy chủ trả về dữ liệu không hợp lệ.');
        }
    }

    if (!response.ok) {
        throw new Error(result?.error || 'Có lỗi xảy ra');
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
