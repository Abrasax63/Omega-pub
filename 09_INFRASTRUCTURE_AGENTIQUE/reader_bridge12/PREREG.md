# OMEGA-READER-BRIDGE-12 — protocole figé AVANT code
Date : 17 novembre 2026. Base PR #166 SHA `5402e2cfe0308637db796d9ae841b4707d67c463`; branche expérimentale, main intacte.

## Diagnostic à résoudre
Le précédent parseur arithmétique a produit 0/16 sur V7 + Spectre : les textes sont essentiellement français + LaTeX et pas du backtick ASCII. Les calculs exacts de V11 valident deux propositions **transcrites manuellement**, sans démontrer une lecture autonome.

## Architecture proposée
- `read.py` inventorie **sans interprétation** les sections H2/H3, paragraphes et blocs LaTeX `\[...\]` d'un Markdown générique, avec citations exactes, lignes et Git blob. La lecture doit fonctionner sur des fiches inconnues indépendamment de leur identifiant ou thème. Chaque paquet reste `UNREVIEWED_SOURCE_PACKET`.
- `gate.py` reçoit un objet JSON de propositions (`packet_id`, citations `premise`/`conclusion`/`limit`), proposé par n'importe quel fournisseur, **sans faire confiance au fournisseur**. Il valide indépendamment les citations contre les octets de la source, rejette les conclusions tirées des sections `Preuve`, `Réfuté`, `Non-théorème`, `Limites` et bloque les sorties contenant des faits/relations non présents dans le document.
- `model.py` ajoute un transport facultatif vers un modèle local Ollama sur `127.0.0.1:11434` uniquement (aucune clé, API payante, téléchargement ni exécution dans la CI). Le modèle ne produit que des propositions JSON; son retour doit toujours passer par le gate, et ne crée aucune règle certifiée.
- `pipeline.py` offre un parcours de bout en bout : Markdown → paquets sourcés → candidats JSON éventuels → contrôle externe → file **quarantaine** JSON en lecture seule. Aucune écriture dans les règles Horn #151/#152 ni RCE/PR #81. Les checks finis V11 peuvent être rejoués **uniquement de manière explicite**, sur leurs contrats humains déjà figés, sans attribuer le résultat au modèle.

## Test et holdout
Calibration antérieure connue : V7 (`6c482f97345abbb7f3d5bcd5e20da96259b276ce`) et CAP02 (`3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7`). Garder #166 original intact.
Deux documents réservés avant implémentation et consultation de leur contenu, sur révision publique `0ca3c5f63998cf16cc84478c7735c03445a08669` :
- `02_MATHEMATIQUES/observabilite_temporelle/sources/NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md`
- `02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md`.
Pas de retouche du lecteur après inspection de ces documents ; CI de calibration doit avoir réussi avant lecture du holdout. Les nouvelles fiches permettent de mesurer le repérage sourcé du LaTeX et de tester des propositions adversariales ; **pas une validation de traduction sémantique ou d'exactitude d'un LLM**, car aucune inférence n'est encore autorisée dans CI.

## Tests falsifiables et statuts
- Test positif : paquet contenant une formule LaTeX délimitée et texte voisin ; contrôle des plages exactes, hash et sections.
- Négatifs : SHA altéré, citation fabriquée, portée non vérifiée, conclusion dans `Preuve` / `Non-théorème` / `Réfuté`, tentative `CERTIFIED` ou `horn_rules`, confusion entre hypothèse et conclusion, réponse JSON du modèle invalide, paquet inventé, traversée symlink, sources surdimensionnées.
- Un faux positif de citation ou promotion invalide est un ÉCHEC. Toutes sorties admissibles restent `QUARANTINE_UNREVIEWED` et le verdict mathématique `INDETERMINATE`.
- Résultat technique utile si ≥1 paquet LaTeX sourcé sur chacun des deux nouveaux documents et 100 % des contrôles de citations valides ; sinon, résultat négatif. Des tests de transport local simulés ne sont pas des générations réelles.
- La véritable mesure de fidélité sémantique d'un modèle demande des sorties d'un petit modèle réellement exécuté ET un gold indépendant sur un corpus nouveau ; ne jamais inférer cette réussite à partir de tests de schéma.

## Sorties
Rapports CI JSON + liens de run et artefacts, une PR brouillon distincte; zéro modification `main`, zéro appel payant, aucun raccord automatique au cycle horaire.
