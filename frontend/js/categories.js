requireAuth();
let categories = [];
let deleteTargetId = null;

updateWelcomeUser();

async function loadCategories() {
    try {
        const [income, expense] = await Promise.all([
            apiCall('/categories?type=income'),
            apiCall('/categories?type=expense')
        ]);
        categories = [...income, ...expense];
        renderCategories('incomeCategories', income);
        renderCategories('expenseCategories', expense);
    } catch (err) {
        showNotification(err.message, 'error');
    }
}

function renderCategories(containerId, cats) {
    const container = document.getElementById(containerId);
    if (cats.length === 0) {
        container.innerHTML = '<p class="text-gray-400 text-sm">Chưa có danh mục</p>';
        return;
    }
    container.innerHTML = cats.map(c => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
                <span class="w-10 h-10 rounded-full flex items-center justify-center text-lg" style="background-color: ${c.color}20">
                    <span>${c.icon || '📌'}</span>
                </span>
                <div>
                    <span class="font-medium text-gray-800">${c.name}</span>
                    ${c.is_default ? '<span class="ml-2 text-xs bg-gray-200 text-gray-500 px-2 py-0.5 rounded">Mặc định</span>' : ''}
                </div>
            </div>
            ${!c.is_default ? `
                <div>
                    <button onclick="editCategory(${c.id})" class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i></button>
                    <button onclick="deleteCategory(${c.id})" class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i></button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function selectColor(btn, color) {
    document.querySelectorAll('#colorPicker button').forEach(b => b.classList.remove('border-gray-800'));
    btn.classList.add('border-gray-800');
    document.getElementById('catColor').value = color;
}

function openAddModal() {
    document.getElementById('catModalTitle').textContent = 'Thêm Danh Mục';
    document.getElementById('categoryForm').reset();
    document.getElementById('catId').value = '';
    document.getElementById('catIcon').value = '📌';
    document.getElementById('catColor').value = '#6B7280';
    document.querySelectorAll('#colorPicker button').forEach(b => b.classList.remove('border-gray-800'));
    showModal('categoryModal');
}

async function editCategory(id) {
    const cat = categories.find(c => c.id === id);
    if (!cat) return;
    document.getElementById('catModalTitle').textContent = 'Sửa Danh Mục';
    document.getElementById('catId').value = cat.id;
    document.getElementById('catName').value = cat.name;
    document.getElementById('catType').value = cat.type;
    document.getElementById('catColor').value = cat.color;
    document.getElementById('catIcon').value = cat.icon;
    document.querySelectorAll('#colorPicker button').forEach(b => {
        b.classList.remove('border-gray-800');
        if (b.style.backgroundColor && cat.color) {
            // Simple color match
        }
    });
    document.getElementById('categoryModal').classList.remove('hidden');
}

function closeCatModal() {
    hideModal('categoryModal');
}

document.getElementById('categoryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('catId').value;
    const data = {
        name: document.getElementById('catName').value,
        type: document.getElementById('catType').value,
        color: document.getElementById('catColor').value,
        icon: document.getElementById('catIcon').value || '📌'
    };

    try {
        if (id) {
            await apiCall(`/categories/${id}`, 'PUT', data);
            showNotification('Đã cập nhật danh mục');
        } else {
            await apiCall('/categories', 'POST', data);
            showNotification('Đã thêm danh mục');
        }
        closeCatModal();
        loadCategories();
    } catch (err) {
        showNotification(err.message, 'error');
    }
});

function deleteCategory(id) {
    if (!confirm('Bạn có chắc muốn xóa danh mục này?')) return;
    deleteTargetId = id;
    apiCall(`/categories/${id}`, 'DELETE')
        .then(() => {
            showNotification('Đã xóa danh mục');
            loadCategories();
        })
        .catch(err => showNotification(err.message, 'error'));
}

document.addEventListener('DOMContentLoaded', loadCategories);
