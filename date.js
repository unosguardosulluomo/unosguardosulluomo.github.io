(function(){
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

  if(location.pathname.endsWith('article-scudo-parlamentare.html')){
    const hero=document.querySelector('.article-hero img');
    if(hero){
      hero.src='https://archivio.quirinale.it/bookreader//la_costituzione_volume_cosentino/LA_COSTITUZIONE_DELLA_REPUBBLICA_ITALIANA_121.jpg';
      hero.alt='La Costituzione della Repubblica italiana';
      const caption=hero.closest('figure')?.querySelector('figcaption');
      if(caption) caption.textContent='La Costituzione della Repubblica italiana. Archivio storico della Presidenza della Repubblica.';
    }
  }
})();