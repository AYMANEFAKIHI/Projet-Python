document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar toggle ──
  const toggle  = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const main    = document.getElementById('main-content');

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
      } else {
        const isOpen = sidebar.style.transform !== 'translateX(-100%)' &&
                       sidebar.style.transform !== '';
        if (isOpen || sidebar.style.transform === '') {
          sidebar.style.transform = 'translateX(-100%)';
          main.style.marginLeft   = '0';
        } else {
          sidebar.style.transform = '';
          main.style.marginLeft   = 'var(--sidebar-w)';
        }
      }
    });
  }

  // ── Auto-dismiss success alerts ──
  document.querySelectorAll('.alert-success').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-8px)';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // ── Animate KPI values ──
  document.querySelectorAll('.kpi-value').forEach(function (el) {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(10px)';
    el.style.transition = 'opacity .4s ease, transform .4s ease';
  });

  setTimeout(function () {
    document.querySelectorAll('.kpi-value').forEach(function (el, i) {
      setTimeout(function () {
        el.style.opacity   = '1';
        el.style.transform = 'none';
      }, i * 80);
    });
  }, 100);

  // ── Stagger card animations ──
  const cards = document.querySelectorAll('.card, .mission-card, .kpi-card');
  cards.forEach(function (card, i) {
    card.style.opacity   = '0';
    card.style.transform = 'translateY(12px)';
    card.style.transition = 'opacity .35s ease, transform .35s ease';
    setTimeout(function () {
      card.style.opacity   = '1';
      card.style.transform = 'none';
    }, 60 + i * 40);
  });

  // ── Active nav highlight fix ──
  document.querySelectorAll('.nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });

  // ── Set today's date for date inputs without value ──
  document.querySelectorAll('input[type="date"]').forEach(function (inp) {
    if (!inp.value) {
      const today = new Date().toISOString().split('T')[0];
      inp.setAttribute('placeholder', today);
    }
  });

});
