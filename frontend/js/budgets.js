requireAuth();
let expenseCategories = [];

updateWelcomeUser();

// Set month/year to current
const now = new Date();
document.getElementById('budgetMonth').value = now.getMonth() + 1;

// Year selector
const yearSelect = document.getElementById('budgetYear');
const currentYear = now.getFullYear();
for (let y = currentYear; y >= currentYear - 5; y--) {
    yearSelect.innerHTML += `<option value="${y}">${y}</option>`;
}
yearSelect.value = currentYear;

async function loadExpenseCategories() {
    try {
        expenseCategories = await apiCall('/categories?type=expense');
        const select = document.getElementById('budgetCategory');
        select.innerHTML = expenseCategories.map(c =>
            `<option value="${c.id}">${c.icon} ${c.name}</option>`
        ).join('');
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

async function loadBudgets() {
    const month = document.getElementById('budgetMonth').value;
    const year = document.getElementById('budgetYear').value;

    try {
        const budgets = await apiCall(`/budgets?month=${month}&year=${year}`);
        renderBudgets(budgets);
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function renderBudgets(budgets) {
    const container = document.getElementById('budgetsList');
    const noBudgets = document.getElementById('noBudgets');

    if (budgets.length === 0) {
        container.innerHTML = '';
        noBudgets.classList.remove('hidden');
        return;
    }
    noBudgets.classList.add('hidden');

    container.innerHTML = budgets.map(b => {
        const percentage = b.percentage;
        const isOver = percentage >= 100;
        const barColor = isOver ? 'bg-red-500' : percentage >= 80 ? 'bg-yellow-500' : 'bg-green-500';

        return `
            <div class="bg-white rounded-xl shadow p-6 card">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-3">
                        <span class="text-2xl">${b.category_icon || '📌'}</span>
                        <span class="font-semibold text-gray-800">${b.category_name}</span>
                    </div>
                    <button onclick="deleteBudget(${b.id})" class="text-red-400 hover:text-red-600">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="mb-2">
                    <div class="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Đã dùng: ${formatCurrency(b.spent)}</span>
                        <span>${percentage}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="budget-progress ${barColor} h-3 rounded-full" style="width: ${Math.min(percentage, 100)}%"></div>
                    </div>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Ngân sách: ${formatCurrency(b.budget_amount)}</span>
                    <span class="${isOver ? 'text-red-600 font-semibold' : 'text-green-600'}">
                        Còn lại: ${formatCurrency(b.remaining)}
                    </span>
                </div>
                ${isOver ? '<p class="text-red-500 text-xs mt-2"><i class="fas fa-exclamation-triangle mr-1"></i>Đã vượt ngân sách!</p>' : ''}
            </div>
        `;
    }).join('');
}

function openAddModal() {
    document.getElementById('budgetForm').reset();
    document.getElementById('budgetFormError').classList.add('hidden');
    showModal('budgetModal');
}

function closeBudgetModal() {
    hideModal('budgetModal');
}

document.getElementById('budgetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        category_id: parseInt(document.getElementById('budgetCategory').value),
        amount: parseFloat(document.getElementById('budgetAmount').value),
        month: parseInt(document.getElementById('budgetMonth').value),
        year: parseInt(document.getElementById('budgetYear').value)
    };

    try {
        await apiCall('/budgets', 'POST', data);
        showNotification('Đã thêm ngân sách');
        closeBudgetModal();
        loadBudgets();
    } catch (err) {
        showNotification(err.message, 'error');
    }
});

async function deleteBudget(id) {
    if (!confirm('Bạn có chắc muốn xóa ngân sách này?')) return;
    try {
        await apiCall(`/budgets/${id}`, 'DELETE');
        showNotification('Đã xóa ngân sách');
        loadBudgets();
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadExpenseCategories();
    loadBudgets();
});
