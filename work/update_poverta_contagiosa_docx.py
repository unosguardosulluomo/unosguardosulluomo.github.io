from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dossier-sindacato-vampiro.docx"


REPLACEMENTS = {
    "IL SINDACATO VAMPIRO": "LA POVERTÀ CONTAGIOSA",
    "La povertà che non vediamo e le famiglie che la sostengono":
        "Quando la povertà di uno finisce per impoverire anche chi gli sta più vicino",
    "Neppure il titolo autorizza equivoci: «Il sindacato vampiro» è una formula critica e satirica sul flusso di risorse e sull’efficacia della rappresentanza, non un’accusa penale. Le organizzazioni ricevono denaro attraverso un meccanismo normativo esistente; proprio quel meccanismo è l’oggetto della contestazione editoriale.":
        "Il titolo «La povertà contagiosa» descrive un meccanismo economico e familiare, non attribuisce una colpa alle persone povere. Quando il reddito non basta, il costo si sposta su figli, genitori, fratelli e nonni; il flusso delle trattenute sindacali è una delle risorse sulle quali il dossier interroga le priorità collettive.",
    "Il titolo di questa inchiesta è «IL SINDACATO VAMPIRO». Il suo soggetto, però, è l’uomo. Quello che chiede aiuto, quello che lo offre a costo di privarsi del necessario e quello che, arrivato alla vecchiaia, avrebbe diritto almeno a non dover scegliere ogni giorno che cosa sacrificare.":
        "La povertà diventa contagiosa quando il bisogno di una persona si trasferisce su chi le sta accanto. Il soggetto di questa inchiesta è l’uomo: quello che chiede aiuto, quello che lo offre a costo di privarsi del necessario e quello che, arrivato alla vecchiaia, avrebbe diritto almeno a non dover scegliere ogni giorno che cosa sacrificare.",
    "Titolo: IL SINDACATO VAMPIRO": "Titolo: LA POVERTÀ CONTAGIOSA",
    "Sottotitolo: La povertà che non vediamo e le famiglie che la sostengono":
        "Sottotitolo: Quando la povertà di uno finisce per impoverire anche chi gli sta più vicino",
    "Slug permanente proposto: article-geopolitica-societa-sindacato-vampiro.html":
        "Slug permanente proposto: article-geopolitica-societa-poverta-contagiosa.html",
    "URL canonico proposto: https://unosguardosulluomo.github.io/article-geopolitica-societa-sindacato-vampiro.html":
        "URL canonico proposto: https://unosguardosulluomo.github.io/article-geopolitica-societa-poverta-contagiosa.html",
    "Descrizione breve: Dalla povertà di 5,7 milioni di italiani alle reti di aiuto e al sostegno dei familiari: l’inchiesta sui 515 milioni di trattenute sindacali e l’ipotesi di una quattordicesima sociale.":
        "Descrizione breve: La povertà degli anziani si estende alle famiglie: pensioni insufficienti, aiuti informali e 515 milioni di trattenute sindacali nel 2025.",
}


def replace_text(paragraph, old, new):
    if paragraph.text != old:
        return False
    if len(paragraph.runs) == 1:
        paragraph.runs[0].text = new
    else:
        paragraph.text = new
    return True


document = Document(PATH)
for old, new in REPLACEMENTS.items():
    matches = [paragraph for paragraph in document.paragraphs if replace_text(paragraph, old, new)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one match, found {len(matches)} for {old[:80]!r}")

document.save(PATH)
print(f"updated {PATH}")
print(f"replacements: {len(REPLACEMENTS)}")
