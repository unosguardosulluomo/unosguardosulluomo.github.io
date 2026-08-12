(function(){
  const now=new Date();
  const months=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  const d=`${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
  document.querySelectorAll('.current-date').forEach(el=>{el.textContent=d; el.setAttribute('datetime', now.toISOString().slice(0,10));});

  const fbMobileFix=document.createElement('link');
  fbMobileFix.rel='stylesheet';
  fbMobileFix.href='mobile-fb-fix.css?v=20260812-1';
  document.head.appendChild(fbMobileFix);
})();