(function(){
  const now=new Date();
  const months=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  const d=`${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
  document.querySelectorAll('.current-date').forEach(el=>{el.textContent=d; el.setAttribute('datetime', now.toISOString().slice(0,10));});
})();