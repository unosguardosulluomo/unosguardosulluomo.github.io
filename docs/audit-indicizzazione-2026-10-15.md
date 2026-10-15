# Audit indicizzazione — 15 ottobre 2026

## Perimetro e fonte

Il controllo riproduce lo stato mostrato da Google Search Console il 15 ottobre 2026, con report aggiornato al 12 ottobre 2026:

- 10 URL classificate come «Pagina scansionata, ma attualmente non indicizzata»;
- 12 URL indicizzate;
- tra le 12 URL indicizzate ci sono soltanto 3 dossier: le altre 9 sono la home, quattro archivi e quattro pagine istituzionali.

Lo script ripetibile `scripts/audit_search_console_indexing.py` confronta il report con l’HTML corrente. Non interroga automaticamente Search Console: gli elenchi rappresentano uno snapshot datato e vanno aggiornati quando cambia il report.

## Risultato sui dossier

| gruppo | dossier | parole mediane | fonti mediane | link interni mediani |
|---|---:|---:|---:|---:|
| Scansionati ma non indicizzati | 10 | 3.850 | 14 | 14 |
| Indicizzati mostrati dal report | 3 | 1.991 | 0 | 6 |

Tutti i 10 dossier esclusi:

- restituiscono un canonical autonomo e coerente;
- sono presenti nel rispettivo archivio;
- hanno metadati e dati strutturati statici;
- sono inclusi nella sitemap;
- hanno un numero di collegamenti interni almeno comparabile, e mediamente superiore, a quello dei tre dossier già indicizzati.

Il confronto non sostiene l’ipotesi che le 10 esclusioni dipendano da testi troppo brevi, assenza di fonti o isolamento nella struttura del sito. Aggiungere parole o collegamenti indiscriminatamente non è quindi una correzione fondata sui dati.

## Intervento tecnico conseguente

La scoperta resta affidata a una sola sitemap canonica:

- `robots.txt` dichiara esclusivamente `https://unosguardosulluomo.github.io/sitemap.xml`;
- `sitemap.xml` è un `urlset` semplice con tutte e sole le URL canoniche pubbliche;
- i vecchi nomi `sitemap-index.xml` e `sitemap-google.xml` restano copie compatibili dello stesso `urlset`, così le precedenti segnalazioni non producono errori 404;
- le sitemap specialistiche continuano a essere generate per compatibilità, ma non sono dichiarate in `robots.txt`.

## Interpretazione corretta

«Scansionata, ma attualmente non indicizzata» significa che Google ha potuto leggere la pagina ma, al momento del report, ha scelto di non inserirla nell’indice. La correzione elimina ambiguità nel percorso di scoperta, ma non può garantire l’inclusione: la decisione finale rimane di Google.

Non sono stati modificati testi, titoli, fonti o contenuti editoriali dei dossier sulla base di questa sola segnalazione.
