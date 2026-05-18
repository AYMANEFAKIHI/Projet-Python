document.addEventListener('DOMContentLoaded', function () {

  // ── Add ambient orb2 element ──
  const orb2 = document.createElement('div');
  orb2.className = 'orb2';
  document.body.appendChild(orb2);

  // ── Sidebar toggle ──
  const toggle  = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const main    = document.getElementById('main-content');

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
      } else {
        const collapsed = sidebar.dataset.collapsed === 'true';
        if (collapsed) {
          sidebar.style.transform = '';
          main.style.marginLeft   = 'var(--sidebar-w)';
          sidebar.dataset.collapsed = 'false';
        } else {
          sidebar.style.transform = 'translateX(-100%)';
          main.style.marginLeft   = '0';
          sidebar.dataset.collapsed = 'true';
        }
      }
    });
  }

  // ── Close sidebar on outside click (mobile) ──
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('open')) {
      if (!sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
      }
    }
  });

  // ── Auto-dismiss success alerts ──
  document.querySelectorAll('.alert-success').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-8px)';
      setTimeout(function () { el.remove(); }, 400);
    }, 4500);
  });

  // ── KPI counter animation ──
  document.querySelectorAll('.kpi-value').forEach(function (el) {
    const text = el.textContent.trim();
    // Extract numeric value if possible
    const numMatch = text.match(/^([\d\s]+)/);
    if (numMatch && !text.includes('.')) {
      const target = parseInt(numMatch[1].replace(/\s/g,''), 10);
      if (!isNaN(target) && target > 0 && target < 100000) {
        let start = 0;
        const suffix = text.replace(numMatch[1], '');
        const duration = 700;
        const step = 16;
        const increment = target / (duration / step);
        el.textContent = '0' + suffix;
        const timer = setInterval(function () {
          start += increment;
          if (start >= target) {
            start = target;
            clearInterval(timer);
          }
          el.textContent = Math.round(start).toLocaleString('fr') + suffix;
        }, step);
      }
    }
  });

  // ── Stagger entrance animation for cards ──
  const animatables = document.querySelectorAll('.card, .mission-card, .kpi-card');
  animatables.forEach(function (el, i) {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(14px)';
    el.style.transition = `opacity .35s ease ${i * 45}ms, transform .35s ease ${i * 45}ms`;
    requestAnimationFrame(function () {
      setTimeout(function () {
        el.style.opacity   = '1';
        el.style.transform = 'none';
      }, 30);
    });
  });

  // ── Stat bar fill animation ──
  const bars = document.querySelectorAll('.stat-bar-fill, .chart-bar-inner');
  bars.forEach(function (bar) {
    const target = bar.style.width;
    bar.style.width = '0%';
    setTimeout(function () {
      bar.style.transition = 'width .8s cubic-bezier(.4,0,.2,1)';
      bar.style.width = target;
    }, 300);
  });

  // ── Smooth row click highlight ──
  document.querySelectorAll('tbody tr[onclick]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('mouseenter', function () {
      row.style.background = 'rgba(79,125,255,0.06)';
    });
    row.addEventListener('mouseleave', function () {
      row.style.background = '';
    });
  });

  // ── Active nav highlight ──
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── Confirm dialogs for danger actions ──
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Date inputs: set max to today ──
  document.querySelectorAll('input[type="date"]').forEach(function (inp) {
    if (!inp.max && inp.name === 'date_frais') {
      inp.max = new Date().toISOString().split('T')[0];
    }
  });

  // ── Tooltip enhancement for icon buttons ──
  document.querySelectorAll('[title]').forEach(function (el) {
    el.setAttribute('aria-label', el.getAttribute('title'));
  });

});
