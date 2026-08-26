(function(){
  const seoScript=document.createElement('script');
  seoScript.src='seo.js?v=20260822-2';
  seoScript.defer=true;
  document.head.appendChild(seoScript);

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
  document.querySelectorAll('.current-date').forEach(el=>{
    el.textContent=d;
    el.setAttribute('datetime',now.toISOString().slice(0,10));
  });

  [
    ['mobile-fb-fix.css?v=20260812-1','stylesheet'],
    ['editorial-standard.css?v=20260812-1','stylesheet'],
    ['navigation.css?v=20260821-1','stylesheet']
  ].forEach(([href,rel])=>{
    const link=document.createElement('link');
    link.rel=rel;
    link.href=href;
    document.head.appendChild(link);
  });

  const path=location.pathname;
  const nav=document.querySelector('.nav');
  if(nav && !nav.querySelector('a[href="contatti.html"]')){
    const contactLink=document.createElement('a');
    contactLink.href='contatti.html';
    contactLink.textContent='Contatti';
    if(path.endsWith('/contatti.html') || path.endsWith('contatti.html')) contactLink.setAttribute('aria-current','page');
    nav.appendChild(contactLink);
  }

  if(path.endsWith('article-scudo-parlamentare.html')){
    const article68Fix=document.createElement('link');
    article68Fix.rel='stylesheet';
    article68Fix.href='article-68-fix.css?v=20260814-2';
    document.head.appendChild(article68Fix);

    const hero=document.querySelector('.article-hero img');
    if(hero){
      hero.src='https://archivio.quirinale.it/bookreader//la_costituzione_volume_cosentino/LA_COSTITUZIONE_DELLA_REPUBBLICA_ITALIANA_121.jpg';
      hero.alt='La Costituzione della Repubblica italiana';
      const caption=hero.closest('figure')?.querySelector('figcaption');
      if(caption) caption.textContent='La Costituzione della Repubblica italiana. Archivio storico della Presidenza della Repubblica.';
    }
  }

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
})();