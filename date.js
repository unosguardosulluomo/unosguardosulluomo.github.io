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
          image.src='https://iicsanfrancisco.esteri.it/wp-content/uploads/2024/02/300px-Ieri_oggi_domani_primo_episodio.jpg';
          image.alt='Sophia Loren e Marcello Mastroianni nell’episodio Adelina di Ieri, oggi, domani';
        }
        if(caption){
          caption.innerHTML='Adelina e Carmine nel primo episodio di <em>Ieri, oggi, domani</em> (Vittorio De Sica, 1963). Immagine: Istituto Italiano di Cultura di San Francisco – Ministero degli Affari Esteri e della Cooperazione Internazionale.';
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

  const sigHref='article-sigfrido-ultima-battaglia.html';
  const sigImage='https://www.gedistatic.it/content/gnn/img/lastampa/2026/04/30/132759559-cb1ffd4e-50de-409a-938c-37af4bdceb2e.jpg';

  if((path==='/' || path.endsWith('/index.html')) && !document.getElementById('sigfrido-home')){
    const section=[...document.querySelectorAll('section.story-grid')].find(s=>s.getAttribute('aria-label')==='Politica italiana');
    if(section){
      const card=document.createElement('article');
      card.className='story-card';
      card.id='sigfrido-home';
      card.innerHTML=`<a class="story-image" href="${sigHref}"><img src="${sigImage}" alt="Sigfrido Ranucci" loading="lazy"></a><p class="eyebrow">Informazione, giustizia e potere</p><h3><a class="headline-link" href="${sigHref}">SIGFRIDO E L’ULTIMA BATTAGLIA</a></h3><p>Oltre 220 azioni legali, Report, politica, Rai, audience e il confine tra inchiesta e spettacolo del conflitto.</p><a class="read-more" href="${sigHref}">Leggi l’indagine →</a>`;
      section.prepend(card);
    }
  }

  if((path.endsWith('/indagini.html') || path.endsWith('indagini.html')) && !document.getElementById('sigfrido-ultima-battaglia')){
    const list=document.querySelector('.article-list');
    if(list){
      const item=document.createElement('article');
      item.id='sigfrido-ultima-battaglia';
      item.dataset.category='politica-italiana';
      item.dataset.topics='ranucci report rai querele informazione giustizia politica audience mediaset';
      item.innerHTML=`<a class="story-image" href="${sigHref}"><img src="${sigImage}" alt="Sigfrido Ranucci" loading="lazy"></a><div class="article-copy"><p class="eyebrow">Politica italiana</p><h2><a class="headline-link" href="${sigHref}">SIGFRIDO E L’ULTIMA BATTAGLIA</a></h2><p>Oltre 220 azioni legali, Report, politica, Rai, audience e potere mediatico: quando il conflitto diventa parte del prodotto.</p><div class="topic-list"><span>Ranucci</span><span>Report</span><span>Rai</span><span>Querele</span><span>Informazione</span></div><a class="read-more" href="${sigHref}">Leggi l’indagine →</a></div>`;
      list.prepend(item);
    }
  }

  const dubHref='article-dublinati.html';
  const dubImage='https://commons.wikimedia.org/wiki/Special:Redirect/file/Voting_session_at_the_European_Parliament_-_54056837075.jpg?width=1400';

  if(path==='/' || path.endsWith('/index.html')){
    const politics=[...document.querySelectorAll('section.story-grid')].find(s=>s.getAttribute('aria-label')==='Politica italiana');
    if(politics && !document.getElementById('dublinati-home')){
      const card=document.createElement('article');
      card.className='story-card';
      card.id='dublinati-home';
      card.innerHTML=`<a class="story-image" href="${dubHref}"><img src="${dubImage}" alt="Dossier Dublinati" loading="lazy"></a><p class="eyebrow">Politica italiana • Europa</p><h3><a class="headline-link" href="${dubHref}">DUBLINATI — IL BOOMERANG CHE ARRIVA DA LONTANO</a></h3><p>Schlein, Meloni, AMMR, Ceuta e il compromesso europeo che riporta i trasferimenti al centro dello scontro politico.</p><a class="read-more" href="${dubHref}">Leggi l’indagine →</a>`;
      politics.prepend(card);
    }
    const lead=document.querySelector('.lead-grid');
    if(lead && !document.getElementById('dublinati-evidenza')){
      const side=lead.querySelector('aside');
      if(side){
        const item=document.createElement('article');
        item.className='side-story';
        item.id='dublinati-evidenza';
        item.innerHTML=`<a class="story-image" href="${dubHref}"><img src="${dubImage}" alt="Dossier Dublinati" loading="lazy"></a><p class="eyebrow">Politica italiana • Europa</p><h2><a class="headline-link" href="${dubHref}">DUBLINATI</a></h2><p>Il boomerang che arriva da lontano: Schlein, Meloni, AMMR e Ceuta.</p><a class="read-more" href="${dubHref}">Leggi →</a>`;
        side.prepend(item);
      }
    }
  }

  if((path.endsWith('/indagini.html') || path.endsWith('indagini.html')) && !document.getElementById('dublinati')){
    const list=document.querySelector('.article-list');
    if(list){
      const item=document.createElement('article');
      item.id='dublinati';
      item.dataset.category='politica-italiana';
      item.dataset.topics='dublinati schlein meloni amm r ammr ceuta albania unione-europea migrazione';
      item.innerHTML=`<a class="story-image" href="${dubHref}"><img src="${dubImage}" alt="Dossier Dublinati" loading="lazy"></a><div class="article-copy"><p class="eyebrow">Politica italiana • Europa</p><h2><a class="headline-link" href="${dubHref}">DUBLINATI — IL BOOMERANG CHE ARRIVA DA LONTANO</a></h2><p>Dublino, AMMR, voto del 2024, Albania e ripartenza dei trasferimenti nel 2026: chi ha costruito il sistema che oggi tutti denunciano?</p><div class="topic-list"><span>Dublinati</span><span>Schlein</span><span>Meloni</span><span>AMMR</span><span>Ceuta</span></div><a class="read-more" href="${dubHref}">Leggi l’indagine →</a></div>`;
      list.prepend(item);
    }
  }
})();