# P5 — compréhension des preuves et comparaison A/B/C/D, calibration publique

**Version :** 0.1 expérimentale, 10 novembre 2026.
**Statut :** protocole + extracteur documentaire strict, **aucune étude A/B/C/D
sur les sorties de modèles réalisée**. Cet ajout s'appuie sur la PR #24
sans la fusionner, sans altérer `main` et sans créer d'autre mémoire.

## Question de recherche

Est-ce que la capacité de produire soi-même un état des preuves à partir
de documents apporte une meilleure **décision finale vérifiable** qu'une
réponse directe, un prisme de rôles fixes ou une planification recevant
déjà des éléments structurés ?

Le risque critique est de confondre une bonne politique sur un modèle
donné et la capacité d'**élaborer le bon modèle**.

## Quatre bras, à interpréter séparément

- **A :** question et documents, réponse directe.
- **B :** mêmes éléments et livrables, cinq perspectives fixes.
- **C :** mêmes documents mais **contexte décisionnel supplémentaire fourni**,
  avec les perspectives choisies par P1. **Ce bras est une ablation
  privilégiée** ; il ne représente PAS une comparaison à information égale.
  Sa performance doit être rapportée séparément.
- **D :** mêmes documents, invitation à reconstruire les faits, leurs
  sources et les incertitudes **avant** de choisir l'action.

`prism/p5_four_arm_protocol.py` prépare, sans les exécuter, les prompts
des quatre bras, avec mêmes documents, question et livrables communs.
Chaque demande possède une empreinte SHA-256. Le module ne produit
aucune sortie de modèle, aucun score, aucun temps ni coût fictif.
Une expérimentation réelle doit utiliser un modèle/snapshot identique,
un budget identique, des contextes isolés et un ordre des bras randomisé.

**L'action de P1 n'est pas une prédiction de réponse correcte :**
les verdicts doivent être notés séparément de l'action choisie.

## Calibration locale réellement exécutable

`prism/evidence_extraction_pilot.py` propose un **parseur conservateur**
qui reconnaît une grammaire documentaire étroite :

- une notice officielle donnant deux délais et la date de bascule ;
- une ou plusieurs dates de réception dans un registre ;
- un message interne secondaire, non autorisé à modifier la règle ;
- la disponibilité déclarée de la notice et du registre.

Il choisit `answer`, `ask`, `verify` ou
`insufficient_evidence`, puis transmet son contexte au P1 existant.
Pour `answer`, il fournit un délai et une référence explicite.

Le parseur **ne lit pas le langage naturel général**, ne déduit pas
la crédibilité d'une source, et ne vérifie ni les métadonnées ni
l'authenticité. Les noms de rôles des documents et la disponibilité
des registres sont déjà **fournis comme métadonnées** ; cette
information n'est pas reconstruite par Omega.

`prism/evidence_calibration_24.py` crée 24 cas **PUBLICS ET CONSTRUITS
DANS CETTE EXPÉRIENCE** : quatre jeux de dates/délais × six structures
(avant seuil, après seuil, réception absente, deux dates contradictoires,
notice accessible mais absente, notice inaccessible). Ils incluent
des notes internes trompeuses et des cas d'abstention. Ces 24 cas ne
sont ni un holdout, ni statistiquement indépendants, ni des tâches
représentatives du monde réel ; ils sont une calibration de logiciel.

`prism/test_evidence_extraction_p5.py` contrôle les 24 décisions,
les refus d'inventer, les mutations documentaires, l'ordre des
documents, le raccordement P1, l'absence d'appels de modèles,
les 96 prompts d'entrée A/B/C/D et l'interdiction des clés de
réponses dans les entrées. Les anciennes suites P1–P5 restent actives.

## Reproduction

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python -m unittest -v test_evidence_extraction_p5
python evidence_calibration_24.py
```

GitHub Actions exécute `python -m unittest -v` sur l'ensemble
du dossier ; lire les journaux et la version de commit avant
d'annoncer des nombres vérifiés.

## Conditions nécessaires pour une vraie campagne A/B/C/D

1. **Geler indépendamment** un jeu de cas réellement inédit, créé ou
   choisi sans accès aux solutions par les systèmes évalués.
   Les calibrations publiques précédentes ne doivent pas servir
   de holdout secret. Choisir des tâches aux réponses clairement
   vérifiables dans plusieurs domaines et des situations demandant
   une nouvelle vérification, non seulement un tri de dates.
2. **Pré-enregistrer** questions, sources, budget, modèle/snapshot,
   droit d'accès aux outils, critères, évaluateurs, méthode d'analyse,
   politique d'abstention, et seuils de succès/échec.
3. Ne jamais fournir un corrigé dans les prompts. Pour C,
   préparer ses hypothèses structurées indépendamment du corrigé,
   consigner provenance et coût de cette préparation, et garder
   l'ablation à information privilégiée **hors de la conclusion
   causale sur le seul routage**.
4. Produire réellement des réponses A/B/C/D en sessions isolées
   avec la même version de modèle, le même accès aux outils,
   le même plafond et une trace des appels/couts. **Aucun appel n'est
   lancé par cette PR**.
5. Deux correcteurs humains indépendants, aveugles aux bras,
   doivent noter d'abord la **décision finale correcte**, puis
   les sources, abstentions, erreurs, coûts et durées. Geler et
   signer les notes avant l'ouverture de la clé privée.
6. Analyser sur les cas appariés, sans confondre répétitions et
   taille d'échantillon ; publier les échecs et intervalles de
   confiance quand adaptés. Distinguer qualité, coût, robustesse,
   transfert aux cas inédits, et information additionnelle reçue
   par C. Utiliser le pipeline d'analyse P5 existant plutôt
   que créer une seconde méthode de notation.

**Aucune augmentation de qualité générale ni indépendance multiagent
n'est revendiquée par cette PR.** L'extracteur lexical représente
seulement une étape minimale, falsifiable et testable.
