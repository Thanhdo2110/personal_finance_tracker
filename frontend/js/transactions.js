requireAuth();
let allCategories = [];
let deleteTargetId = null;
let currentPage = 1;
let totalPages = 1;

document.getElementById('welcomeUser').textContent = `Xin chào, ${currentUser?.username || ''}`;

// Set default month filter to current month
document.getElementById('filterMonth').value = new Date().toISOString().slice(0, 7);

async function loadCategories() {
    const type = document.getElementById('txType').value;
    try {
        allCategories = await apiCall(`/categories?type=${type}`);
        const select = document.getElementById('txCategory');
        select.innerHTML = allCategories.map(c =>
            `<option value="${c.id}">${c.icon} ${c.name}</option>`
        ).join('');
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

async function loadTransactions() {
    const params = new URLSearchParams();
    const search = document.getElementById('searchInput').value;
    const type = document.getElementById('filterType').value;
    const categoryId = document.getElementById('filterCategory').value;
    const month = document.getElementById('filterMonth').value;

    if (search) params.set('search', search);
    if (type) params.set('type', type);
    if (categoryId) params.set('category_id', categoryId);
    if (month) {
        const [y, m] = month.split('-');
        params.set('year', y);
        params.set('month', parseInt(m));
    }
    params.set('page', currentPage);
    params.set('per_page', 15);

    try {
        const data = await apiCall(`/transactions?${params}`);
        renderTransactions(data.transactions);
        renderPagination(data.pagination);
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function renderTransactions(transactions) {
    const tbody = document.getElementById('transactionsTable');
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-12 text-gray-400">Chưa có giao dịch nào</td></tr>';
        return;
    }
    tbody.innerHTML = transactions.map(t => `
        <tr class="table-row border-b">
            <td class="py-3 px-4">${formatDate(t.transaction_date)}</td>
            <td class="py-3 px-4">
                <span class="px-2 py-1 rounded-full text-xs font-medium ${t.type === 'income' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                    ${t.type === 'income' ? 'Thu nhập' : 'Chi tiêu'}
                </span>
            </td>
            <td class="py-3 px-4">
                <span class="inline-flex items-center gap-1">
                    <span>${t.category_icon || '📌'}</span>
                    <span>${t.category_name}</span>
                </span>
            </td>
            <td class="py-3 px-4 text-gray-600 max-w-xs truncate">${t.description || '-'}</td>
            <td class="py-3 px-4 text-right font-semibold ${t.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
            </td>
            <td class="py-3 px-4 text-center">
                <button onclick="editTransaction(${t.id})" class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i></button>
                <button onclick="deleteTransaction(${t.id})" class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

function renderPagination(pagination) {
    totalPages = pagination.total_pages;
    currentPage = pagination.page;
    const container = document.getElementById('pagination');
    if (totalPages <= 1) { container.innerHTML = ''; return; }

    let html = '<div class="flex gap-2">';
    html += `<button onclick="goToPage(${currentPage - 1})" class="px-3 py-1 border rounded ${currentPage === 1 ? 'opacity-50' : 'hover:bg-gray-100'}" ${currentPage === 1 ? 'disabled' : ''}>Trước</button>`;
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<button class="px-3 py-1 bg-blue-600 text-white rounded">${i}</button>`;
        } else if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<button onclick="goToPage(${i})" class="px-3 py-1 border rounded hover:bg-gray-100">${i}</button>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<span class="px-2">...</span>';
        }
    }
    html += `<button onclick="goToPage(${currentPage + 1})" class="px-3 py-1 border rounded ${currentPage === totalPages ? 'opacity-50' : 'hover:bg-gray-100'}" ${currentPage === totalPages ? 'disabled' : ''}>Sau</button>`;
    html += '</div>';
    container.innerHTML = html;
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadTransactions();
}

async function loadFilterCategories() {
    try {
        const [income, expense] = await Promise.all([
            apiCall('/categories?type=income'),
            apiCall('/categories?type=expense')
        ]);
        const select = document.getElementById('filterCategory');
        select.innerHTML = '<option value="">Tất cả danh mục</option>' +
            income.map(c => `<option value="${c.id}">💰 ${c.name}</option>`).join('') +
            expense.map(c => `<option value="${c.id}">${c.icon || '📌'} ${c.name}</option>`).join('');
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function openAddModal() {
    document.getElementById('modalTitle').textContent = 'Thêm Giao Dịch';
    document.getElementById('transactionForm').reset();
    document.getElementById('txId').value = '';
    document.getElementById('txDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('txType').value = 'expense';
    loadCategories();
    document.getElementById('transactionModal').classList.remove('hidden');
}

async function editTransaction(id) {
    try {
        const data = await apiCall(`/transactions/${id}`);
        document.getElementById('modalTitle').textContent = 'Sửa Giao Dịch';
        document.getElementById('txId').value = data.id;
        document.getElementById('txType').value = data.type;
        await loadCategories();
        document.getElementById('txCategory').value = data.category_id;
        document.getElementById('txAmount').value = data.amount;
        document.getElementById('txDate').value = data.transaction_date;
        document.getElementById('txDescription').value = data.description || '';
        document.getElementById('transactionModal').classList.remove('hidden');
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function closeModal() {
    document.getElementById('transactionModal').classList.add('hidden');
}

document.getElementById('transactionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('txId').value;
    const data = {
        category_id: parseInt(document.getElementById('txCategory').value),
        amount: parseFloat(document.getElementById('txAmount').value),
        type: document.getElementById('txType').value,
        transaction_date: document.getElementById('txDate').value,
        description: document.getElementById('txDescription').value
    };

    try {
        if (id) {
            await apiCall(`/transactions/${id}`, 'PUT', data);
            showNotification('Đã cập nhật giao dịch');
        } else {
            await apiCall('/transactions', 'POST', data);
            showNotification('Đã thêm giao dịch');
        }
        closeModal();
        loadTransactions();
    } catch (err) {
        showNotification(err.message, 'error');
    }
});

function deleteTransaction(id) {
    deleteTargetId = id;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteTargetId = null;
}

async function confirmDelete() {
    try {
        await apiCall(`/transactions/${deleteTargetId}`, 'DELETE');
        showNotification('Đã xóa giao dịch');
        closeDeleteModal();
        loadTransactions();
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

async function exportCSV() {
    const params = new URLSearchParams();
    const type = document.getElementById('filterType').value;
    const month = document.getElementById('filterMonth').value;
    if (type) params.set('type', type);
    if (month) {
        const [y, m] = month.split('-');
        params.set('start_date', `${y}-${m}-01`);
        const lastDay = new Date(parseInt(y), parseInt(m), 0).getDate();
        params.set('end_date', `${y}-${m}-${lastDay}`);
    }

    try {
        const response = await fetch(`${API_BASE}/reports/export/csv?${params}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Export failed');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã export CSV thành công');
    } catch (err) {
        showNotification(err.message || 'Lỗi export', 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadFilterCategories();
    loadTransactions();
});
