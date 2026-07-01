requireAuth();
let monthlyChart = null;
let categoryChart = null;

document.getElementById('welcomeUser').textContent = `Xin chào, ${currentUser?.username || ''}`;

// Year selector
const yearSelect = document.getElementById('reportYear');
const currentYear = new Date().getFullYear();
for (let y = currentYear; y >= currentYear - 5; y--) {
    yearSelect.innerHTML += `<option value="${y}">${y}</option>`;
}
yearSelect.value = currentYear;

async function loadReports() {
    const year = parseInt(yearSelect.value);
    const type = document.getElementById('reportType').value;
    const month = parseInt(document.getElementById('reportMonth').value);

    try {
        // Monthly report
        const monthlyData = await apiCall(`/reports/monthly?year=${year}`);
        updateMonthlyChart(monthlyData.data, year);

        // Category report
        if (month > 0) {
            const catData = await apiCall(`/reports/category?year=${year}&month=${month}&type=${type}`);
            updateCategoryChart(catData.data);
        } else {
            updateCategoryChart([]);
        }

        // Table
        updateReportTable(monthlyData.data);
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function updateMonthlyChart(data, year) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    if (monthlyChart) monthlyChart.destroy();

    const months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'];
    const incomeData = new Array(12).fill(0);
    const expenseData = new Array(12).fill(0);

    data.forEach(d => {
        incomeData[d.month - 1] = d.income;
        expenseData[d.month - 1] = d.expense;
    });

    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                { label: 'Thu Nhập', data: incomeData, backgroundColor: '#10B981', borderRadius: 4 },
                { label: 'Chi Tiêu', data: expenseData, backgroundColor: '#EF4444', borderRadius: 4 }
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

function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    if (categoryChart) categoryChart.destroy();

    if (data.length === 0) {
        data = [{ name: 'Chưa có dữ liệu', total: 1, color: '#D1D5DB' }];
    }

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => d.total),
                backgroundColor: data.map(d => d.color || '#6B7280'),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' },
                tooltip: { callbacks: { label: ctx => `${ctx.label}: ${formatCurrency(ctx.raw)}` } }
            }
        }
    });
}

function updateReportTable(data) {
    const tbody = document.getElementById('reportTable');
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-gray-400">Chưa có dữ liệu</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(d => `
        <tr class="table-row border-b">
            <td class="py-3 px-4 font-medium">Tháng ${d.month}</td>
            <td class="py-3 px-4 text-right text-green-600">${formatCurrency(d.income)}</td>
            <td class="py-3 px-4 text-right text-red-600">${formatCurrency(d.expense)}</td>
            <td class="py-3 px-4 text-right font-semibold ${d.balance >= 0 ? 'text-blue-600' : 'text-red-600'}">${formatCurrency(d.balance)}</td>
        </tr>
    `).join('');
}

document.addEventListener('DOMContentLoaded', loadReports);
