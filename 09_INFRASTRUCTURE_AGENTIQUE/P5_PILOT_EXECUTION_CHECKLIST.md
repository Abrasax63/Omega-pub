# P5 — préparation du pilote A/B/C et audit du holdout

**Date :** 2026-11-10  
**Protocole de référence :** P5 v0.2  
**Branche de travail :** `audit/p5-hardening-2026-11-09`  
**Statut :** préparation méthodologique ; pilote NON LANCÉ ; holdout NON GELÉ.

## 1. Décision de sécurité expérimentale

Le cas privé `P5V2-EXPL-001` a été corrigé. Les parcours microscopiques sont désormais distingués par système : T1 suit `a1→b1→a1`, T2 suit `a1→b1→a2`. Les deux se projettent sur la trace observée `A→B→A`. Le fichier JSON corrigé a été relu et contrôlé par un script indépendant : transitions des parcours, projection, totalité des applications et cohérence des transitions macroscopiques déclarées.

L'empreinte SHA-256 du fichier privé corrigé est publiée dans le manifeste public `evaluation/holdout_v0_2/manifest.json`. Le corrigé et ses parcours attendus restent strictement privés ; seul le digest est public.

Ne pas réutiliser comme holdout aveugle les cas v0.1 déjà exposés dans l'historique public.

**Règle anti-contamination :** aucun résultat, aucune note et aucun retour issu du pilote ne peut servir à modifier le planificateur, les prompts, les rôles ou les règles de routage avant le gel complet des sorties et des notes. Toute modification ultérieure crée une version candidate distincte et impose un jeu de test indépendant.

## 2. Portes de lancement (toutes obligatoires)

| Porte | Condition vérifiable | État |
|---|---|---|
| G1 | Corrigé privé corrigé, relu et cohérent avec les définitions des cas | **SATISFAIT pour P5V2-EXPL-001** |
| G2 | Empreinte SHA-256 recalculée sur les octets exacts du corrigé final | **SATISFAIT** |
| G3 | Manifeste public mis à jour avec ID, version et empreintes autorisées, sans contenu secret | **SATISFAIT** |
| G4 | Cas v0.2 distincts du matériel v0.1 public et absence de fuite vérifiée | À AUDITER |
| G5 | Modèles, snapshots, paramètres et prompts A/B/C explicitement fixés | NON RENSEIGNÉ |
| G6 | Budget commun par cas/bras et mesures réellement accessibles définis | NON RENSEIGNÉ |
| G7 | Ordre randomisé, graine protégée et table d'aveuglement séparée | NON RENSEIGNÉ |
| G8 | Deux évaluateurs indépendants disponibles et procédure aveugle praticable | NON RENSEIGNÉ |
| G9 | Barème, arbitrage et gestion des données manquantes gelés | À FINALISER |
| G10 | Tests du validateur réussis sur données synthétiques positives et négatives | À REPRODUIRE |

Le lancement est interdit tant qu'une porte critique est BLOQUÉE ou NON RENSEIGNÉE. La satisfaction de G1–G3 ne vaut pas gel global du holdout.

## 3. Plan de collecte A/B/C

Unité expérimentale : un couple (cas, bras). Chaque cas reçoit une sortie de chacun des trois bras, dans des sessions séparées et réinitialisées.

Pour chaque sortie, conserver dans un enregistrement immuable :

- `campaign_id`, `protocol_version`, `case_id`, `opaque_output_id` ;
- bras réel dans une table de correspondance privée, jamais dans le fichier remis aux évaluateurs ;
- modèle exact, fournisseur, snapshot/version, paramètres et limites de génération ;
- hash du prompt système, hash du prompt utilisateur et hash du contexte initial ;
- commit du code Omega et configuration des rôles fixes B ;
- décisions de routage de C, avec horodatage et motif codifié ;
- outils autorisés, outils demandés, outils réellement appelés et résultat d'appel ;
- tokens/coût/latence seulement lorsqu'ils sont réellement fournis par l'environnement ;
- durée murale, statut de fin, interruption, erreur et cause connue ;
- sortie brute exacte et empreinte SHA-256 de cette sortie.

Ne pas inférer les tokens ou coûts à partir de la longueur du texte. Si une mesure n'est pas accessible, enregistrer `NOT_AVAILABLE`, avec la raison.

## 4. Instrumentation des décisions du Prisme

Objectif : mesurer le comportement adaptatif, et non simplement compter les rôles affichés.

Pour chaque décision du planificateur, enregistrer :

1. **État d'entrée :** identifiant du cas, signaux observables utilisés, contraintes détectées.
2. **Décision :** `DIRECT`, `DECOMPOSE`, `INDEPENDENT_CHECK`, `COUNTEREXAMPLE_SEARCH`, `SOURCE_CHECK`, `ABSTAIN` ou autre action explicitement définie avant le pilote.
3. **Motif :** code de justification choisi dans une taxonomie préétablie, plus justification textuelle courte.
4. **Alternatives :** action concurrente écartée et raison, si le planificateur les expose.
5. **Exécution :** action réellement exécutée, échec éventuel, coût/latence disponible.
6. **Résultat local :** élément nouveau trouvé, erreur détectée, contre-exemple trouvé, ou absence de gain observable.
7. **Lien de provenance :** sortie ou observation qui a déclenché la décision.

### Taxonomie minimale des déclencheurs à pré-enregistrer

- `UNCERTAINTY_HIGH` : ambiguïté ou information insuffisante ;
- `MULTIPLE_SUBCLAIMS` : plusieurs sous-affirmations séparables ;
- `COUNTERMODEL_POSSIBLE` : recherche de contre-modèle discriminant ;
- `SOURCE_DEPENDENT` : affirmation dépendante d'une source externe ;
- `CALCULATION_CHECKABLE` : calcul exact ou vérification mécanique possible ;
- `CONTRADICTION_SIGNAL` : incohérence détectée entre étapes ou affirmations ;
- `LOW_EXPECTED_VALUE` : coût attendu supérieur au bénéfice anticipé ;
- `DIRECT_SUFFICIENT` : réponse directe jugée suffisante.

Les seuils et règles qui associent ces déclencheurs à une action doivent être fixés avant le pilote. Ils ne doivent pas être ajustés après inspection des résultats du holdout.

## 5. Mesurer le gain et la dégradation de l'adaptation

Pour chaque cas, les évaluateurs aveugles notent séparément :

- exactitude ;
- qualité des justifications et des sources ;
- pertinence des contre-exemples et tentatives de réfutation ;
- détection des erreurs présentes dans l'énoncé ou dans une réponse intermédiaire ;
- calibration et reconnaissance des limites ;
- traçabilité/reproductibilité.

L'analyse des décisions du Prisme est secondaire et descriptive au pilote. Elle ne doit pas être utilisée comme substitut à l'évaluation des réponses.

Une adaptation est un **gain observé** uniquement si elle améliore une dimension pré-définie par rapport aux bras A et B sur le même cas, sans masquer une régression importante sur une autre dimension. Une adaptation est une **dégradation observée** si elle introduit une erreur, manque un contre-exemple, ajoute une affirmation non étayée, augmente le coût sans bénéfice mesuré, ou retarde/empêche une réponse correcte. Les cas sans différence claire restent `INDETERMINATE`.

Ne pas agréger les dimensions en un score global tant que les pondérations ne sont pas justifiées et pré-enregistrées. Publier les différences appariées par cas et les désaccords entre évaluateurs.

## 6. Analyse des limites du pilote

Cinq cas constituent un pilote de faisabilité et de détection de défauts, pas un échantillon suffisant pour établir une supériorité générale. Les résultats devront être présentés comme descriptifs et exploratoires. Pas de revendication de significativité ou de généralisation à partir de ce seul pilote.

Le pilote doit répondre d'abord à ces questions :

- Les trois bras ont-ils été exécutés dans des conditions comparables ?
- Les sorties ont-elles été correctement aveuglées ?
- Les évaluateurs ont-ils pu noter chaque sortie sans connaître le bras ?
- Les journaux permettent-ils de reconstruire les décisions et les coûts réellement observables ?
- Le validateur détecte-t-il les jeux de notes incomplets ou déséquilibrés ?
- Le protocole révèle-t-il des modes d'échec du Prisme, pas seulement ses réussites ?

## 7. P5 v0.3 — exigences de conception, pas encore un jeu de test

La version v0.3 devra être conçue après l'analyse du pilote, mais ses cas ne devront pas être dérivés en reformulant simplement les cinq cas v0.2. Prévoir plusieurs cas par strate et des variantes indépendantes :

- preuve avec quantificateurs et hypothèses proches mais non équivalentes ;
- calcul fini avec vérification croisée et cas limite ;
- recherche documentaire avec source primaire et conflit entre sources ;
- système observé avec plusieurs extensions microscopiques compatibles ;
- affirmation fausse nécessitant un contre-exemple minimal ;
- cas où la décomposition est inutile ou nuisible ;
- cas où une vérification indépendante détecte une erreur plausible ;
- cas où l'outil ou la source externe est indisponible et où l'abstention est préférable.

Les nouveaux cas doivent être écrits indépendamment des sorties du pilote, puis contrôlés contre les fuites et les ambiguïtés. Le corrigé et les barèmes restent privés jusqu'à la fin de l'évaluation.

## 8. État de travail au 2026-11-10

- Protocole v0.2 et validateur : présents dans la PR #9 en brouillon.
- Corrigé privé : correction de P5V2-EXPL-001 effectuée et contrôlée.
- SHA-256 privé : recalculé sur les octets exacts ; digest publié sans divulguer le corrigé.
- Manifeste public : créé dans `evaluation/holdout_v0_2/manifest.json`.
- Pilote A/B/C : non exécuté.
- Notation humaine : non exécutée.
- G4–G10 : non satisfaites ou non vérifiées.
- Analyse des décisions adaptatives : schéma de collecte préparé ; aucune donnée observée.
- P5 v0.3 : exigences de conception uniquement ; aucun cas finalisé.

**Verdict :** `PILOT_NOT_READY`. G1–G3 sont satisfaites pour la correction examinée ; cela ne constitue ni un gel global du holdout, ni une validation expérimentale, ni une certification de l'architecture Omega.
