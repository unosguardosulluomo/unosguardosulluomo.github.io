(function(){
  const now=new Date();
  const months=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  const d=`${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
  document.querySelectorAll('.current-date').forEach(el=>{el.textContent=d; el.setAttribute('datetime', now.toISOString().slice(0,10));});

  const fbMobileFix=document.createElement('link');
  fbMobileFix.rel='stylesheet';
  fbMobileFix.href='mobile-fb-fix.css?v=20260812-1';
  document.head.appendChild(fbMobileFix);

  const confessioniImg='https://unsplash.com/photos/CheH_aaDkUM/download?force=true&w=1600';
  document.querySelectorAll('img[src*="photo-1677442136019-21780ecad995"]').forEach(img=>{
    img.src=confessioniImg;
    img.alt='Volto umano astratto composto da linee';
  });
  const confessioniHero=document.querySelector('article .article-hero img[src*="CheH_aaDkUM"]');
  if(confessioniHero){
    const caption=confessioniHero.closest('figure')?.querySelector('figcaption');
    if(caption) caption.textContent='Un volto umano ricostruito da linee: il confine visivo tra persona e intelligenza artificiale.';
  }
})();