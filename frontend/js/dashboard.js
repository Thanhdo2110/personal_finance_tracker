requireAuth();

let barChart = null;
let pieChart = null;

// Set up year selector
function setupYearSelector() {
    const yearSelect = document.getElementById('yearSelect');
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= currentYear - 5; y--) {
        yearSelect.innerHTML += `<option value="${y}">${y}</option>`;
    }
    yearSelect.value = currentYear;
}

// Set up month selector
function setupMonthSelector() {
    const monthSelect = document.getElementById('monthSelect');
    monthSelect.value = new Date().getMonth() + 1;
}

async function loadDashboard() {
    const month = parseInt(document.getElementById('monthSelect').value);
    const year = parseInt(document.getElementById('yearSelect').value);

    try {
        const data = await apiCall(`/dashboard/summary?month=${month}&year=${year}`);

        // Update summary cards
        document.getElementById('totalBalance').textContent = formatCurrency(data.total_balance);
        document.getElementById('monthlyIncome').textContent = formatCurrency(data.monthly.total_income);
        document.getElementById('monthlyExpense').textContent = formatCurrency(data.monthly.total_expense);

        // Bar chart
        updateBarChart(data.monthly_chart);

        // Pie chart
        updatePieChart(data.category_breakdown);

        // Recent transactions
        updateRecentTransactions(data.recent_transactions);
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function updateBarChart(chartData) {
    const ctx = document.getElementById('barChart').getContext('2d');
    if (barChart) barChart.destroy();

    const labels = chartData.map(d => `T${d.month}/${d.year}`);
    const incomeData = chartData.map(d => d.income);
    const expenseData = chartData.map(d => d.expense);

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Thu Nhập', data: incomeData, backgroundColor: '#10B981', borderRadius: 6 },
                { label: 'Chi Tiêu', data: expenseData, backgroundColor: '#EF4444', borderRadius: 6 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                y: { beginAtZero: true, ticks: { callback: v => formatCurrency(v) } }
            }
        }
    });
}

function updatePieChart(breakdown) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    if (pieChart) pieChart.destroy();

    if (breakdown.length === 0) {
        breakdown = [{ name: 'Chưa có', total: 1, color: '#D1D5DB' }];
    }

    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: breakdown.map(d => d.name),
            datasets: [{
                data: breakdown.map(d => d.total),
                backgroundColor: breakdown.map(d => d.color || '#6B7280'),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' },
                tooltip: {
                    callbacks: { label: ctx => `${ctx.label}: ${formatCurrency(ctx.raw)}` }
                }
            }
        }
    });
}

function updateRecentTransactions(transactions) {
    const tbody = document.getElementById('recentTransactions');
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-gray-400">Chưa có giao dịch nào</td></tr>';
        return;
    }
    tbody.innerHTML = transactions.map(t => `
        <tr class="table-row border-b">
            <td class="py-3 px-4">${formatDate(t.transaction_date)}</td>
            <td class="py-3 px-4">
                <span class="inline-flex items-center gap-1">
                    <span>${t.category_icon || '📌'}</span>
                    <span>${t.category_name}</span>
                </span>
            </td>
            <td class="py-3 px-4 text-gray-600">${t.description || '-'}</td>
            <td class="py-3 px-4 text-right font-semibold ${t.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
            </td>
        </tr>
    `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('welcomeUser').textContent = `Xin chào, ${currentUser?.username || ''}`;
    setupYearSelector();
    setupMonthSelector();
    loadDashboard();
});
