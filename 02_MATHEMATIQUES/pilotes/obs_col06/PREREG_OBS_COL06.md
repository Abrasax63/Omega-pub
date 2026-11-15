# OBS-COL-06 — Pré-enregistrement de la sélection de représentations concurrentes
Date : 2026-11-15. **Engagement écrit avant tout code OBS-COL-06.**
Base empilée : PR #88 ; `main` et registres certifiés inchangés.

## Verrou scientifique
Une dynamique visible peut-elle être expliquée soit par une règle sans mémoire (incluant interactions simultanées de plusieurs bits), soit seulement par une variable d'état latente ? Peut-on trouver une contradiction **reproductible** au postulat de Markov sur les variables visibles, et reconnaître qu'un modèle de mémoire binaire ne suffit pas, sans donner la règle génératrice au planificateur ?

## Grammaire de représentations concurrentes, non hiérarchisée
Visibilité : quatre bits (0..15), actions `prime` et `read`, reset de l'état visible `x` avec mémoire cachée initialisée à 0.
Les cinq hypothèses paramétrées **déclarées aux comparateurs et à Omega**, mais non l'identité de la cible :
- `PAIR01` : prime laisse x inchangé ; read bascule b3 si b0 & b1.
- `PAIR02` : prime laisse x inchangé ; read bascule b3 si b0 & b2.
- `TRIPLE012` : prime laisse x inchangé ; read bascule b3 si b0 & b1 & b2.
- `MEMORY_TOGGLE` : prime inverse un bit de mémoire latente, read bascule b3 si mémoire=1.
- `MEMORY_SET` : prime positionne la mémoire latente à 1, read bascule b3 si mémoire=1.

Les cinq familles sont concurrentes ; aucun ordre de complexité préfixé ne doit sélectionner le résultat. Le monde `OUTSIDE_TERNARY` est intentionnellement **absent** du catalogue : prime augmente un compteur latent modulo 3, et read bascule b3 lorsque le compteur vaut 1 ou 2. Il est indiscernable de MEMORY_SET pour zéro, une et deux actions prime, mais différent après trois actions prime.

## Données et séparation fixées
- Les six mondes `PAIR01, PAIR02, TRIPLE012, MEMORY_TOGGLE, MEMORY_SET, OUTSIDE_TERNARY` sont des constructions publiques de l'expérimentateur, NON un holdout aveugle indépendant.
- Observations initiales pour chaque monde : reset x=0 et x=1, intervention `read` (aucune de ces cibles ne bascule b3). Les résultats sont fournis comme traces brutes, sans étiquettes de famille.
- Catalogue de huit consultations possibles, chacune avec reset et séquence complète : (3,R), (5,R), (7,R), (0,P-R), (0,P-P-R), (7,P-R), (3,P-R), (5,P-R). Les mesures complètes sont des histoires visibles, pas seulement des valeurs finales.
- **Réserve de généralisation : six consultations jamais proposées au planificateur**, x=0,3,7 avec P-P-P-R, et x=8,13,15 avec R.
- P1/PR #23 doit **choisir réellement** la consultation via sa politique exacte à profondeur 2, plafonnée à 60 milli-unités hypothétiques pour deux consultations, puis le simulateur caché fournit la trace. Au plus cinq consultations actives par épisode.
- Le catalogue identique et le même budget sont donnés au comparateur classique indépendant d'énumération exhaustive deux étapes provenant de OBS-COL-04. Si les politiques coïncident, résultat **nul** pour un gain propre à Omega.
- Chercher un certificat de non-Markov : deux transitions mesurées avec le **même état visible x et la même action**, mais des successeurs visibles différents, après des histoires distinctes. Un tel certificat exclut **toute** dynamique visible déterministe markovienne (dans le périmètre du reset défini), indépendamment des cinq familles.
- Pour un monde hors catalogue, **ne jamais présenter une désignation de famille certaine** : un échec sur les six contrôles réservés doit donner `OUT_OF_CATALOG_WARNING`. Aucune correction par fuite des réponses réservées.

## Critères d'acceptation et d'échec
- Tests de l'interface d'oracle et d'isolement des états réservés ; présence réelle des appels de P1, PR23, garde-fou PR40 et analyse Walsh de PR86 quand pertinente ; audit de concordance avec le solveur deux-étapes indépendant.
- Les cinq mondes connus doivent être classés correctement et prédire les six expériences de réserve ; la sixième cible doit susciter une alerte plutôt qu'une certification erronée.
- Certificat de non-Markov pour tous les mondes à mémoire lorsque des traces contradictoires sont effectivement mesurées ; ne pas déclarer de certificat sans témoin.
- Échec explicite si le modèle vrai est éliminé des candidats dans un monde connu, si une prédiction réservée est utilisée pour sélectionner le modèle, ou si des appels artificiels sont présentés comme un modèle externe autonome.
- Rapport statistique/épistémique : ces règles et sondes sont produites par le concepteur, les familles mathématiques sont données ; une réussite n'est donc ni découverte ouverte, ni théorie nouvelle, ni mesure d'intelligence d'Omega supérieure à un classique.

Ne pas fusionner, ne pas mettre à jour CORE, ne pas déployer d'agent autonome.
