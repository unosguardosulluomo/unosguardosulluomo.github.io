(function () {
  const buttons = Array.from(document.querySelectorAll('[data-filter]'));
  const articles = Array.from(document.querySelectorAll('.article-list article[data-category]'));
  if (!buttons.length || !articles.length) return;

  function applyFilter(category) {
    articles.forEach((article) => {
      article.hidden = category !== 'tutte' && article.dataset.category !== category;
    });
    buttons.forEach((button) => {
      const active = button.dataset.filter === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    const url = new URL(window.location.href);
    if (category === 'tutte') url.searchParams.delete('categoria');
    else url.searchParams.set('categoria', category);
    history.replaceState(null, '', url);
  }

  buttons.forEach((button) => button.addEventListener('click', () => applyFilter(button.dataset.filter)));
  const requested = new URLSearchParams(window.location.search).get('categoria');
  applyFilter(buttons.some((button) => button.dataset.filter === requested) ? requested : 'tutte');
})();
