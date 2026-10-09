# Procedura SEO gratuita per i dossier

Questa procedura integra il lavoro editoriale: non sostituisce verifica delle fonti, qualità del testo o giudizio giornalistico.

## Prima della scrittura

1. Formulare la domanda precisa alla quale il dossier risponde.
2. Controllare gratuitamente la query su Google e osservare formato, temi e domande presenti nei risultati. Usare Google Trends solo per confrontare formulazioni; non trasformare valori relativi in volumi assoluti.
3. Consultare Search Console per verificare se il sito riceve già impressioni su query collegate.
4. Registrare nel file `editorial/*.json`:

```json
"seo": {
  "primaryQuery": "guerra ibrida Italia",
  "searchIntent": "informativo-approfondimento",
  "supportingQueries": [
    "che cos'è la guerra ibrida",
    "come si prepara l'Italia alla guerra ibrida",
    "quali infrastrutture italiane sono vulnerabili"
  ],
  "serpCheckedAt": "2026-10-09"
}
```

Gli intenti ammessi sono `informativo-attualità`, `informativo-approfondimento` e `navigazionale`.

## Durante la costruzione

- Titolo, slug e apertura devono rendere riconoscibile l'argomento principale.
- L'apertura espone subito risposta, tesi o risultato della verifica.
- Le domande secondarie diventano sezioni quando migliorano davvero la comprensione.
- Numeri, fonti, limiti e contraddittorio hanno priorità sulla ripetizione della query.
- Il generatore ricava la descrizione SEO dai contenuti visibili, aggiunge dimensioni reali alle immagini locali e crea tre collegamenti a dossier semanticamente correlati.

## Prima della pull request

```text
python scripts/build_search_visibility.py
python scripts/build_related_dossiers.py
python scripts/build_search_visibility.py
python scripts/build_related_dossiers.py
python scripts/check_search_visibility.py
python scripts/check_new_dossier_seo.py --base origin/main
```

Controllare inoltre il diff, la resa desktop e mobile e i collegamenti proposti. Un collegamento semanticamente sbagliato va corretto nei tag editoriali, non sostituito con JavaScript.

## Ogni mese

Esportare da Search Console gli ultimi 90 giorni e lavorare in quest'ordine:

1. esclusioni dall'indice che non corrispondono a redirect o `noindex` intenzionali;
2. pagine in posizione media 5-20;
3. query con impressioni e CTR basso;
4. dossier con calo persistente di impressioni;
5. aggiornamenti sostanziali di dati, risposte e titoli, senza cambiare la data di pubblicazione.

I backlink non si comprano: si ottengono pubblicando dati verificabili, segnalando il lavoro alle fonti interessate e distribuendolo sui canali reali della testata.
