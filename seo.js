(function(){
  const SITE='https://unosguardosulluomo.github.io';
  const cleanPath=location.pathname.endsWith('/index.html') ? '/' : location.pathname;
  const canonicalUrl=SITE + (cleanPath.startsWith('/') ? cleanPath : '/' + cleanPath);

  let canonical=document.querySelector('link[rel="canonical"]');
  if(!canonical){
    canonical=document.createElement('link');
    canonical.rel='canonical';
    document.head.appendChild(canonical);
  }
  canonical.href=canonicalUrl;

  const description=document.querySelector('meta[name="description"]')?.content || '';
  const ogImage=document.querySelector('meta[property="og:image"]')?.content || `${SITE}/assets/testata.webp`;
  const ogType=document.querySelector('meta[property="og:type"]')?.content || '';
  const h1=document.querySelector('h1')?.textContent?.replace(/\s+/g,' ').trim();
  const title=h1 || document.title.replace(/\s+[—|-]\s+Uno Sguardo sull[’']Uomo.*$/i,'').trim();
  const articleTime=document.querySelector('.article-header time[datetime], .article-meta time[datetime], article time[datetime]');
  const datePublished=articleTime?.getAttribute('datetime') || document.querySelector('.current-date')?.getAttribute('datetime') || undefined;

  const publisher={
    '@type':'Organization',
    '@id':`${SITE}/#organization`,
    name:'Uno Sguardo sull’Uomo',
    url:`${SITE}/`,
    logo:{'@type':'ImageObject',url:`${SITE}/assets/testata.webp`}
  };

  let data;
  if(ogType==='article' || document.querySelector('.article-page')){
    data={
      '@context':'https://schema.org',
      '@type':'NewsArticle',
      headline:title,
      description:description,
      mainEntityOfPage:{'@type':'WebPage','@id':canonicalUrl},
      url:canonicalUrl,
      image:[ogImage],
      inLanguage:'it-IT',
      publisher:publisher,
      author:{'@type':'Organization',name:'Redazione Uno Sguardo sull’Uomo'}
    };
    if(datePublished) data.datePublished=datePublished;
  } else if(cleanPath==='/' || cleanPath===''){
    data={
      '@context':'https://schema.org',
      '@graph':[
        publisher,
        {
          '@type':'WebSite',
          '@id':`${SITE}/#website`,
          url:`${SITE}/`,
          name:'Uno Sguardo sull’Uomo',
          description:description,
          publisher:{'@id':`${SITE}/#organization`},
          inLanguage:'it-IT'
        }
      ]
    };
  } else if(document.querySelector('.archive-index, .archive-grid')){
    data={
      '@context':'https://schema.org',
      '@type':'CollectionPage',
      name:title,
      description:description,
      url:canonicalUrl,
      inLanguage:'it-IT',
      isPartOf:{'@type':'WebSite',url:`${SITE}/`,name:'Uno Sguardo sull’Uomo'}
    };
  } else {
    data={
      '@context':'https://schema.org',
      '@type':'WebPage',
      name:title || document.title,
      description:description,
      url:canonicalUrl,
      inLanguage:'it-IT',
      isPartOf:{'@type':'WebSite',url:`${SITE}/`,name:'Uno Sguardo sull’Uomo'}
    };
  }

  if(!document.querySelector('script[data-seo-schema]')){
    const schema=document.createElement('script');
    schema.type='application/ld+json';
    schema.dataset.seoSchema='true';
    schema.textContent=JSON.stringify(data);
    document.head.appendChild(schema);
  }
})();
