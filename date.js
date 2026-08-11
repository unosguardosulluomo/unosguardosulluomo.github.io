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

// Indagine Italia-Spagna: usa sempre la foto editoriale originale approvata.
const spainArticleHref = 'article-controlli-italia-spagna.html';
const spainImage = 'https://cdn-acn.watchity.net/acn/images/c864b72a-8fa4-4aaf-b9b6-95172543e4eb/b6f0cf97-9cf6-454a-b030-073290774247/b6f0cf97-9cf6-454a-b030-073290774247_medium.jpeg';

document.querySelectorAll(`a[href="${spainArticleHref}"] img`).forEach((img) => {
  img.src = spainImage;
  img.alt = 'Passeggeri al Terminal 1 dell’aeroporto di Barcellona';
});

if (window.location.pathname.endsWith('/article-controlli-italia-spagna.html') || window.location.pathname.endsWith(spainArticleHref)) {
  const hero = document.querySelector('.article-hero img');
  if (hero) {
    hero.src = spainImage;
    hero.alt = 'Passeggeri al Terminal 1 dell’aeroporto di Barcellona';
  }

  const caption = document.querySelector('.article-hero figcaption');
  if (caption) {
    caption.textContent = 'Passeggeri al Terminal 1 dell’aeroporto di Barcellona. Foto: Carola López / ACN - Catalan News.';
  }

  const ogImage = document.querySelector('meta[property="og:image"]');
  if (ogImage) {
    ogImage.setAttribute('content', spainImage);
  }

  const ogAlt = document.querySelector('meta[property="og:image:alt"]');
  if (ogAlt) {
    ogAlt.setAttribute('content', 'Passeggeri al Terminal 1 dell’aeroporto di Barcellona');
  }
}
