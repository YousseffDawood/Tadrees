/**
 * navbar.js – Premium Animated Navigation Logic
 * Handles cavity sliding, extraction effects, and magnetic hover.
 */

document.addEventListener('DOMContentLoaded', () => {
  const sidebarNav = document.querySelector('.sidebar-nav');
  if (!sidebarNav) return;

  // 1. Create and inject cavity element
  const cavity = document.createElement('div');
  cavity.className = 'nav-cavity';
  sidebarNav.appendChild(cavity);

  const navItems = document.querySelectorAll('.nav-item');

  // 2. Initial cavity positioning (check session storage first to prevent jump)
  function positionCavity(item, instant = false) {
    if (!item) return;
    const top = item.offsetTop;
    const height = item.offsetHeight;
    if (instant) {
      cavity.style.transition = 'none';
    } else {
      cavity.style.transition = 'transform 0.25s var(--spring-transition), height 0.25s var(--spring-transition), opacity 0.3s';
    }
    cavity.style.transform = `translateY(${top}px)`;
    cavity.style.height = `${height}px`;

    // Force reflow if instant to ensure transition is disabled for the jump
    if (instant) {
      cavity.offsetHeight;
      cavity.style.transition = ''; // restore from css
    }

    // Save to session storage for smooth page load
    sessionStorage.setItem('navCavityPos', top);
    sessionStorage.setItem('navCavityHeight', height);
  }

  // Restore from session storage instantly if available
  const savedTop = sessionStorage.getItem('navCavityPos');
  const savedHeight = sessionStorage.getItem('navCavityHeight');
  if (savedTop !== null) {
    cavity.style.transition = 'none';
    cavity.style.transform = `translateY(${savedTop}px)`;
    cavity.style.height = `${savedHeight}px`;
    cavity.offsetHeight; // force reflow
    cavity.style.transition = '';
  }

  // Wait a tiny bit for router.js to set .active, then reposition precisely
  setTimeout(() => {
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) {
      sidebarNav.closest('.sidebar')?.classList.add('nav-has-active');
      positionCavity(activeItem, !savedTop);
    }

    // ── Desktop auto-hide (works with or without active item) ──
    if (window.innerWidth > 768) {
      const sidebar = document.querySelector('.sidebar');
      if (!sidebar) return;

      // Ensure trigger element exists
      let trigger = document.getElementById('sidebar-trigger');
      if (!trigger) {
        trigger = document.createElement('div');
        trigger.className = 'sidebar-trigger';
        trigger.id = 'sidebar-trigger';
        sidebar.parentNode?.insertBefore(trigger, sidebar);
      }

      let mini = null;
      let hideTimeout;
      let sidebarForced = false;

      function showSidebar() {
        clearTimeout(hideTimeout);
        sidebarForced = true;
        sidebar.classList.add('visible');
        if (mini) mini.classList.remove('visible');
      }

      function scheduleHide() {
        sidebarForced = false;
        hideTimeout = setTimeout(() => {
          sidebar.classList.remove('visible');
          if (mini) mini.classList.add('visible');
        }, 400);
      }

      document.addEventListener('mousemove', (e) => {
        const tr = trigger.getBoundingClientRect();
        const sr = sidebar.getBoundingClientRect();

        const overTrigger = e.clientX >= tr.left && e.clientX <= tr.right;
        const overSidebar = e.clientX >= sr.left && e.clientX <= sr.right &&
                            e.clientY >= sr.top && e.clientY <= sr.bottom;

        if (overTrigger || overSidebar) {
          showSidebar();
        } else if (sidebarForced) {
          scheduleHide();
        }
      });

      // ── Mini icon (only when active item exists) ──
      if (activeItem) {
        mini = document.createElement('div');
        mini.className = 'nav-mini-icon';
        const iconSvg = activeItem.querySelector('svg')?.cloneNode(true);
        if (iconSvg) mini.appendChild(iconSvg);
        document.body.appendChild(mini);

        function positionMini() {
          const item = document.querySelector('.nav-item.active');
          if (!item) return;
          const rect = item.getBoundingClientRect();
          mini.style.top = `${rect.top + rect.height / 2 - 16}px`;
        }

        positionMini();
        setTimeout(() => mini.classList.add('visible'), 150);
        window.addEventListener('resize', positionMini);
      }
    }
  }, 50);

  // 3. Magnetic Hover Effect
  navItems.forEach(item => {
    item.addEventListener('mousemove', (e) => {
      if (item.classList.contains('active') || item.classList.contains('extracted')) return; // don't move if extracted

      const rect = item.getBoundingClientRect();
      // Calculate center of the item
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Calculate distance from center (-1 to 1)
      const moveX = (e.clientX - centerX) / (rect.width / 2);
      const moveY = (e.clientY - centerY) / (rect.height / 2);

      // Apply gentle movement (max 4px)
      const maxDist = 4;
      item.style.transform = `translate(${moveX * maxDist}px, ${moveY * maxDist}px)`;
    });

    item.addEventListener('mouseleave', () => {
      // Reset transform. 
      item.style.transform = '';
    });

    // 4. Click Interception
    item.addEventListener('click', (e) => {
      const href = item.getAttribute('href');
      // Ignore if it's not a real link or it's the current page
      if (!href || href === '#' || item.classList.contains('active')) return;

      // Allow holding ctrl/cmd to open in new tab without animation block
      if (e.ctrlKey || e.metaKey) return;

      e.preventDefault();

      // Reset transforms
      item.style.transform = '';

      // Remove active from all
      navItems.forEach(nav => {
        nav.classList.remove('active');
        nav.classList.remove('extracted');
      });

      // Add extracted to clicked
      item.classList.add('extracted');

      // Move cavity
      positionCavity(item);

      // Delay navigation
      setTimeout(() => {
        window.location.href = href;
      }, 250);
    });
  });

  // Handle window resize
  window.addEventListener('resize', () => {
    const activeItem = document.querySelector('.nav-item.active') || document.querySelector('.nav-item.extracted');
    if (activeItem) positionCavity(activeItem, true);
  });
});
