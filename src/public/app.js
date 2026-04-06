const createForm = document.getElementById('createForm');
const taskBody = document.getElementById('taskBody');
const refreshBtn = document.getElementById('refreshBtn');
const reviewDialog = document.getElementById('reviewDialog');
const reviewForm = document.getElementById('reviewForm');

async function request(url, options = {}) {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const json = await resp.json();
  if (!resp.ok) {
    throw new Error(json.message || '请求失败');
  }
  return json;
}

function renderRows(tasks) {
  taskBody.innerHTML = '';
  tasks.forEach((task) => {
    const tr = document.createElement('tr');
    const statusClass = `status-${task.status.toLowerCase()}`;
    tr.innerHTML = `
      <td>${task.id}</td>
      <td>${task.order_no}</td>
      <td>${task.customer_name}</td>
      <td class="${statusClass}">${task.status}</td>
      <td>${task.reviewer || '-'}</td>
      <td>
        <button ${task.status !== 'PENDING' ? 'disabled' : ''} data-review-id="${task.id}">
          审核
        </button>
      </td>
    `;
    taskBody.appendChild(tr);
  });

  document.querySelectorAll('[data-review-id]').forEach((btn) => {
    btn.addEventListener('click', () => openReviewDialog(btn.dataset.reviewId));
  });
}

async function loadTasks() {
  try {
    const data = await request('/api/tasks');
    renderRows(data.data || []);
  } catch (err) {
    alert(`加载任务失败: ${err.message}`);
  }
}

function openReviewDialog(id) {
  reviewForm.elements.id.value = id;
  reviewDialog.showModal();
}

createForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(createForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    createForm.reset();
    await loadTasks();
    alert('创建成功');
  } catch (err) {
    alert(`创建失败: ${err.message}`);
  }
});

reviewForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(reviewForm);
  const payload = {
    reviewer: formData.get('reviewer'),
    status: formData.get('status'),
    review_note: formData.get('review_note')
  };
  const id = formData.get('id');

  try {
    await request(`/api/tasks/${id}/review`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    reviewDialog.close();
    reviewForm.reset();
    await loadTasks();
    alert('审核成功，已触发邮件与ERP写入');
  } catch (err) {
    alert(`审核失败: ${err.message}`);
  }
});

refreshBtn.addEventListener('click', loadTasks);

loadTasks();
