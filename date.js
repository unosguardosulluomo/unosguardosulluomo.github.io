const today = new Date();
const isoDate = new Intl.DateTimeFormat('en-CA', {year:'numeric',month:'2-digit',day:'2-digit',timeZone:'Europe/Rome'}).format(today);
const italianDate = new Intl.DateTimeFormat('it-IT', {day:'numeric',month:'long',year:'numeric',timeZone:'Europe/Rome'}).format(today);
document.querySelectorAll('.current-date').forEach((element)=>{element.dateTime=isoDate;element.textContent=italianDate;});

if (!document.querySelector('link[href="editorial-rules.css"]')) {const editorialStyles=document.createElement('link');editorialStyles.rel='stylesheet';editorialStyles.href='editorial-rules.css?v=20260812-1';document.head.appendChild(editorialStyles);}

const spainArticleHref='article-controlli-italia-spagna.html';
const spainImage='https://cdn-acn.watchity.net/acn/images/c864b72a-8fa4-4aaf-b9b6-95172543e4eb/b6f0cf97-9cf6-454a-b030-073290774247/b6f0cf97-9cf6-454a-b030-073290774247_medium.jpeg';
document.querySelectorAll(`a[href="${spainArticleHref}"] img`).forEach((img)=>{img.src=spainImage;img.alt='Passeggeri al Terminal 1 dell’aeroporto di Barcellona';});
if(window.location.pathname.endsWith('/article-controlli-italia-spagna.html')||window.location.pathname.endsWith(spainArticleHref)){const hero=document.querySelector('.article-hero img');if(hero){hero.src=spainImage;hero.alt='Passeggeri al Terminal 1 dell’aeroporto di Barcellona';}const caption=document.querySelector('.article-hero figcaption');if(caption)caption.textContent='Passeggeri al Terminal 1 dell’aeroporto di Barcellona. Foto: Carola López / ACN - Catalan News.';const ogImage=document.querySelector('meta[property="og:image"]');if(ogImage)ogImage.setAttribute('content',spainImage);const ogAlt=document.querySelector('meta[property="og:image:alt"]');if(ogAlt)ogAlt.setAttribute('content','Passeggeri al Terminal 1 dell’aeroporto di Barcellona');}

// Indagine Lega: immagine editoriale approvata e presenza nell'archivio Indagini.
const legaHref='article-lega-governatori.html';
const legaImage='assets/lega-governatori.jpg';
if(window.location.pathname.endsWith('/article-lega-governatori.html')||window.location.pathname.endsWith(legaHref)){
  const header=document.querySelector('.article-header');
  if(header && !document.querySelector('.article-hero')){
    const figure=document.createElement('figure');figure.className='article-hero';
    figure.innerHTML=`<img src="${legaImage}" alt="Lega a un bivio: tornano i governatori?"><figcaption>Elaborazione grafica editoriale — Uno Sguardo sull’Uomo.</figcaption>`;
    header.insertAdjacentElement('afterend',figure);
  }
  let og=document.querySelector('meta[property="og:image"]');if(!og){og=document.createElement('meta');og.setAttribute('property','og:image');document.head.appendChild(og);}og.setAttribute('content','https://unosguardosulluomo.github.io/assets/lega-governatori.jpg');
}

if(window.location.pathname.endsWith('/indagini.html')||window.location.pathname.endsWith('indagini.html')){
  const list=document.querySelector('.article-list');
  if(list && !document.getElementById('lega-governatori')){
    const card=document.createElement('article');card.id='lega-governatori';card.dataset.category='politica-italiana';card.dataset.topics='lega nord autonomia governatori salvini zaia fontana romeo';
    card.innerHTML=`<a class="story-image" href="${legaHref}"><img src="${legaImage}" alt="Lega a un bivio: tornano i governatori?" loading="lazy"></a><div class="article-copy"><p class="eyebrow">Politica italiana</p><h2><a class="headline-link" href="${legaHref}">Lega a un bivio: tornano i Governatori?</a></h2><p>Dopo anni di svolta sovranista, la Lega torna a fare i conti con le proprie origini. Territori, autonomia e governatori tornano al centro della partita.</p><div class="topic-list"><span>Lega</span><span>Nord</span><span>Autonomia</span><span>Governatori</span><span>Salvini</span></div><a class="read-more" href="${legaHref}">Leggi l’indagine →</a></div>`;
    list.prepend(card);
  }
}