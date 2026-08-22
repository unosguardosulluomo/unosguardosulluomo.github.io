(function(){
  const SITE='https://unosguardosulluomo.github.io';
  const BRAND='Uno Sguardo sull’Uomo';
  const BRAND_ALIASES=['UNO SGUARDO SULL\'UOMO','unosguardosulluomo'];
  const cleanPath=location.pathname.endsWith('/index.html') ? '/' : location.pathname;
  const canonicalUrl=SITE + (cleanPath.startsWith('/') ? cleanPath : '/' + cleanPath);
  const categoryMap={
    'politica italiana':'archivio-politica-italiana.html',
    'politica internazionale':'archivio-politica-internazionale.html',
    'economia':'archivio-economia.html',
    'società':'archivio-societa.html'
  };
  const monthMap={
    gennaio:'01',febbraio:'02',marzo:'03',aprile:'04',maggio:'05',giugno:'06',
    luglio:'07',agosto:'08',settembre:'09',ottobre:'10',novembre:'11',dicembre:'12'
  };

  let canonical=document.querySelector('link[rel="canonical"]');
  if(!canonical){
    canonical=document.createElement('link');
    canonical.rel='canonical';
    document.head.appendChild(canonical);
  }
  canonical.href=canonicalUrl;

  let ogSiteName=document.querySelector('meta[property="og:site_name"]');
  if(!ogSiteName){
    ogSiteName=document.createElement('meta');
    ogSiteName.setAttribute('property','og:site_name');
    document.head.appendChild(ogSiteName);
  }
  ogSiteName.content='UNO SGUARDO SULL\'UOMO';

  const description=document.querySelector('meta[name="description"]')?.content || '';
  const ogImage=document.querySelector('meta[property="og:image"]')?.content || `${SITE}/assets/testata.webp`;
  const ogType=document.querySelector('meta[property="og:type"]')?.content || '';
  const h1=document.querySelector('h1')?.textContent?.replace(/\s+/g,' ').trim();
  const title=h1 || document.title.replace(/\s+[—|-]\s+Uno Sguardo sull[’']Uomo.*$/i,'').trim();

  const categoryLabel=document.querySelector('.category-label');
  const categoryName=categoryLabel?.textContent?.replace(/\s+/g,' ').trim() || '';
  const categoryKey=categoryName.toLocaleLowerCase('it-IT');
  const categoryPath=categoryMap[categoryKey];
  if(categoryLabel && categoryPath) categoryLabel.href=categoryPath;

  const explicitTime=document.querySelector('.article-header time[datetime], .article-meta time[datetime], article time[datetime]');
  let datePublished=explicitTime?.getAttribute('datetime') || undefined;
  if(!datePublished){
    const metaTexts=[...document.querySelectorAll('.article-meta span')].map(el=>el.textContent.trim());
    const dateText=metaTexts.find(text=>/^\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+\d{4}$/u.test(text));
    if(dateText){
      const match=dateText.toLocaleLowerCase('it-IT').match(/^(\d{1,2})\s+([a-zà-ÿ]+)\s+(\d{4})$/u);
      if(match && monthMap[match[2]]) datePublished=`${match[3]}-${monthMap[match[2]]}-${String(match[1]).padStart(2,'0')}`;
    }
  }

  const keywords=[...document.querySelectorAll('.topic-list span')]
    .map(el=>el.textContent.replace(/\s+/g,' ').trim())
    .filter(Boolean);

  const publisher={
    '@type':['Organization','NewsMediaOrganization'],
    '@id':`${SITE}/#organization`,
    name:BRAND,
    alternateName:BRAND_ALIASES,
    url:`${SITE}/`,
    description:'Progetto editoriale indipendente italiano di approfondimento: indagini, dati, documenti e ricostruzione dei fatti oltre la narrazione.',
    email:'mailto:unosguardosulluomo@gmail.com',
    logo:{'@type':'ImageObject',url:`${SITE}/assets/testata.webp`},
    sameAs:[
      'https://www.facebook.com/profile.php?id=61593043131759',
      'https://www.linkedin.com/company/unosguardosulluomo/'
    ]
  };

  const website={
    '@type':'WebSite',
    '@id':`${SITE}/#website`,
    url:`${SITE}/`,
    name:BRAND,
    alternateName:BRAND_ALIASES,
    description:'Indagini, dati e documenti per osservare i fatti oltre la narrazione.',
    publisher:{'@id':`${SITE}/#organization`},
    inLanguage:'it-IT'
  };

  function breadcrumb(items){
    return {
      '@type':'BreadcrumbList',
      itemListElement:items.map((item,index)=>({
        '@type':'ListItem',position:index+1,name:item.name,item:item.url
      }))
    };
  }

  let data;
  if(ogType==='article' || document.querySelector('.article-page')){
    const article={
      '@type':'NewsArticle',
      '@id':`${canonicalUrl}#article`,
      headline:title,
      description:description,
      mainEntityOfPage:{'@type':'WebPage','@id':canonicalUrl},
      url:canonicalUrl,
      image:[ogImage],
      inLanguage:'it-IT',
      isPartOf:{'@id':`${SITE}/#website`},
      publisher:{'@id':`${SITE}/#organization`},
      author:{'@type':'Organization',name:'Redazione Uno Sguardo sull’Uomo',url:`${SITE}/chi-siamo.html`}
    };
    if(datePublished) article.datePublished=datePublished;
    if(categoryName) article.articleSection=categoryName;
    if(keywords.length) article.keywords=keywords.join(', ');

    const crumbs=[{name:'Prima pagina',url:`${SITE}/`}];
    if(categoryPath) crumbs.push({name:categoryName,url:`${SITE}/${categoryPath}`});
    crumbs.push({name:title,url:canonicalUrl});

    data={'@context':'https://schema.org','@graph':[publisher,website,article,breadcrumb(crumbs)]};
  } else if(cleanPath==='/' || cleanPath===''){
    data={
      '@context':'https://schema.org',
      '@graph':[publisher,website]
    };
  } else if(document.querySelector('.archive-index, .archive-grid')){
    const page={
      '@type':'CollectionPage',
      '@id':`${canonicalUrl}#collection`,
      name:title,
      description:description,
      url:canonicalUrl,
      inLanguage:'it-IT',
      isPartOf:{'@id':`${SITE}/#website`},
      publisher:{'@id':`${SITE}/#organization`}
    };
    const crumbs=[{name:'Prima pagina',url:`${SITE}/`}];
    if(cleanPath.endsWith('/indagini.html') || cleanPath.endsWith('indagini.html')){
      crumbs.push({name:'Indagini',url:canonicalUrl});
    } else {
      crumbs.push({name:'Indagini',url:`${SITE}/indagini.html`},{name:title,url:canonicalUrl});
    }
    data={'@context':'https://schema.org','@graph':[publisher,website,page,breadcrumb(crumbs)]};
  } else {
    const page={
      '@type':'WebPage',
      '@id':`${canonicalUrl}#webpage`,
      name:title || document.title,
      description:description,
      url:canonicalUrl,
      inLanguage:'it-IT',
      isPartOf:{'@id':`${SITE}/#website`},
      publisher:{'@id':`${SITE}/#organization`}
    };
    data={'@context':'https://schema.org','@graph':[publisher,website,page]};
  }

  if(!document.querySelector('script[data-seo-schema]')){
    const schema=document.createElement('script');
    schema.type='application/ld+json';
    schema.dataset.seoSchema='true';
    schema.textContent=JSON.stringify(data);
    document.head.appendChild(schema);
  }
})();