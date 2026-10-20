"""Pubblica il dossier narrativo sulle primarie del campo largo."""

import email.utils
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"
D = {
    "slug": "article-geopolitica-politica-italiana-schlein-conte-primarie-campo-largo.html",
    "title": "CAMPO LARGO TUTTI PRONTI A VINCERE",
    "deck": "Le primarie tra Elly Schlein e Giuseppe Conte e il rischio di una coalizione incapace di sopravvivere alla sconfitta",
    "description": "L'investitura di Elly Schlein e la sfida di Giuseppe Conte trasformano le primarie del campo largo in una prova di forza dagli effetti asimmetrici sul Partito Democratico e sul Movimento 5 Stelle.",
    "datePublished": "2026-10-20",
    "dateModified": "2026-10-20",
    "dateLabel": "20 ottobre 2026",
    "category": "Politica italiana",
    "categoryPath": "archivio-politica-italiana.html",
    "image": "assets/campo-largo-schlein-conte-primarie.webp",
    "imageAlt": "Elly Schlein parla alla stampa circondata dai leader del campo largo, tra i quali Giuseppe Conte",
    "imageWidth": 1536,
    "imageHeight": 1024,
    "secondaryImage": "assets/campo-largo-riunione-politica.webp",
    "secondaryImageAlt": "Elly Schlein e Giuseppe Conte durante una riunione politica sul campo largo",
    "cardEyebrow": "Politica italiana • Campo largo • Primarie",
}
URL = SITE + D["slug"]


def esc(value):
    return html.escape(str(value), quote=True)


opening = [
    "Alla Nuvola di Roma, il 18 ottobre, il Partito Democratico non ha semplicemente indicato una candidata. Ha costruito un punto di non ritorno. Con 578 voti favorevoli, 3 contrari e 26 astensioni, l'Assemblea nazionale ha investito Elly Schlein della candidatura alla presidenza del Consiglio e l'ha mandata verso le eventuali primarie di coalizione con alle spalle un partito quasi unanime. Quando la segretaria ha aggiunto di essere pronta alla sfida con o senza primarie, il messaggio è diventato ancora più netto: il PD aveva già scelto, mentre il campo largo doveva ancora farlo.",
    "Due giorni dopo Giuseppe Conte ha preso atto di quella decisione e ha accettato la gara. Non ha annunciato che il Movimento 5 Stelle correrà da solo alle elezioni politiche. Ha detto che saranno gli elettori a scegliere tra lui e Schlein attraverso le primarie, trasformando così una trattativa tra gruppi dirigenti in una competizione pubblica per la guida dell'intera coalizione. Prima aveva proposto che entrambi i leader facessero un passo indietro a favore di una figura terza; respinta quella strada, ha deciso di presentarsi sulla pista scelta dal PD.",
    "È qui che comincia il vero dossier. Le primarie vengono raccontate come lo strumento capace di unire ciò che i partiti non sono riusciti a comporre al tavolo. Ma una votazione non produce soltanto un candidato: produce anche uno sconfitto. E lo sconfitto continuerà a controllare un partito senza il quale l'alleanza non può vincere né governare. Il campo largo cerca dunque una leadership comune con un metodo che, per funzionare, dovrebbe convincere uno dei due contendenti ad accettare una subordinazione che nessuno dei due può permettersi.",
    "Per esaminare questo passaggio assumiamo che vengano confermate le regole tradizionali delle primarie del centrosinistra: voto aperto, gazebo, identificazione degli elettori, dichiarazione di sostegno alla coalizione ed eventuale contributo simbolico. Il regolamento definitivo della consultazione non è stato ancora pubblicato, ma è precisamente quel modello, ormai parte dell'identità politica del centrosinistra, a determinare il peso simbolico della sfida. Non si tratta di un consiglio interno che distribuisce incarichi. Chi vince riceve un'investitura popolare che pretende di valere più delle gerarchie dei singoli partiti.",
    "Da questa asimmetria nasce la tesi dell'indagine. Schlein entra nella competizione per confermare una leadership che il PD considera già naturale; Conte entra per dimostrare che la dimensione del partito non basta a stabilire chi debba guidare la coalizione. Lei può ottenere una conferma. Lui, se prevale, può ottenere una consacrazione. E più la vittoria di Schlein viene presentata come inevitabile, maggiore sarà il rumore di un'eventuale caduta.",
]

sections = [
    ("la-gara", "LA GARA CHE DOVEVA UNIRE IL CAMPO LARGO", [
        "Il passaggio dalle trattative alle primarie non ha risolto il conflitto sulla leadership: gli ha dato una data, una procedura e un pubblico. Il PD arriva alla consultazione come il partito più grande della coalizione, con più voti, più amministratori locali, più circoli e una macchina abituata a organizzare gazebo. Il Movimento 5 Stelle (M5S) arriva con una struttura territoriale meno capillare, ma con un leader che ha già presieduto due governi e che può rivolgersi a un elettorato più ampio della propria organizzazione.",
        "La differenza non è secondaria perché le primarie aperte non pesano i voti in base ai seggi, agli iscritti o ai risultati delle ultime elezioni. Ogni partecipante ammesso alla consultazione dispone dello stesso voto. La forza parlamentare del PD resta essenziale per costruire una maggioranza, ma nel giorno dei gazebo non garantisce alla segretaria alcun vantaggio automatico. Conta la capacità di mobilitare persone, di attraversare i confini del proprio partito e di convincere elettori che non appartengono stabilmente a nessuna organizzazione.",
        "La stessa storia politica di Schlein contiene l'avvertimento. Nel 2023 Stefano Bonaccini prevalse tra gli iscritti, ma la consultazione aperta ribaltò il risultato e consegnò a lei la segreteria. Quel precedente non permette di prevedere l'esito di una sfida con Conte; dimostra però che il popolo delle primarie non coincide necessariamente con l'apparato che prepara la consultazione. Il metodo che ha legittimato Schlein può ora sottoporla alla prova più pericolosa.",
        "Il voto del 18 ottobre, proprio perché quasi unanime, alza ulteriormente la posta. Il PD non manda ai gazebo una candidata provvisoria: mette in gara la propria segretaria, la decisione dell'Assemblea e la pretesa di essere il baricentro dell'alternativa. Se Schlein vince, il partito vede confermato ciò che aveva già deciso. Se perde, non viene sconfitta soltanto una persona; viene smentita davanti allo stesso elettorato che dovrebbe riconoscere il PD come guida.",
        "Conte corre un rischio diverso. Una sconfitta lo lascerebbe presidente del M5S, titolare del simbolo e interlocutore necessario della coalizione. Potrebbe accettare la candidatura di Schlein senza consegnarle il Movimento, continuando a negoziare programma, liste e ministeri. Una sua vittoria, al contrario, gli consentirebbe di presentarsi come il leader scelto non solo dai propri elettori, ma anche da una parte del popolo democratico. Moralmente e politicamente guiderebbe alle elezioni anche il partito che non dirige.",
        "Le primarie hanno quindi effetti asimmetrici prima ancora che venga espresso un voto. Per Conte sono una possibilità di espansione; per Schlein sono un esame di sopravvivenza politica. La procedura nata per unire il campo largo comincia col distribuire ai due contendenti premi e rischi completamente diversi.",
    ]),
    ("ferrari-cinquecento", "LA FERRARI E LA CINQUECENTO", [
        "L'immagine più semplice è quella di una Ferrari e di una Cinquecento schierate sulla stessa pista. La Ferrari è il PD: più grande, organizzato, radicato, allenato alle primarie. La Cinquecento è il M5S: meno attrezzato sul territorio e nato, almeno in origine, contro i rituali dei partiti tradizionali. Se la Ferrari vince, il risultato appare naturale. Se vince la Cinquecento, la gara cambia significato e diventa un giudizio sulla macchina che avrebbe dovuto dominare.",
        "Una vittoria di Schlein confermerebbe il pronostico e le permetterebbe di sommare il mandato dell'Assemblea a un'investitura popolare di coalizione. Conte potrebbe però ricordare di aver corso sulla pista storica dell'avversaria e resterebbe alla guida del Movimento. La sconfitta ne ridimensionerebbe l'ambizione, non ne cancellerebbe il potere. Il giorno dopo avrebbe ancora parlamentari, voti e la possibilità di condizionare ogni scelta della candidata comune.",
        "Se prevalesse Conte, la scena sarebbe opposta: potrebbe togliersi il casco e dire a Schlein di averla battuta con una Cinquecento, sulla sua pista e con le sue regole. Non sarebbe una semplice differenza numerica. Sarebbe la dimostrazione che il principale partito dell'opposizione, pur disponendo dell'apparato più forte, non è riuscito a far riconoscere la propria segretaria come guida del suo stesso campo politico. La vittoria della Ferrari sarebbe ordinaria; quella della Cinquecento diventerebbe un terremoto.",
        {"quote": "Ti ho battuta con una Cinquecento, sulla tua pista e con le tue regole."},
        "L'apertura del voto amplifica questa incertezza. L'identificazione al gazebo verifica chi vota, non perché vota. Una dichiarazione di sostegno alla coalizione non può impedire a elettori occasionali, simpatizzanti di altre forze o persino avversari di scegliere il candidato ritenuto più debole alle elezioni generali. Non esistono elementi per affermare che una mobilitazione strategica determinerà il risultato. Esiste però la possibilità tecnica e politica che una consultazione aperta venga attraversata da interessi estranei alla fedeltà dei partiti.",
        "Se il margine fosse ristretto, anche una consultazione formalmente corretta potrebbe lasciare spazio a contestazioni. Lo sconfitto potrebbe chiamare in causa l'organizzazione dei gazebo, la diversa capacità di mobilitazione o la presenza di voti esterni. Il punto non è delegittimare in anticipo le primarie, ma capire il loro limite: attribuiscono al vincitore una potente legittimazione simbolica senza obbligare lo sconfitto e il suo partito a rinunciare alla propria autonomia.",
        "Neppure gli altri alleati saranno spettatori neutrali. Alleanza Verdi e Sinistra (AVS), Italia Viva, le formazioni socialiste, le aree civiche e gli amministratori locali valuteranno affinità, convenienza elettorale e spazio disponibile in un eventuale governo. Non è affatto certo che tutti preferiscano Schlein. Conte ha già guidato esecutivi composti da forze diverse e può apparire più disposto a distribuire responsabilità; Schlein, dopo aver difeso la propria candidatura e respinto il passo indietro reciproco, può essere letta come determinata oppure come una leader intenzionata ad accentrare il comando.",
        "Dietro la scelta del candidato si muove quindi una trattativa sul potere futuro. Sostenere l'uno o l'altra significa anche decidere chi avrà più forza nella distribuzione dei ministeri, delle candidature e delle priorità. Prima ancora che esista un governo, il campo largo sta già negoziando chi ne controllerà le stanze.",
    ]),
    ("giorno-dopo", "IL GIORNO DOPO LE PRIMARIE", [
        "Il risultato migliore per il PD sarebbe una vittoria larga di Schlein. La segretaria potrebbe presentarsi come la guida scelta dal partito maggiore e riconosciuta dall'intero elettorato della coalizione. La contesa sulla candidatura si chiuderebbe, ma non scomparirebbe il problema del governo. Conte continuerebbe a dirigere un Movimento indispensabile per la maggioranza e avrebbe la forza necessaria per negoziare ministeri, programma, candidature e votazioni parlamentari. Il vincitore avrebbe ancora bisogno dello sconfitto per arrivare a Palazzo Chigi e per restarci.",
        "Una vittoria di misura sarebbe molto più insidiosa. Schlein otterrebbe formalmente la candidatura, mentre Conte potrebbe rivendicare di rappresentare quasi metà dell'elettorato mobilitato. Il campo largo nascerebbe con una leader ufficiale e un contropotere dotato di una legittimazione quasi equivalente. Ogni decisione successiva, dalla composizione delle liste alla distribuzione degli incarichi, verrebbe letta alla luce di quel rapporto di forza. Le primarie non chiuderebbero la competizione: si limiterebbero ad assegnarle un numero.",
        "La vittoria di Conte produrrebbe invece l'effetto più violento. Schlein resterebbe formalmente segretaria, ma avrebbe perso davanti agli elettori la gara per guidare la coalizione. Nel PD la domanda sulle dimissioni diventerebbe inevitabile, le correnti tornerebbero a misurarsi e gli avversari interni contesterebbero la strategia che ha trasformato una leadership quasi unanime dentro il partito in una leadership respinta fuori dal partito.",
        "La sconfitta non dissolverebbe giuridicamente il PD. Ne produrrebbe però la distruzione politica nella forma costruita attorno a Schlein. Il partito dovrebbe scegliere se sostenere senza riserve un candidato proveniente dal M5S, aprire una resa dei conti durante la campagna elettorale o chiedere compensazioni tali da ridurre l'autonomia del vincitore. La coalizione avrebbe trovato il proprio capo proprio nel momento in cui il suo motore principale comincia a essere smontato.",
        "Per Conte sarebbe una consacrazione accompagnata da un problema immediato. Avrebbe conquistato il volante di un'alleanza traumatizzata dalla sua stessa vittoria e continuerebbe ad avere bisogno del PD per ogni passaggio decisivo. Il partito sconfitto potrebbe rispettare l'esito delle primarie senza trasformarsi in un'organizzazione docile. Potrebbe sostenere il candidato comune e, nello stesso tempo, limitarne ogni scelta attraverso i gruppi parlamentari e il peso elettorale.",
        "In nessuno dei tre scenari la consultazione genera un'autorità realmente comune. Una vittoria larga riduce la contesa ma non subordina il M5S; una vittoria stretta istituzionalizza due leadership concorrenti; una vittoria di Conte apre nel PD una crisi che indebolisce la stessa coalizione affidata al vincitore. Il giorno dopo le primarie, il campo largo avrà certamente un candidato. Non è detto che abbia una catena di comando.",
    ]),
    ("coalizione", "UNA COALIZIONE CHE NON SA PERDERE", [
        "L'idea di collocare il programma prima del leader è ragionevole, ma non elimina questa fragilità. Un documento comune può registrare formule condivise e rinviare le decisioni più difficili. Governare significa trasformare quelle formule in bilanci, decreti, nomine e votazioni parlamentari. È allora che le differenze su politica estera, difesa, energia, infrastrutture, giustizia, immigrazione e distribuzione delle risorse tornano a produrre conseguenze concrete.",
        "Il confronto sugli aiuti all'Ucraina offre un esempio di come una differenza possa diventare anche propaganda elettorale. Nel 2026 l'ultima consegna italiana descritta pubblicamente nel dettaglio riguardava caldaie, generatori e materiale per l'emergenza energetica. Il 26 agosto il ministro della Difesa Guido Crosetto dichiarava che nessuna nuova forma di aiuto era stata formalizzata in quell'anno. Questo non esclude eventuali consegne legate ai decreti classificati del 2025, ma impedisce di trattare ogni riferimento a un pacchetto come prova automatica di un nuovo invio di armi.",
        "La guerra potrebbe perdere centralità prima delle elezioni e ridurre una delle distanze più visibili tra PD e M5S. Resterebbero tutte le altre e, soprattutto, resterebbe la domanda che le contiene: chi decide quando i partiti della coalizione non sono d'accordo? Le primarie scelgono il candidato, non gli consegnano il controllo dei gruppi parlamentari degli alleati. Il programma descrive un'intenzione, non costruisce da solo una disciplina politica.",
        "Il campo largo può trovare un interesse comune nel battere il centrodestra. Questo interesse può bastare per presentare liste e condurre una campagna elettorale. Non basta necessariamente per governare cinque anni. Ogni partito conserva il proprio gruppo dirigente, i propri elettori e la possibilità di far mancare voti decisivi. Più la coalizione si allarga per vincere, più aumenta il numero dei soggetti capaci di bloccare, rallentare o riscrivere una decisione.",
        "La stabilità appare perciò pressoché impossibile non perché manchino dichiarazioni di unità, ma perché il metodo scelto non affronta la distribuzione del potere. Produce un capo comune senza costruire un'autorità comune. Il vincitore avrà il titolo per guidare, ma dipenderà da leader che non gli sono subordinati e che rispondono a elettorati diversi. Lo sconfitto, qualunque sia il suo nome, resterà abbastanza forte da rendere incompleta la vittoria dell'altro.",
        "È questo il cul de sac nel quale la coalizione rischia di essersi chiusa. Schlein ha alzato l'asticella fino a legare la propria leadership all'esito della consultazione; Conte ha accettato perché la stessa gara gli offre un premio molto più grande del rischio che corre. Entrambi parlano come se il problema fosse vincere le primarie. Il problema vero comincia quando uno dei due le perde.",
        "Nel campo largo sono tutti pronti a vincere. Il problema è che nessuno può permettersi di perdere.",
    ]),
]

sources = [
    "Partito Democratico, “Schlein: siamo all'ultimo miglio, andiamo a battere le destre e a cambiare il Paese”, 18 ottobre 2026.",
    "Partito Democratico, “Bonafoni: Schlein candidata presidente del Consiglio per la svolta necessaria”, 18 ottobre 2026.",
    "Sky TG24 e ANSA, “Assemblea PD, Schlein pronta a essere candidata premier con o senza le primarie”, 18 ottobre 2026.",
    "ANSA, “Schlein ai 5 Stelle: abbiamo il doppio dei vostri voti. Conte la sfida alle primarie”, 2 ottobre 2026.",
    "Giuseppe Conte, post pubblico sulla partecipazione del Movimento 5 Stelle alle primarie e sulla scelta affidata agli elettori, Facebook, 20 ottobre 2026.",
    "Open, “Giuseppe Conte e le primarie: il Paese è in ginocchio, subito i gazebo”, 20 ottobre 2026.",
    "Partito Democratico, Statuto nazionale approvato nel 2024, disposizioni sulle primarie di coalizione.",
    "Ministero degli Affari esteri e della cooperazione internazionale, “L'Italia partecipa alla riunione ministeriale G7+ sull'emergenza energetica ucraina”, 23 gennaio 2026.",
    "Ministero della Difesa, “Comunicato stampa del ministro Crosetto” sugli aiuti all'Ucraina e sul tredicesimo pacchetto, 26 agosto 2026.",
]

body = []
for anchor, heading, paragraphs in sections:
    body.append(f'<h2 id="{anchor}">{esc(heading)}</h2>')
    for paragraph in paragraphs:
        if isinstance(paragraph, dict):
            body.append(f'<p class="article-pullquote"><em>{esc(paragraph["quote"])}</em></p>')
        else:
            body.append(f'<p>{esc(paragraph)}</p>')
    if anchor == "ferrari-cinquecento":
        body.append(f'<figure class="article-inline-image"><img src="{D["secondaryImage"]}" width="1536" height="1024" alt="{esc(D["secondaryImageAlt"])}" loading="lazy"><figcaption>Immagine prodotta da Uno Sguardo sull&#x27;Uomo</figcaption></figure>')

tags = ["Elly Schlein", "Giuseppe Conte", "Campo largo", "Primarie", "Partito Democratico", "Movimento 5 Stelle", "Governabilità"]
word_count = len(re.findall(r"\b[\wÀ-ÖØ-öø-ÿ’'-]+\b", " ".join(opening) + " " + " ".join(str(x) for _, _, ps in sections for x in ps)))
schema = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": D["title"], "datePublished": D["datePublished"], "dateModified": D["dateModified"], "articleSection": D["category"], "wordCount": word_count}
toc = "".join(f'<li><a href="#{anchor}">{esc(heading)}</a></li>' for anchor, heading, _ in sections) + '<li><a href="#fonti">Fonti</a></li>'
opening_html = f'<p class="article-lead">{esc(opening[0])}</p><details class="dossier-contents"><summary>In questo dossier</summary><ol>{toc}</ol></details>' + "".join(f'<p>{esc(p)}</p>' for p in opening[1:])

page = f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="description" content="{esc(D['description'])}">
<meta property="og:site_name" content="UNO SGUARDO SULL'UOMO"><meta property="og:title" content="{esc(D['title'])}"><meta property="og:description" content="{esc(D['description'])}"><meta property="og:type" content="article"><meta property="og:url" content="{URL}"><meta property="og:image" content="{SITE + D['image']}"><meta property="og:image:alt" content="{esc(D['imageAlt'])}"><meta property="og:image:width" content="1536"><meta property="og:image:height" content="1024">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(D['title'])}"><meta name="twitter:description" content="{esc(D['description'])}"><meta name="twitter:image" content="{SITE + D['image']}"><link rel="canonical" href="{URL}"><title>{esc(D['title'])}</title>
<link rel="stylesheet" href="styles.css?v=20261014-inline-image-1"><link rel="stylesheet" href="editorial-rules.css?v=20260812-1"><link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<meta property="article:published_time" content="{D['datePublished']}"><meta property="article:modified_time" content="{D['dateModified']}"><meta property="article:section" content="{D['category']}"><meta name="author" content="Redazione Uno Sguardo sull’Uomo">{''.join(f'<meta property="article:tag" content="{esc(tag)}">' for tag in tags)}<link rel="alternate" type="application/rss+xml" title="Uno Sguardo sull’Uomo" href="{SITE}feed.xml"><script type="application/ld+json" data-seo-schema>{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script></head>
<body><main class="newspaper"><div class="utility-bar"><span>Quotidiano indipendente di approfondimento</span><span>Politica, società e istituzioni</span><time class="current-date" datetime="{D['datePublished']}">{D['dateLabel']}</time></div><header class="masthead"><a href="/" aria-label="Prima pagina"><img src="assets/testata.webp" width="1230" height="279" alt="Uno Sguardo sull’Uomo"></a></header><nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a><a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>
<article class="article-page" data-macro-topic="Geopolitica" data-micro-topic="Politica italiana"><nav class="topic-breadcrumb" aria-label="Percorso tematico"><span class="topic-breadcrumb-macro">Geopolitica</span><span aria-hidden="true">›</span><a href="{D['categoryPath']}">Politica italiana</a><span aria-hidden="true">›</span><span aria-current="page">{esc(D['title'])}</span></nav><header class="article-header"><a class="category-label" href="{D['categoryPath']}">Politica italiana</a><p class="eyebrow">DOSSIER</p><h1>{esc(D['title'])}</h1><p class="article-deck">{esc(D['deck'])}</p><div class="article-meta"><span>Redazione Uno Sguardo sull&#x27;Uomo</span><time datetime="{D['datePublished']}">Pubblicato: {D['dateLabel']}</time><span>Tempo di lettura: 12 minuti</span></div><div class="topic-list" aria-label="Argomenti">{''.join(f'<span>{esc(tag)}</span>' for tag in tags)}</div></header>
<figure class="article-hero"><img src="{D['image']}" width="1536" height="1024" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>Immagine prodotta da Uno Sguardo sull&#x27;Uomo</figcaption></figure><div class="article-layout"><div class="article-body">{opening_html}{''.join(body)}
<p><em>I dati relativi all'Assemblea del PD, alle dichiarazioni pubbliche dei leader e agli aiuti italiani all'Ucraina derivano dalle fonti indicate. Le conseguenze dei possibili risultati delle primarie sono scenari editoriali costruiti sull'ipotesi che venga confermato il modello tradizionale delle consultazioni aperte del centrosinistra.</em></p>
<section class="related-dossiers" aria-labelledby="related-dossiers-heading"><h2 id="related-dossiers-heading">DOSSIER CORRELATI</h2><ul><li><a href="article-elly-nome-garanzia.html">ELLY: UN NOME, UNA GARANZIA?</a><span>Politica italiana</span></li><li><a href="article-geopolitica-politica-italiana-dissenso-violenza-autoalimentata-studenti.html">Dal dissenso organizzato alla violenza autoalimentata</a><span>Politica italiana</span></li><li><a href="article-politica-italiana-societa-immigrazione-cpr-medici-ravenna.html">MEDICI SOTTO TORCHIO</a><span>Politica italiana</span></li></ul></section>
<nav class="dossier-series" aria-label="Continua nella categoria"><a class="dossier-series-archive" href="{D['categoryPath']}">Tutti i dossier di Politica italiana</a><div><a class="dossier-series-link dossier-series-older" rel="next" href="article-geopolitica-politica-italiana-dissenso-violenza-autoalimentata-studenti.html"><span>Dossier precedente</span><strong>Dal dissenso organizzato alla violenza autoalimentata</strong></a></div></nav>
<section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI</h2><ul class="sources-list">{''.join(f'<li>{esc(source)}</li>' for source in sources)}</ul></section></div></div></article><footer class="footer"><span>Uno Sguardo sull’Uomo — Politica italiana</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer></main><script src="date.js?v=20260826-audit-1"></script></body></html>'''
(ROOT / D["slug"]).write_text(page, encoding="utf-8", newline="\n")


def card(kind="archive-card", heading="h3", eager=False):
    priority = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return f'<article class="{kind}" data-dossier="{D["slug"]}"><a class="story-image" href="{D["slug"]}" aria-label="Leggi il dossier {esc(D["title"])}"><img src="{D["image"]}" width="1536" height="1024" alt="{esc(D["imageAlt"])}"{priority}></a><p class="eyebrow">{D["cardEyebrow"]}</p><p class="archive-meta"><time datetime="{D["datePublished"]}">{D["dateLabel"]}</time></p><{heading}><a class="headline-link" href="{D["slug"]}">{D["title"]}</a></{heading}><p>{esc(D["description"])}</p><a class="read-more" href="{D["slug"]}">Leggi il dossier →</a></article>'


def dated_cards(markup):
    cards = re.findall(r'<article class="archive-card".*?</article>', markup, re.S)
    return sorted(cards, key=lambda item: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', item).group(1), reverse=True)


def change_card(markup, kind, heading):
    updated = re.sub(r'class="archive-card"', f'class="{kind}"', markup, count=1)
    updated = updated.replace('<h3>', f'<{heading}>', 1).replace('</h3>', f'</{heading}>', 1)
    return updated.replace(' fetchpriority="high"', ' loading="lazy"')


def current_date(markup):
    return re.sub(r'<time class="current-date" datetime="[^"]+">.*?</time>', f'<time class="current-date" datetime="{D["datePublished"]}">{D["dateLabel"]}</time>', markup, count=1)


archive_path = ROOT / D["categoryPath"]
archive = archive_path.read_text(encoding="utf-8")
archive = re.sub(r'<article class="archive-card" data-dossier="' + re.escape(D["slug"]) + r'".*?</article>', '', archive, flags=re.S)
archive = archive.replace('<div class="archive-grid">', '<div class="archive-grid">\n' + card(), 1)
archive_path.write_text(current_date(archive), encoding="utf-8", newline="\n")

category_cards = dated_cards(archive_path.read_text(encoding="utf-8"))
indagini_path = ROOT / "indagini.html"
indagini = indagini_path.read_text(encoding="utf-8")
pattern = re.compile(r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-politica-italiana.html">Politica italiana</a></h2></div><div class="archive-grid">).*?(</div><a class="category-archive-link")', re.S)
indagini, count = pattern.subn(lambda m: m.group(1) + ''.join(category_cards[:3]) + m.group(2), indagini, count=1)
if count != 1:
    raise RuntimeError("Sezione Politica italiana non trovata in Indagini")
indagini_path.write_text(current_date(indagini), encoding="utf-8", newline="\n")

all_cards = []
for name in ("archivio-politica-italiana.html", "archivio-politica-internazionale.html", "archivio-economia.html", "archivio-societa.html"):
    all_cards.extend(dated_cards((ROOT / name).read_text(encoding="utf-8")))
all_cards.sort(key=lambda item: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', item).group(1), reverse=True)
home_path = ROOT / "index.html"
home = home_path.read_text(encoding="utf-8")
lead = change_card(all_cards[0], "lead-story", "h1").replace(' loading="lazy"', ' fetchpriority="high"', 1)
side = ''.join(change_card(item, "side-story", "h2") for item in all_cards[1:3])
latest = ''.join(change_card(item, "story-card", "h3") for item in all_cards[3:6])
other = ''.join(change_card(item, "story-card", "h3") for item in all_cards[6:9])
home = re.sub(r'<article class="lead-story".*?</article>', lead, home, count=1, flags=re.S)
home = re.sub(r'(<aside>).*?(</aside>)', lambda m: m.group(1) + side + m.group(2), home, count=1, flags=re.S)
home = re.sub(r'(<section class="story-grid" aria-label="Ultime indagini">).*?(</section>)', lambda m: m.group(1) + latest + m.group(2), home, count=1, flags=re.S)
home = re.sub(r'(<section class="story-grid" aria-label="Altre indagini recenti">).*?(</section>)', lambda m: m.group(1) + other + m.group(2), home, count=1, flags=re.S)
home_path.write_text(current_date(home), encoding="utf-8", newline="\n")

pub_date = email.utils.format_datetime(datetime.fromisoformat(D["datePublished"]).replace(tzinfo=timezone.utc))
feed_path = ROOT / "feed.xml"
feed = feed_path.read_text(encoding="utf-8")
feed = re.sub(r'\s*<item>\s*<title>' + re.escape(esc(D["title"])) + r'</title>.*?</item>', '', feed, flags=re.S)
entry = f'    <item><title>{esc(D["title"])}</title><link>{URL}</link><guid isPermaLink="true">{URL}</guid><pubDate>{pub_date}</pubDate><category>{D["category"]}</category><description>{esc(D["description"])}</description></item>\n'
feed = feed.replace('    <atom:link href="https://unosguardosulluomo.github.io/feed.xml" rel="self" type="application/rss+xml"/>\n', '    <atom:link href="https://unosguardosulluomo.github.io/feed.xml" rel="self" type="application/rss+xml"/>\n' + entry, 1)
feed_path.write_text(feed, encoding="utf-8", newline="\n")

print(f"Creato {D['slug']} e aggiornati home, Indagini, archivio e feed")
