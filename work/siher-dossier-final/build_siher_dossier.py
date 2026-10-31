from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\utente\OneDrive\Documenti\ChatGPT\sito uno sguardo sull'uomo")
OUT = ROOT / "DOSSIER_SIHER_LA_CAUTELA_ESCLUSA.docx"
HERO = Path(r"C:\Users\utente\.codex\generated_images\01a19274-9d04-7123-b79c-a64d137d1956\exec-196719eb-8934-414d-a662-aba98fafc846.png")
PROFILE = Path(r"C:\Users\utente\.codex\generated_images\01a19274-9d04-7123-b79c-a64d137d1956\exec-0d95c86c-c3c7-418a-970f-08c0e131b053.png")


def set_font(run, name="Aptos", size=11, bold=None, italic=None, color="000000"):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_table_borders(table, color="D9D9D9", size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), size)
        el.set(qn("w:color"), color)


def set_fixed_table_widths(table, widths):
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.first_child_found_in("w:tblLayout")
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    total_twips = int(sum(widths) * 1440)
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(total_twips))
    tbl_w.set(qn("w:type"), "dxa")
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Inches(width)
            tc_w = cell._tc.get_or_add_tcPr().first_child_found_in("w:tcW")
            tc_w.set(qn("w:w"), str(int(width * 1440)))
            tc_w.set(qn("w:type"), "dxa")


def add_field(paragraph, field_code):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field_code
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_font(run, size=9, color="555555")


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(text)
    set_font(r, name="Aptos Display", size=16 if level == 1 else 12, bold=True)
    return p


def add_body(doc, text, bold_lead=None, keep=False):
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.keep_together = keep
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_font(r2)
    else:
        r = p.add_run(text)
        set_font(r)
    return p


def add_quote(doc, text, attribution=None):
    p = doc.add_paragraph(style="Quote")
    p.paragraph_format.left_indent = Inches(0.42)
    p.paragraph_format.right_indent = Inches(0.30)
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_together = True
    r = p.add_run(f"“{text}”")
    set_font(r, name="Aptos", size=10.5, italic=True)
    if attribution:
        r2 = p.add_run(f"\n{attribution}")
        set_font(r2, name="Aptos", size=9.5, bold=True)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    set_font(r)
    return p


def add_image(doc, path, alt_text, width=7.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    shape = run.add_picture(str(path), width=Inches(width))
    doc_pr = shape._inline.docPr
    doc_pr.set("descr", alt_text)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(9)
    cap.paragraph_format.keep_with_next = True
    cr = cap.add_run("Immagine prodotta da Uno Sguardo sull’Uomo")
    set_font(cr, size=8.5, italic=True, color="555555")


doc = Document()
sec = doc.sections[0]
sec.page_width = Inches(8.5)
sec.page_height = Inches(11)
sec.top_margin = Inches(0.55)
sec.bottom_margin = Inches(0.58)
sec.left_margin = Inches(0.70)
sec.right_margin = Inches(0.70)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Aptos"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
normal.font.size = Pt(11)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.line_spacing = 1.08
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.widow_control = True

for style_name, size in (("Title", 25), ("Heading 1", 16), ("Heading 2", 12)):
    st = styles[style_name]
    st.font.name = "Aptos Display"
    st._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
    st._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
    st.font.size = Pt(size)
    st.font.bold = style_name != "Title"
    st.font.color.rgb = RGBColor(0, 0, 0)

# Remove any inherited paragraph border from Word's built-in Title style.
title_ppr = styles["Title"]._element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)

if "Deck" not in styles:
    deck_style = styles.add_style("Deck", WD_STYLE_TYPE.PARAGRAPH)
else:
    deck_style = styles["Deck"]
deck_style.font.name = "Aptos"
deck_style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
deck_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
deck_style.font.size = Pt(12.5)
deck_style.font.color.rgb = RGBColor(0, 0, 0)
deck_style.paragraph_format.space_after = Pt(8)

# Cover
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(5)
r = p.add_run("UNO SGUARDO SULL’UOMO")
set_font(r, name="Aptos", size=10.5, bold=True)

add_image(
    doc,
    HERO,
    "Composizione editoriale con la gip Tiziana Landoni, fascicoli e analisi digitale, e Youssef Siher presso un’uscita",
    width=7.05,
)

title = doc.add_paragraph(style="Title")
title.paragraph_format.space_before = Pt(2)
title.paragraph_format.space_after = Pt(4)
tr = title.add_run("Caso Siher la cautela esclusa")
set_font(tr, name="Aptos Display", size=25, bold=True)

deck = doc.add_paragraph(style="Deck")
dr = deck.add_run(
    "Perché liberare senza alcuna misura Youssef Siher prima di completare gli accertamenti digitali è stata una scelta di rischio e non un esito inevitabile"
)
set_font(dr, size=12.5)

meta = doc.add_paragraph()
meta.paragraph_format.space_before = Pt(2)
meta.paragraph_format.space_after = Pt(0)
mr = meta.add_run("DOSSIER  |  Chiusura redazionale 31 ottobre 2026  |  Tempo di lettura 20 minuti")
set_font(mr, size=8.5, bold=True, color="444444")

meta2 = doc.add_paragraph()
meta2.paragraph_format.space_after = Pt(0)
mr2 = meta2.add_run("Macroargomento Geopolitica  |  Microargomento Politica italiana")
set_font(mr2, size=8.5, color="444444")

doc.add_page_break()

# Footer from page 2 onward (same section, cover intentionally shares footer but first-page different).
sec.different_first_page_header_footer = True
footer = sec.footer
fp = footer.paragraphs[0]
fp.text = ""
ft = footer.add_table(rows=1, cols=2, width=Inches(7.1))
ft.autofit = False
set_repeat_table_header(ft.rows[0])
ft.columns[0].width = Inches(6.1)
ft.columns[1].width = Inches(1.0)
left = ft.rows[0].cells[0]
right = ft.rows[0].cells[1]
left.width = Inches(6.1)
right.width = Inches(1.0)
set_cell_margins(left, top=0, start=0, bottom=0, end=0)
set_cell_margins(right, top=0, start=0, bottom=0, end=0)
lp = left.paragraphs[0]
lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
lr_footer = lp.add_run("UNO SGUARDO SULL’UOMO  •  Caso Siher la cautela esclusa")
set_font(lr_footer, size=8.2, color="555555")
rp = right.paragraphs[0]
rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
add_field(rp, "PAGE")
tbl_pr = ft._tbl.tblPr
tbl_borders = OxmlElement("w:tblBorders")
for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "nil")
    tbl_borders.append(el)
tbl_pr.append(tbl_borders)

# Opening
lead = doc.add_paragraph()
lead.paragraph_format.space_after = Pt(10)
lead.paragraph_format.keep_together = True
lr = lead.add_run(
    "Il 28 ottobre 2026 la giudice per le indagini preliminari Tiziana Landoni non ha soltanto respinto il carcere per Youssef Siher. Ha scelto di non applicare alcuna cautela, mentre gli investigatori stavano ancora entrando nel materiale digitale e mancavano due giorni a una nuova mobilitazione nazionale. Quel vuoto di protezione è il fatto politico e giudiziario che merita di essere esaminato."
)
set_font(lr, name="Aptos", size=13, bold=True)

add_body(doc, "Il fermo non è una condanna. La libertà personale non può essere compressa per offrire alla Procura qualche giorno di lavoro in più. Ma da questi principi non discende che l’unica alternativa alla custodia in carcere fosse restituire a Siher piena libertà senza condizioni. Il Codice di procedura penale prevede misure graduate e revocabili. Landoni le ha escluse tutte perché ha letto i messaggi attribuiti all’indagato come espressione politica priva di un richiamo diretto alla violenza e ha giudicato insussistenti le esigenze cautelari.")
add_body(doc, "La nostra tesi è diversa. Il rischio non si misurava soltanto cercando una frase firmata da Siher con un ordine esplicito di colpire qualcuno. Si misurava anche nel ruolo di chi amministrava una rete capace di raggiungere decine di migliaia di persone, nel momento scelto per attivarla, nella gestione dei messaggi altrui e nella vicinanza di un’altra giornata di piazza. Ridurre questa capacità organizzativa alla sola lettera dei post ha prodotto una decisione formalmente motivata, ma priva della cautela che il contesto richiedeva.")

add_heading(doc, "Il tempo che la decisione ha tolto agli accertamenti", 1)
add_body(doc, "Siher è stato fermato nella notte tra il 24 e il 25 ottobre. Il 28 ottobre è tornato libero. Telefono e computer sequestrati contenevano un insieme di contatti, conversazioni, accessi e attività che non poteva essere ricostruito in poche ore. Il 31 ottobre la Procura risultava ancora in attesa di ciò che gli accertamenti digitali avrebbero potuto aggiungere. Il materiale non era un dettaglio successivo: era il luogo in cui verificare la reale estensione del ruolo organizzativo contestato.")
add_body(doc, "La giudice non poteva prorogare il fermo per attendere gli esiti tecnici. Poteva però riconoscere, se li avesse ritenuti presenti, i gravi indizi e le esigenze cautelari previsti dagli articoli 273 e 274 del Codice di procedura penale, applicare una misura coercitiva ai sensi dell’articolo 391 e revocarla o sostituirla quando il quadro fosse cambiato, come prevede l’articolo 299. La legge non offriva tempo in astratto. Offriva strumenti temporanei per governare un rischio concreto.")
add_body(doc, "Il risultato della valutazione di Landoni è stato netto: nessun vincolo. Il 30 ottobre era già fissato lo sciopero generale con cortei studenteschi e mobilitazioni nazionali. A Milano, dopo le violenze del 17 e 18 ottobre, le autorità attendevano migliaia di manifestanti. La nuova giornata si è poi svolta con messaggi di solidarietà a Siher. Questo non dimostra che lui avrebbe commesso altri reati. Dimostra che il momento della decisione non era neutro e che l’eventuale capacità di mobilitazione avrebbe avuto un banco di prova immediato.")

perspective_heading = add_heading(doc, "L’errore di prospettiva", 1)
perspective_heading.paragraph_format.page_break_before = True
add_quote(doc, "Nei post e nel comunicato [...] l’indagato non prospetta mai il ricorso ad azioni violente", "Passaggio dell’ordinanza riportato da Sky TG24 e RaiNews")
add_body(doc, "È il punto centrale del ragionamento della giudice: nei contenuti direttamente attribuiti a Siher non compare l’incitamento esplicito alla violenza e le devastazioni del 17 e 18 ottobre non vengono indicate come modello da ripetere. È un elemento favorevole all’indagato, ma non esaurisce il problema cautelare.")
add_body(doc, "Chi governa uno spazio digitale può esercitare influenza senza scrivere l’ultima frase della catena. Decide quando aprire un canale, quali appuntamenti rilanciare, quali contenuti mettere in evidenza, chi può pubblicare e quali messaggi lasciare visibili. Questa non è una presunzione di colpevolezza. È la ragione per cui il ruolo di amministratore deve essere ricostruito prima di concludere che l’assenza di un ordine personale equivalga all’assenza di rischio.")
add_body(doc, "Il silenzio davanti a un messaggio violento non prova automaticamente adesione. Può essere disattenzione, impossibilità materiale di intervenire oppure una scelta. Per distinguerle servono orari, permessi, cancellazioni, reazioni, log e conversazioni. Erano proprio gli elementi ancora in corso di esame quando ogni cautela è stata esclusa. La decisione ha trattato come rassicurante ciò che, in quel momento, era ancora incompleto.")

add_heading(doc, "Siher non era un ragazzo trascinato dalla piazza", 1)
add_body(doc, "Youssef Siher aveva trent’anni. Era presentato come ricercatore di geopolitica, studioso dei movimenti politici islamici e giornalista freelance. Il canale Telegram del Movimento 17 ottobre contava circa 11.000 iscritti e la pagina Instagram circa 39.000. I canali sarebbero stati creati la sera del 18 ottobre, dopo le devastazioni milanesi. Questa cronologia non gli attribuisce automaticamente l’organizzazione degli scontri precedenti. Mostra però la rapidità con cui seppe dare una struttura e un pubblico a una mobilitazione già accesa.")
add_body(doc, "Il dato anagrafico conta perché impedisce di leggere la vicenda con l’indulgenza riservata a una bravata adolescenziale. Siher era un adulto sposato, con competenze culturali e digitali, capace di costruire un apparato comunicativo in pochi giorni. Il matrimonio non è una patente di rispettabilità né una prova di pericolosità. È un segno di vita adulta e di responsabilità assunte. In questo caso, inoltre, la famiglia non restava fuori dall’attività politica.")
add_body(doc, "La moglie, sposata nel settembre 2026, risultava indagata nello stesso procedimento. Secondo l’Agenzia Nazionale Stampa Associata (ANSA), i coniugi erano i due amministratori e, nelle aree riservate alla pubblicazione, gli unici autorizzati a scrivere. Il matrimonio quindi non descrive soltanto una sfera privata da preservare: coincideva anche con una collaborazione nella macchina comunicativa sotto esame. Non sappiamo se quella unione abbia rafforzato l’attivismo. Sappiamo che l’attivismo era condiviso e organizzato dentro la coppia.")

add_image(doc, PROFILE, "Composizione editoriale di Youssef Siher a una scrivania con dispositivi digitali e una rete di comunicazione", width=7.0)

add_heading(doc, "Il potere di un amministratore digitale", 1)
add_body(doc, "Nel mondo fisico riconosciamo subito la differenza tra chi assiste a una manifestazione e chi prepara il percorso, convoca le persone, distribuisce indicazioni e sceglie gli interlocutori. Online quella differenza è meno visibile, ma non scompare. Un amministratore non è responsabile per definizione di ogni frase scritta da un utente. Possiede però strumenti che un utente comune non ha e può determinare la durata e la diffusione di un contenuto.")
add_body(doc, "Per questo la domanda corretta non era soltanto se Siher avesse scritto parole violente. Bisognava accertare quale controllo esercitasse sugli ambienti collegati, come fossero coordinati Telegram e Instagram, chi autorizzasse i contenuti, quali relazioni esistessero con gli organizzatori delle piazze e se i messaggi più estremi fossero tollerati, contrastati o utilizzati per tenere alta la pressione. Il sequestro dei dispositivi serviva precisamente a dare un contenuto probatorio a queste domande.")
add_body(doc, "Landoni ha preferito giudicare subito il nucleo già visibile. È una scelta legittima sul piano delle funzioni, ma discutibile sul piano della prudenza: ha isolato la voce individuale dal sistema che quella voce aveva contribuito a costruire.")

add_heading(doc, "Le frasi contro Giovanni Donzelli", 1)
add_body(doc, "Dopo la scarcerazione sono stati pubblicati screenshot attribuiti agli spazi Telegram collegati al Movimento 17 ottobre. Non disponiamo dell’esportazione integrale della conversazione e non attribuiamo le frasi a Siher. I messaggi, tuttavia, non lasciano dubbi sul bersaglio evocato.")
add_quote(doc, "Andate sotto il Parlamento a migliaia… E magari spaccare il muso anche a Donzelli")
add_quote(doc, "Se qualcuno gli lancia qualcosa stile statuetta del Duomo a Berlusconi…")
add_body(doc, "L’immagine della statuetta richiama l’aggressione subita da Silvio Berlusconi nel 2009. Non è dissenso aspro, ma l’evocazione di un atto fisico. Giovanni Donzelli, responsabile dell’organizzazione di Fratelli d’Italia (FdI), riceve minacce da anni. Nel febbraio 2023 il Ministero dell’interno dispose per lui una scorta nel clima del caso Cospito. Nel giugno 2026 a Firenze comparve anche la scritta «Donzelli a testa in giù». Chi scriveva nei canali non stava scegliendo un nome privo di esposizione: indicava una persona il cui rischio era già riconosciuto dallo Stato.")
add_body(doc, "Secondo la ricostruzione pubblicata il 30 ottobre, questi messaggi non erano confluiti nella richiesta iniziale di fermo né nel provvedimento di liberazione. Non possono quindi essere usati retroattivamente come se Landoni li avesse letti e ignorati. Possono però mostrare quanto fosse fragile una valutazione costruita prima di completare l’esame dell’ecosistema digitale. Quando nuovi contenuti emergono subito dopo la liberazione, il dubbio non riguarda soltanto il loro autore. Riguarda la decisione di escludere ogni cautela prima di sapere che cosa contenesse realmente quella rete.")

add_heading(doc, "Il rischio riconosciuto a velocità diverse", 1)
add_body(doc, "Le minacce contro Landoni sono gravi e devono produrre protezione. Il presidente del Tribunale di Milano Fabio Roia ha chiesto a prefetto e questore di valutare misure a tutela della giudice. Numerosi consiglieri del Consiglio superiore della magistratura (CSM) hanno inoltre chiesto una pratica a tutela dopo le parole con cui la presidente del Consiglio Giorgia Meloni aveva definito «vergognosa» la decisione. Criticare un provvedimento non autorizza nessuno a minacciare chi lo ha firmato.")
add_body(doc, "Proprio questa reazione rende visibile un contrasto. Davanti ai messaggi contro la giudice, l’apparato istituzionale ha riconosciuto immediatamente il possibile pericolo: monitoraggio, segnalazioni formali, valutazione della protezione, iniziativa al CSM. Davanti ai messaggi contro Donzelli, già sotto scorta, il materiale è emerso quando Siher era libero e non risultava aver inciso sul primo esame cautelare.")
add_body(doc, "Le due situazioni non sono identiche e non chiediamo di sottrarre tutela a Landoni. Chiediamo coerenza nel metodo. Se una minaccia online acquista peso perché il bersaglio è una magistrata esposta, la stessa attenzione deve valere quando il bersaglio è un politico già protetto e quelle parole circolano in un ambiente amministrato da persone sotto indagine. Non basta liquidare il secondo caso come rumore di fondo e il primo come allarme istituzionale.")

add_heading(doc, "La Procura resa più debole dal primo rigetto", 1)
add_body(doc, "La scarcerazione non dimostra che la Procura abbia inventato il caso, né che debba trasformare l’impugnazione in uno scontro con la giudice. Il 31 ottobre l’orientamento sul ricorso veniva descritto come «più no che sì» se gli elementi fossero rimasti gli stessi. La ragione è comprensibile: riproporre un quadro già giudicato insufficiente espone l’accusa a una seconda bocciatura. Telefono e computer possono invece fornire elementi nuovi e rendere più solida una successiva iniziativa.")
add_body(doc, "Qui si vede l’effetto concreto dell’ordinanza. Landoni non ha fermato l’indagine, ma ne ha cambiato il terreno. La Procura ora deve scegliere se contestare subito la lettura giuridica o attendere prove capaci di superarla. Nel frattempo Siher resta libero e il controllo sugli eventuali rischi dipende soltanto dalle normali attività investigative. Non è la Procura ad aver scelto questo intervallo senza misura. È la conseguenza della valutazione compiuta dalla GIP.")

add_heading(doc, "La cautela non sarebbe stata una condanna", 1)
add_body(doc, "La libertà personale è la regola e la misura cautelare l’eccezione. Ma eccezione non significa impossibilità. Significa motivazione, proporzionalità, controllo e revoca quando i presupposti cessano. Il sistema conosce diverse misure e non obbliga il giudice a scegliere tra carcere e libertà senza condizioni. Le informazioni pubbliche non permettono di stabilire quale misura alternativa fosse concretamente adeguata al fascicolo. Permettono di constatare che nessuna fu ritenuta necessaria.")
add_body(doc, "Una cautela limitata avrebbe potuto accompagnare i pochi giorni necessari a chiarire il materiale digitale e sarebbe stata rimossa se gli accertamenti avessero escluso il rischio. Non avrebbe dichiarato Siher colpevole. Avrebbe riconosciuto che un adulto dotato di capacità organizzative, amministratore con la moglie di canali molto seguiti, non poteva essere valutato come un semplice autore di post isolati mentre un’altra manifestazione nazionale era imminente.")
add_body(doc, "La nostra conclusione non riguarda la colpevolezza penale, che deve essere provata nelle forme previste dalla legge. Riguarda il giudizio sul rischio. Landoni ha attribuito valore decisivo all’assenza di un invito personale alla violenza e ha lasciato sullo sfondo la forza dell’organizzazione, i poteri di amministrazione e ciò che i dispositivi non avevano ancora rivelato. In questo scarto si trova la cautela esclusa.")

add_heading(doc, "I fatti e le deduzioni", 1)
summary_rows = [
    ("Fatto documentato", "Il 28 ottobre Landoni non ha convalidato il fermo e non ha applicato misure personali."),
    ("Fatto documentato", "Gli accertamenti sui dispositivi erano ancora rilevanti per le successive scelte della Procura."),
    ("Fatto documentato", "Siher e la moglie risultavano amministratori dei canali, con un pubblico di decine di migliaia di utenti."),
    ("Fatto documentato", "La liberazione è avvenuta due giorni prima della mobilitazione nazionale del 30 ottobre."),
    ("Deduzione editoriale", "Il ruolo organizzativo non poteva essere valutato soltanto attraverso le frasi personalmente firmate da Siher."),
    ("Scenario possibile", "Una misura proporzionata e revocabile avrebbe potuto coprire la fase di verifica senza anticipare una condanna."),
]
table = doc.add_table(rows=1, cols=2)
table.autofit = False
table.columns[0].width = Inches(1.45)
table.columns[1].width = Inches(5.25)
hdr = table.rows[0].cells
hdr[0].text = "Natura"
hdr[1].text = "Punto di osservazione"
for c in hdr:
    shade_cell(c, "243746")
    set_cell_margins(c)
    for p in c.paragraphs:
        for run in p.runs:
            set_font(run, size=9.5, bold=True, color="FFFFFF")
set_repeat_table_header(table.rows[0])
for idx, (kind, point) in enumerate(summary_rows):
    cells = table.add_row().cells
    cells[0].text = kind
    cells[1].text = point
    if idx % 2:
        shade_cell(cells[0], "F3F6F8")
        shade_cell(cells[1], "F3F6F8")
    for c in cells:
        set_cell_margins(c)
        for p in c.paragraphs:
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                set_font(run, size=9.2, bold=(c is cells[0]))
set_table_borders(table)
set_fixed_table_widths(table, (1.45, 5.25))

add_heading(doc, "Dichiarazioni politiche", 1)
add_body(doc, "Le dichiarazioni riportate di seguito documentano la reazione di Fratelli d’Italia alle frasi contro Donzelli. Sono posizioni politiche, non accertamenti giudiziari.")
add_quote(doc, "Rivolgo la piena solidarietà mia e dei deputati di Fratelli d’Italia a Giovanni Donzelli per le minacce emerse nelle chat di Siher. Colpisce, tuttavia, l’assordante silenzio della sinistra davanti a messaggi che inneggiano alla violenza e indicano esponenti di Fratelli d’Italia come bersagli. Ci chiediamo dove sono finiti gli appelli alla difesa della democrazia e alla condanna dell’odio politico. Ci chiediamo se i partiti d’opposizione scelgano di adottare consapevolmente questa precisa linea. Evitare attentamente di pestare i piedi ai movimenti che in questi giorni stanno mettendo a dura prova le Forze dell’ordine. Su minacce e intimidazioni non può esserci alcun conflitto d’interesse: per questo aspettiamo una presa di posizione chiara e senza ambiguità da parte di tutte le forze politiche.", "Galeazzo Bignami")
add_quote(doc, "A quanto pare, tra le importanti rivendicazioni del Movimento 17 ottobre, oltre al diritto allo studio, al futuro dei giovani e alle tante questioni che animano le proteste studentesche, c’è anche il desiderio di spaccare la testa a Giovanni Donzelli. Almeno a giudicare da quello che si legge nelle chat degli organizzatori. Ci chiediamo se queste siano le nuove forme di partecipazione democratica che qualcuno continua a difendere e giustificare.", "Francesco Torselli")
add_quote(doc, "A Giovanni va la mia vicinanza. Manifestare, contestare e dissentire sono diritti sacrosanti, ma augurarsi aggressioni fisiche e trasformare chi la pensa diversamente in un bersaglio non ha nulla a che vedere con il diritto di protesta. È violenza, anche quando viene scritta comodamente dietro una tastiera. E allora vorremmo sapere se la sinistra abbia intenzione di prendere le distanze anche da queste minacce. Perché non si può condannare la violenza soltanto quando fa comodo.", "Francesco Torselli")
add_quote(doc, "Costoro, che si sentono evidentemente impuniti perché nascosti in un gruppo, ignorano che Giovanni non si farà certo intimorire da vigliaccate simili. Perché è rimasta la stessa persona che ai tempi dell’università, quando militava nel Fuan, non si lasciava spaventare da situazioni pericolose, a rischio e tantomeno dai violenti ideologici. Ci aspettiamo adesso una condanna unanime.", "Parlamentari toscani di Fratelli d’Italia")

add_heading(doc, "Fonti", 1)
sources = [
    "ANSA, Amministratori chat Movimento 17 ottobre solo Siher e sua moglie, 25 ottobre 2026.",
    "ANSA, Siher torna in libertà Meloni attacca la gip, 28 ottobre 2026.",
    "ANSA, Il Csm chiede una pratica a tutela della gip del caso Siher, Luca Capponi, 29 ottobre 2026.",
    "ANSA, Caso Siher Tribunale chiede di verificare se serve tutela per gip, 30 ottobre 2026.",
    "ANSA, A Milano già centinaia in piazza cambia il percorso del corteo degli studenti, 30 ottobre 2026.",
    "Corriere della Sera Milano, Chi è Youssef Siher la mente dietro il Movimento 17 ottobre, 24 ottobre 2026.",
    "Corriere della Sera Milano, Scontri a Milano indagata anche la moglie di Youssef Siher, 25 ottobre 2026.",
    "Corriere della Sera Milano, Youssef Siher non convalida del fermo il ricorso possibile soltanto con nuovi elementi di indagine, Luigi Ferrarella, 31 ottobre 2026.",
    "Sky TG24, Proteste Milano fermato Siher, 25 ottobre 2026.",
    "Sky TG24, Youssef Siher il gip di Milano lo rimette in libertà, 28 ottobre 2026.",
    "RaiNews, Youssef Siher è in carcere indagata anche la moglie, 25 ottobre 2026.",
    "RaiNews, Cortei Youssef Siher è libero chiesta in Csm tutela della gip, 29 ottobre 2026.",
    "RaiNews, Disposta la scorta anche per Donzelli, aggiornamento del 3 febbraio 2023 sul caso Cospito.",
    "Il Giornale, Pure Donzelli nel mirino di Siher Ira FdI sulla gip, 30 ottobre 2026.",
    "Secolo d’Italia, Spaccate il muso a Donzelli il messaggio choc nelle chat di Siher, 30 ottobre 2026.",
    "Fratelli d’Italia, Siher con nuove chat si rivaluti posizione Solidarietà a Donzelli per minacce, 29 ottobre 2026.",
    "Normattiva, Codice di procedura penale, articoli 273, 274, 299, 310 e 391, testo vigente consultato il 31 ottobre 2026.",
    "Normattiva, Codice penale, articolo 414, testo vigente consultato il 31 ottobre 2026.",
]
for src in sources:
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.left_indent = Inches(0.20)
    p.paragraph_format.first_line_indent = Inches(-0.16)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.keep_together = True
    r = p.add_run(f"•  {src}")
    set_font(r, size=9.3)

doc.core_properties.title = "Caso Siher la cautela esclusa"
doc.core_properties.subject = "Dossier sulla decisione cautelare nel caso Youssef Siher"
doc.core_properties.author = "Redazione Uno Sguardo sull’Uomo"
doc.core_properties.keywords = "Youssef Siher, Tiziana Landoni, Movimento 17 ottobre, Giovanni Donzelli, misure cautelari"
doc.core_properties.comments = "Versione definitiva Word chiusa il 31 ottobre 2026"

doc.save(OUT)
print(OUT)
