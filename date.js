const today = new Date();
const isoDate = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  timeZone: 'Europe/Rome'
}).format(today);
const italianDate = new Intl.DateTimeFormat('it-IT', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'Europe/Rome'
}).format(today);

document.querySelectorAll('.current-date').forEach((element) => {
  element.dateTime = isoDate;
  element.textContent = italianDate;
});

// Regole editoriali stabili: vengono applicate a tutte le pagine del sito.
if (!document.querySelector('link[href="editorial-rules.css"]')) {
  const editorialStyles = document.createElement('link');
  editorialStyles.rel = 'stylesheet';
  editorialStyles.href = 'editorial-rules.css?v=20260812-1';
  document.head.appendChild(editorialStyles);
}

// Indagine Italia-Spagna: usa sempre la foto editoriale approvata del T1 del 10 agosto.
const spainArticleHref = 'article-controlli-italia-spagna.html';
const spainImage = 'assets/aeroporto-t1-10-agosto.jpg';

document.querySelectorAll(`a[href="${spainArticleHref}"] img`).forEach((img) => {
  img.src = spainImage;
  img.alt = 'Passeggeri al Terminal 1 di un aeroporto spagnolo il 10 agosto 2026';
});

if (window.location.pathname.endsWith('/article-controlli-italia-spagna.html') || window.location.pathname.endsWith(spainArticleHref)) {
  const hero = document.querySelector('.article-hero img');
  if (hero) {
    hero.src = spainImage;
    hero.alt = 'Passeggeri al Terminal 1 di un aeroporto spagnolo il 10 agosto 2026';
  }

  const caption = document.querySelector('.article-hero figcaption');
  if (caption) {
    caption.textContent = 'Terminal 1, 10 agosto 2026.';
  }

  const ogImage = document.querySelector('meta[property="og:image"]');
  if (ogImage) {
    ogImage.setAttribute('content', 'https://unosguardosulluomo.github.io/assets/aeroporto-t1-10-agosto.jpg');
  }

  const ogAlt = document.querySelector('meta[property="og:image:alt"]');
  if (ogAlt) {
    ogAlt.setAttribute('content', 'Passeggeri al Terminal 1 di un aeroporto spagnolo il 10 agosto 2026');
  }
}
