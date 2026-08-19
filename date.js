(function(){
  const gaId='G-XMRPY5JL0Z';
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){window.dataLayer.push(arguments);};
  window.gtag('js',new Date());
  window.gtag('config',gaId);
  const gaScript=document.createElement('script');
  gaScript.async=true;
  gaScript.src=`https://www.googletagmanager.com/gtag/js?id=${gaId}`;
  document.head.appendChild(gaScript);

  const now=new Date();
  const months=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  const d=`${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
  document.querySelectorAll('.current-date').forEach(el=>{el.textContent=d; el.setAttribute('datetime', now.toISOString().slice(0,10));});

  const fbMobileFix=document.createElement('link');
  fbMobileFix.rel='stylesheet';
  fbMobileFix.href='mobile-fb-fix.css?v=20260812-1';
  document.head.appendChild(fbMobileFix);

  const editorialStandard=document.createElement('link');
  editorialStandard.rel='stylesheet';
  editorialStandard.href='editorial-standard.css?v=20260812-1';
  document.head.appendChild(editorialStandard);

  const cover='https://archivio.quirinale.it/bookreader//la_costituzione_volume_cosentino/LA_COSTITUZIONE_DELLA_REPUBBLICA_ITALIANA_121.jpg';
  const href='article-scudo-parlamentare.html';

  if(location.pathname.endsWith('article-scudo-parlamentare.html')){
    const article68Fix=document.createElement('link');
    article68Fix.rel='stylesheet';
    article68Fix.href='article-68-fix.css?v=20260814-2';
    document.head.appendChild(article68Fix);

    const hero=document.querySelector('.article-hero img');
    if(hero){
      hero.src=cover;
      hero.alt='La Costituzione della Repubblica italiana';
      const caption=hero.closest('figure')?.querySelector('figcaption');
      if(caption) caption.textContent='La Costituzione della Repubblica italiana. Archivio storico della Presidenza della Repubblica.';
    }
  }

  const path=location.pathname;

  if(path.endsWith('article-pickpocket-venezia.html')){
    const headings=[...document.querySelectorAll('h3')];
    const adelinaHeading=headings.find(h=>h.textContent.includes('Ieri, oggi, domani'));
    if(adelinaHeading){
      let node=adelinaHeading.nextElementSibling;
      while(node && node.tagName!=='FIGURE') node=node.nextElementSibling;
      if(node){
        const image=node.querySelector('img');
        const caption=node.querySelector('figcaption');
        if(image){
          image.src='https://it.wikipedia.org/wiki/Special:Redirect/file/Ieri_oggi_domani_primo_episodio.jpg';
          image.alt='Sophia Loren nei panni di Adelina nel primo episodio di Ieri, oggi, domani';
        }
        if(caption){
          caption.innerHTML='Adelina nel primo episodio di <em>Ieri, oggi, domani</em> (Vittorio De Sica, 1963). Fotogramma: Wikipedia, file “Ieri oggi domani primo episodio.jpg”. Riproduzione contestuale a fini di critica e discussione del film.';
        }
      }
    }
  }

  if((path==='/' || path.endsWith('/index.html')) && !document.getElementById('scudo-parlamentare-home')){
    const section=[...document.querySelectorAll('section.story-grid')].find(s=>s.getAttribute('aria-label')==='Politica italiana');
    if(section){
      const card=document.createElement('article');
      card.className='story-card';
      card.id='scudo-parlamentare-home';

      const imageLink=document.createElement('a');
      imageLink.className='story-image';
      imageLink.href=href;
      const image=document.createElement('img');
      image.src=cover;
      image.alt='La Costituzione della Repubblica italiana';
      image.loading='lazy';
      imageLink.appendChild(image);

      const eyebrow=document.createElement('p');
      eyebrow.className='eyebrow';
      eyebrow.textContent='Costituzione e Parlamento';

      const heading=document.createElement('h3');
      const headingLink=document.createElement('a');
      headingLink.className='headline-link';
      headingLink.href=href;
      headingLink.textContent='Da scudo contro il potere a scudo della parola?';
      heading.appendChild(headingLink);

      const summary=document.createElement('p');
      summary.textContent='Tre secoli di immunità parlamentare, dalle origini alla politica della comunicazione permanente.';

      const readMore=document.createElement('a');
      readMore.className='read-more';
      readMore.href=href;
      readMore.textContent='Leggi l’indagine →';

      card.append(imageLink,eyebrow,heading,summary,readMore);
      section.prepend(card);
    }
  }

  if((path.endsWith('/indagini.html') || path.endsWith('indagini.html')) && !document.getElementById('scudo-parlamentare')){
    const list=document.querySelector('.article-list');
    if(list){
      const item=document.createElement('article');
      item.id='scudo-parlamentare';
      item.dataset.category='politica-italiana';
      item.dataset.topics='costituzione parlamento immunita prima-repubblica';

      const imageLink=document.createElement('a');
      imageLink.className='story-image';
      imageLink.href=href;
      const image=document.createElement('img');
      image.src=cover;
      image.alt='La Costituzione della Repubblica italiana';
      image.loading='lazy';
      imageLink.appendChild(image);

      const copy=document.createElement('div');
      copy.className='article-copy';

      const eyebrow=document.createElement('p');
      eyebrow.className='eyebrow';
      eyebrow.textContent='Politica italiana';

      const heading=document.createElement('h2');
      const headingLink=document.createElement('a');
      headingLink.className='headline-link';
      headingLink.href=href;
      headingLink.textContent='DA SCUDO CONTRO IL POTERE A SCUDO DELLA PAROLA?';
      heading.appendChild(headingLink);

      const summary=document.createElement('p');
      summary.textContent='Tre secoli di immunità parlamentare: 1689, 1789, 1948, la svolta del 1993 e la politica della comunicazione permanente.';

      const topics=document.createElement('div');
      topics.className='topic-list';
      ['Costituzione','Parlamento','Immunità'].forEach(t=>{const s=document.createElement('span'); s.textContent=t; topics.appendChild(s);});

      const readMore=document.createElement('a');
      readMore.className='read-more';
      readMore.href=href;
      readMore.textContent='Leggi l’indagine →';

      copy.append(eyebrow,heading,summary,topics,readMore);
      item.append(imageLink,copy);
      list.prepend(item);
    }
  }
})();