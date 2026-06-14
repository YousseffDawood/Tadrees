/**
 * utils.js – Toast, modal, date/time formatters, shared UI helpers.
 */

// ── Toast ────────────────────────────────────────────────
let toastContainer;
function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
}

const ICONS = {
  success: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>`,
  error:   `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>`,
  warning: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  info:    `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

function showToast(message, type = 'info', duration = 3500) {
  const container = getToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `${ICONS[type] || ICONS.info}<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-out');
    toast.addEventListener('animationend', () => toast.remove());
  }, duration);
}

// ── Modal ────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); document.body.style.overflow = ''; }
}
// Wire all .modal-close buttons automatically
document.addEventListener('click', e => {
  const btn = e.target.closest('.modal-close, [data-close-modal]');
  if (btn) {
    const backdrop = btn.closest('.modal-backdrop');
    if (backdrop) { backdrop.classList.remove('open'); document.body.style.overflow = ''; }
  }
  // Close on backdrop click
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// ── Date / Time ──────────────────────────────────────────
function formatDate(str) {
  if (!str) return '—';
  const d = new Date(str);
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}
function formatTime(str) {
  if (!str) return '—';
  const [h, m] = str.split(':');
  const hour = parseInt(h, 10);
  return `${hour % 12 || 12}:${m} ${hour < 12 ? 'AM' : 'PM'}`;
}
function formatDateTime(str) {
  if (!str) return '—';
  const d = new Date(str);
  return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function todayISO() {
  return new Date().toISOString().split('T')[0];
}

// ── Empty / Loading states ───────────────────────────────
function renderLoading(container) {
  container.innerHTML = `<div class="loading-center"><div class="spinner"></div><span>Loading...</span></div>`;
}
function renderEmpty(container, message = 'No data found.', action = '') {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
          <rect x="9" y="3" width="6" height="4" rx="1"/>
        </svg>
      </div>
      <h3>Nothing here yet</h3>
      <p>${message}</p>
      ${action}
    </div>`;
}
function renderError(container, msg = 'Failed to load data.') {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon" style="background:var(--danger-light);color:var(--danger)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>
      </div>
      <h3>Error</h3>
      <p>${msg}</p>
    </div>`;
}

// ── Avatar initials ──────────────────────────────────────
function initials(name = '') {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || '?';
}

// ── Form helpers ─────────────────────────────────────────
function formData(formEl) {
  const data = {};
  new FormData(formEl).forEach((v, k) => { data[k] = v; });
  return data;
}
function clearForm(formEl) {
  if (formEl) formEl.reset();
}
function setSubmitting(btn, loading) {
  if (!btn) return;
  btn.disabled = loading;
  btn._origText = btn._origText || btn.innerHTML;
  btn.innerHTML = loading
    ? `<span class="spinner spinner-sm" style="border-top-color:#fff;border-color:rgba(255,255,255,.3)"></span> Saving...`
    : btn._origText;
}

// ── Confirm dialog ───────────────────────────────────────
function confirmAction(message) {
  return window.confirm(message);
}

// ── Debounce ─────────────────────────────────────────────
function debounce(fn, delay = 300) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}
