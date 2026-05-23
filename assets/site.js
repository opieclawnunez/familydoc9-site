(() => {
  const root = document.documentElement;
  const nav = document.querySelector('[data-primary-nav]');
  const menuButton = document.querySelector('[data-menu-button]');
  const themeButton = document.querySelector('[data-theme-button]');
  const form = document.querySelector('[data-newsletter-form]');
  const status = document.querySelector('[data-form-status]');

  const savedTheme = localStorage.getItem('familydoc9-theme');
  const preferredDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (preferredDark ? 'dark' : 'light');
  root.dataset.theme = initialTheme;
  if (themeButton) themeButton.textContent = initialTheme === 'dark' ? 'Light mode' : 'Dark mode';

  menuButton?.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!expanded));
    nav?.classList.toggle('open', !expanded);
  });

  nav?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      menuButton?.setAttribute('aria-expanded', 'false');
    });
  });

  themeButton?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('familydoc9-theme', next);
    themeButton.textContent = next === 'dark' ? 'Light mode' : 'Dark mode';
  });

  const iconPaths = {
    pulse: 'M3 12h4l2-5 4 10 2-5h6',
    shield: 'M12 3 4.5 6v5.5c0 4.8 3 8.8 7.5 10.5 4.5-1.7 7.5-5.7 7.5-10.5V6L12 3z',
    heart: 'M12 20s-7-4.4-9.4-8.5C.7 8 2.6 5 5.8 5c1.8 0 3.1.9 4.2 2.4C11.1 5.9 12.4 5 14.2 5c3.2 0 5.1 3 3.2 6.5C19 15.6 12 20 12 20z',
    family: 'M8 11a2.8 2.8 0 1 0 0-5.6A2.8 2.8 0 0 0 8 11Zm8 0a2.3 2.3 0 1 0 0-4.6A2.3 2.3 0 0 0 16 11M4.5 20c.5-3.2 2.6-5 5.5-5s5 1.8 5.5 5M13.5 20c.3-2.4 1.7-4 4.5-4 2 0 3.2.8 3.5 4',
    book: 'M6 4.5A2.5 2.5 0 0 1 8.5 2H20v18H8.5A2.5 2.5 0 0 0 6 22V4.5Zm0 0C6 3.1 4.9 2 3.5 2H2v18h1.5C4.9 20 6 21.1 6 22',
    mail: 'M4 6h16v12H4z M4 7l8 6 8-6',
    globe: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm0 0c3 2.7 4.6 5.7 4.6 10S15 19.3 12 22c-3-2.7-4.6-5.7-4.6-10S9 4.7 12 2Zm-7 10h14',
    camera: 'M5 7h3l1.2-2h5.6L16 7h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Zm7 2.2A3.8 3.8 0 1 0 12 17a3.8 3.8 0 0 0 0-7.8Z',
    leaf: 'M20 4c-7 0-12.5 4.3-14.5 10.5-.7 2.2-.7 4.6 0 6.5 3.7-6 10-9.2 17-9.2-2.6-1.2-5-2.3-8.1-2.6',
    search: 'M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14Zm6-2 4 4',
    info: 'M12 17v-5m0-4h.01M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z',
    arrow: 'M5 12h14m-6-6 6 6-6 6',
    check: 'M4.5 12.5 9 17 19.5 6.5',
  };

  document.querySelectorAll('[data-icon]').forEach((node) => {
    const name = node.getAttribute('data-icon');
    const path = iconPaths[name] || iconPaths.info;
    node.classList.add('icon-mark');
    node.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${path}"></path></svg>`;
  });

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (status) {
      status.textContent = 'Thanks — this demo form is ready to connect to your email provider.';
      status.style.color = 'var(--accent-2)';
    }
    form.reset();
  });
})();