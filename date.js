(function(){
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

  const nav=document.querySelector('.nav');
  if(nav && !nav.querySelector('a[href="contatti.html"]')){
    const contactLink=document.createElement('a');
    contactLink.href='contatti.html';
    contactLink.textContent='Contatti';
    if(location.pathname.endsWith('/contatti.html') || location.pathname.endsWith('contatti.html')) contactLink.setAttribute('aria-current','page');
    nav.appendChild(contactLink);
  }
})();
