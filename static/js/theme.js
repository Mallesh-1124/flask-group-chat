const toggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const saved = localStorage.getItem('theme');
if (saved) html.dataset.theme = saved;
toggle?.addEventListener('click', () => {
  const cur = html.dataset.theme || 'light';
  const next = cur === 'light' ? 'dark' : 'light';
  html.dataset.theme = next;
  localStorage.setItem('theme', next);
  toggle.textContent = next === 'dark' ? '☀️' : '🌙';
});