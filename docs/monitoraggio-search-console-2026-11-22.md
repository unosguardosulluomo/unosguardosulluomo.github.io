# Monitoraggio Search Console — 22 novembre 2026

## Perimetro e fonti

Il controllo riguarda la proprietà `https://unosguardosulluomo.github.io/`.

- rendimento Web degli ultimi tre mesi: dal 21 agosto al 20 novembre 2026;
- report di indicizzazione aggiornato da Google al 16 novembre 2026;
- esportazioni originali conservate in `docs/search-console/2026-11-22/`;
- confronto storico: audit del 15 ottobre 2026, basato sul report aggiornato al 12 ottobre.

Search Console applica soglie di privacy alle query: le quattro query visibili sommano 14 impressioni, mentre il totale del periodo è 131. Le query esportate non rappresentano quindi tutto il traffico.

## Rendimento complessivo

| metrica | valore |
|---|---:|
| Clic | 68 |
| Impressioni | 131 |
| CTR medio | 51,9% |
| Posizione media | 6,4 |

Il dato complessivo è sostenuto soprattutto dalla home e da ricerche navigazionali o già orientate verso la testata. Non va interpretato come rendimento medio dei dossier.

## Pagine da seguire

| pagina | clic | impressioni | CTR | posizione media | priorità |
|---|---:|---:|---:|---:|---|
| `article-dublinati.html` | 0 | 12 | 0% | 9,67 | alta: prima pagina senza clic |
| `article-aler-lombardia.html` | 0 | 7 | 0% | 9,86 | alta: prima pagina senza clic |
| `contatti.html` | 1 | 18 | 5,56% | 16,67 | media: molte impressioni rispetto al sito e CTR basso |
| `indagini.html` | 0 | 5 | 0% | 8,2 | media: pagina archivio senza clic |
| `chi-siamo.html` | 12 | 48 | 25% | 7,73 | osservazione: buona risposta, non prioritaria |

Tra le query visibili, `dublinato` ha 5 impressioni, nessun clic e posizione media 8,4. È il segnale più concreto su cui verificare titolo e snippet del dossier, senza dedurre volumi dalle sole query mostrate.

## Differenza tra desktop e mobile

| dispositivo | clic | impressioni | CTR | posizione media |
|---|---:|---:|---:|---:|
| Computer | 59 | 89 | 66,29% | 2,71 |
| Mobile | 9 | 41 | 21,95% | 14,44 |
| Tablet | 0 | 1 | 0% | 9 |

Il divario mobile è il principale segnale di rendimento da monitorare. Il campione è ancora piccolo e non giustifica da solo modifiche editoriali, ma rende prioritaria la verifica di snippet, leggibilità e resa mobile delle pagine con impressioni.

## Indicizzazione

| stato | 12 ottobre | 16 novembre | variazione |
|---|---:|---:|---:|
| Indicizzate | 12 | 12 | 0 |
| Scansionate ma non indicizzate | 10 | 11 | +1 |

La nuova esclusione rispetto all’audit precedente è:

- `article-geopolitica-politica-internazionale-artico-nuova-via-seta.html`, ultima scansione 14 ottobre 2026.

Le altre dieci esclusioni restano quelle già documentate. La convalida avviata il 12 ottobre risulta non riuscita il 13 ottobre. Gli esempi esportati non mostrano scansioni successive al 14 ottobre, quindi il report non misura ancora le pubblicazioni e gli interventi più recenti del sito.

## Sitemap in Search Console

Il 22 novembre Search Console mostra cinque invii storici, tutti con stato `Impossibile recuperare` e zero pagine rilevate:

- `/sitemap.xml`, inviata il 12 ottobre 2026;
- `/sitemap-articles.xml`, inviata il 12 ottobre 2026;
- `/sitemap-index.xml`, inviata il 9 ottobre 2026;
- `/sitemap-google.xml`, inviata il 24 settembre 2026;
- `/archivio-politica-internazionale.html`, inviata il 3 settembre 2026.

Il file pubblico `sitemap.xml` risponde correttamente e contiene le URL canoniche. Il problema osservato riguarda quindi lo stato dell’invio in Search Console, non l’assenza del file nel sito.

## Priorità operative

1. Reinviare in Search Console soltanto `sitemap.xml` e verificare che passi a `Operazione riuscita` con pagine rilevate.
2. Non reinviare le sitemap storiche: `robots.txt` dichiara correttamente una sola sitemap canonica.
3. Controllare nelle prossime settimane `article-dublinati.html` e `article-aler-lombardia.html`, entrambe in posizione media 5–20 con impressioni ma senza clic.
4. Verificare la resa mobile delle pagine con impressioni prima di intervenire su titoli o contenuti.
5. Non allungare o riscrivere gli undici dossier esclusi sulla sola base dello stato di indicizzazione: i controlli tecnici locali restano positivi.
6. Ripetere l’esportazione mensile mantenendo separati rendimento, indicizzazione e stato della sitemap.
