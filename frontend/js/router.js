/**
 * router.js – Auth guard, role guard, navbar injection.
 * Include this script in every protected page.
 */

(function () {
  // ── Auth guard ──────────────────────────────────────────
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return;
  }

  // ── Run after DOM is ready ───────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initHamburger();
    highlightActiveNav();
    applyRoleGates();
  });

  function initNavbar() {
    const user = getUser();
    const nameEl = document.getElementById('sidebar-username');
    const roleEl = document.getElementById('sidebar-role');
    const avatarEl = document.getElementById('sidebar-avatar');
    if (nameEl) nameEl.textContent = user?.name || 'User';
    if (roleEl) roleEl.textContent = getRole();
    if (avatarEl) avatarEl.textContent = (user?.name || 'U')[0].toUpperCase();

    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', doLogout);
  }

  function initHamburger() {
    const ham = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    function open()  { sidebar?.classList.add('open'); overlay?.classList.add('open'); }
    function close() { sidebar?.classList.remove('open'); overlay?.classList.remove('open'); }
    ham?.addEventListener('click', open);
    overlay?.addEventListener('click', close);
  }

  function highlightActiveNav() {
    const currentPage = (window.location.pathname.split('/').pop() || 'index.html')
      .split('?')[0]
      .split('#')[0];

    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.remove('active');
      el.removeAttribute('aria-current');

      const href = el.getAttribute('href') || '';
      const linkPage = href.split('/').pop().split('?')[0].split('#')[0];

      if (linkPage === currentPage) {
        el.classList.add('active');
        el.setAttribute('aria-current', 'page');
      }
    });
  }

  function applyRoleGates() {
    const role = getRole();
    // Show admin-only items
    if (role === 'admin') {
      document.querySelectorAll('.nav-admin-only').forEach(el => {
        el.style.display = '';
      });
    }
    // Redirect if page requires admin and user is not
    const requiresAdmin = document.body.dataset.requiresAdmin;
    if (requiresAdmin && role !== 'ADMIN') {
      document.querySelector('.main-content').innerHTML = `
        <div class="page-body">
          <div class="empty-state" style="padding:120px 20px">
            <div class="empty-state-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <h3>Access Denied</h3>
            <p>This page requires Administrator privileges.</p>
            <a href="index.html" class="btn btn-primary" style="margin-top:12px">Go to Home</a>
          </div>
        </div>`;
    }
  }
})();
