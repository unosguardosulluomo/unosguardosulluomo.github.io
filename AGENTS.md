# Regole operative del progetto

## Regola di apertura

Prima di qualsiasi intervento leggere questo file e verificare lo stato corrente del repository. Non lavorare basandosi soltanto sulla memoria o su riepiloghi precedenti.

## Flusso Git obbligatorio

1. Aggiornare `main` senza modificarlo direttamente.
2. Creare un branch con prefisso `codex/`.
3. Eseguire modifiche circoscritte.
4. Controllare diff, link, metadati e comportamento mobile.
5. Aprire una pull request.
6. Eseguire il merge soltanto dopo verifica esplicita.

## Vincoli editoriali e tecnici

- Non abbreviare, riscrivere o rimuovere contenuti e fonti durante interventi tecnici.
- Trattare data di pubblicazione, categoria, titolo, immagine, descrizione, argomenti e URL come metadati strutturali.
- Per tutti i dossier usare `Geopolitica` come macroargomento editoriale fisso. Assegnare come microargomento una sola categoria principale tra `Politica italiana`, `Politica internazionale`, `Economia` e `Società`; gli argomenti più specifici restano tag descrittivi. Rendere questa gerarchia coerente nei metadati e nei dati strutturati Schema.org, mantenendo il microargomento nelle pagine archivio e nel percorso visibile del dossier. Non creare una pagina hub o una voce di menu dedicata al macroargomento senza una richiesta editoriale esplicita.
- Per i nuovi dossier e per quelli il cui indirizzo viene modificato, costruire lo slug SEO includendo nell'ordine macroarea, microarea e parole chiave essenziali del titolo: `article-<macroarea>-<microarea>-<titolo>.html`. Conservare gli indirizzi precedenti soltanto come reindirizzamenti `noindex` verso il nuovo canonical.
- La data di pubblicazione coincide con il primo inserimento Git del dossier e non cambia in seguito.
- Conservare separatamente la data di pubblicazione e l'eventuale data di aggiornamento; una correzione successiva non sostituisce mai la data originale.
- Ordinare archivi e sezioni cronologiche dalla pubblicazione più recente alla più vecchia.
- La home è una prima pagina selettiva; Indagini mostra le tre pubblicazioni più recenti di ogni categoria; gli archivi conservano tutte le pubblicazioni.
- Nei dossier e nelle indagini, alla prima occorrenza di ogni acronimo o sigla scrivere prima la denominazione per esteso e poi l'acronimo tra parentesi, per esempio "Ministero delle infrastrutture e dei trasporti (MIT)". Nelle occorrenze successive si può usare il solo acronimo.
- Evitare copie indipendenti dello stesso dato e override JavaScript che riscrivano contenuti editoriali dopo il caricamento.
- Verificare sempre JavaScript e CSS globali, link locali, canonical, Open Graph, Schema.org, sitemap e resa mobile.
- Nelle sezioni delle fonti citare ente o autore, titolo del documento o dell'articolo e data quando disponibile, senza mostrare URL e senza creare collegamenti esterni cliccabili. Conservare gli indirizzi usati per la verifica nel materiale di lavoro, non nella pagina pubblicata.
- Nelle didascalie delle immagini prodotte dalla testata usare soltanto la formula "Immagine prodotta da Uno Sguardo sull'Uomo", senza indicazioni sulla tecnica di produzione e senza precisazioni sulla natura reale o ricostruita della scena.
- Prima della pubblicazione sul sito o dell'inserimento in un dossier, applicare alle immagini prodotte dalla testata una filigrana visibile con la dicitura "UNO SGUARDO SULL'UOMO". Non applicare la filigrana della testata a fotografie o immagini provenienti da Wikipedia, Wikimedia Commons o altre fonti esterne: per queste conservare attribuzione, licenza e indicazioni richieste dalla fonte.
- Distinguere chiaramente tra modifica preparata, modifica presente nel repository e comportamento verificato sul sito pubblico.

## Regola SEO esecutiva per i dossier

- Prima di costruire un nuovo dossier, definire nel relativo file `editorial/*.json` un oggetto `seo` con `primaryQuery`, `searchIntent`, almeno tre `supportingQueries` e `serpCheckedAt`. Usare soltanto strumenti gratuiti: risultati Google, Google Trends e dati della proprietà Search Console. Per questa testata privilegiare intenti informativi di attualità o approfondimento; non applicare meccanicamente logiche di acquisto o SEO locale.
- Verificare gratuitamente i primi risultati della query principale e annotare un intento coerente con il tipo di pagina. Non inventare volumi di ricerca e non presentare stime non verificabili come dati.
- Inserire l'argomento principale nel titolo visibile, nel titolo SEO, nello slug dei nuovi indirizzi e nell'apertura. L'apertura deve dare subito al lettore la risposta o la tesi verificata, senza introduzioni generiche.
- Usare un titolo SEO descrittivo, autonomo e normalmente non superiore a 70 caratteri; puntare a circa 45-60 caratteri senza abbreviare impropriamente il titolo editoriale. Scrivere una descrizione specifica di 110-165 caratteri, ricavata da deck o apertura e non da formule promozionali generiche.
- Organizzare le sezioni attorno alle domande reali del lettore quando ciò è naturale. Dopo un'intestazione interrogativa, rispondere nella prima frase e poi sviluppare prove, dati, limiti e contraddittorio. Non trasformare forzatamente tutte le intestazioni in domande e non praticare keyword stuffing.
- Ogni dossier deve avere tre collegamenti statici a dossier realmente correlati, con testo descrittivo. I collegamenti vengono generati dai metadati editoriali e devono essere controllati prima della pubblicazione; non aggiungere collegamenti soltanto per raggiungere una quota.
- Dichiarare `width` e `height` per tutte le immagini locali. Caricare in modo differito le immagini sotto la prima schermata, ma non l'immagine principale. Conservare testo alternativo, attribuzioni, licenze e filigrane secondo le altre regole del progetto.
- Per ogni nuovo dossier eseguire `python scripts/build_search_visibility.py`, `python scripts/build_related_dossiers.py` e `python scripts/check_search_visibility.py`. La pull request non è pubblicabile se questi controlli falliscono o se la rigenerazione produce differenze non incluse.
- Una volta al mese esportare gratuitamente da Search Console query e pagine degli ultimi 90 giorni. Dare priorità alle pagine in posizione media 5-20, alle impressioni senza clic e alle esclusioni dall'indice. Aggiornare soltanto con modifiche sostanziali e conservare separatamente `datePublished` e `dateModified`.
- Link esterni autorevoli, citazioni e menzioni richiedono attività editoriale reale: dati originali, comunicazione alle fonti interessate e diffusione sui canali della testata. Non acquistare backlink, non usare directory prive di pubblico e non generare collegamenti artificiali.
