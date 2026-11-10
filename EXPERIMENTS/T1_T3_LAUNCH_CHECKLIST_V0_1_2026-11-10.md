# Checklist de lancement T1/T3 et pilote Omega — v0.1

**Date :** 10 novembre 2026  
**Branche :** `work/benchmark-prisme-adaptatif-v0-1-2026-11-10`  
**PR :** [#19 — Protocole expérimental du routage adaptatif Omega v0.1](https://github.com/Abrasax63/Omega-pub/pull/19)  
**Statut :** générateurs T1/T3 testés en CI ; pilote comparatif non lancé.

## 1. État vérifié

- [x] Définitions T1 (déterminé) et T3 (sous-déterminé) consignées dans `OMEGA_T1_T3_GENERATORS_SPEC_V0_1_2026-11-10.md` (contenu actuellement versionné comme contrat v0.2).
- [x] Séparation des paquets publics et privés implémentée dans les générateurs.
- [x] Validateur T3 recalculant les sorties des témoins depuis les paramètres publics.
- [x] Workflow GitHub Actions dédié présent.
- [x] CI exécutée avec succès : run [42795937582](https://github.com/Abrasax63/Omega-pub/actions/runs/42795937582), job `unit-tests`, Python 3.12.
- [x] Les logs de ce run attestent **12 tests exécutés, 12 réussis** (`Ran 12 tests`, `OK`).
- [ ] Revue indépendante de la conception des générateurs et du contrat anti-fuite.
- [ ] Génération et gel du lot pilote.
- [ ] Comparaison A/B/C.
- [ ] Génération séparée et gel du holdout.
- [ ] Analyse des résultats et décision RAVI-2.

**Portée du succès CI :** il valide les 12 tests logiciels présents dans ce commit. Il ne démontre ni la qualité des réponses des systèmes évalués, ni un gain d'Omega, ni la validité générale du routage adaptatif.

## 2. Format canonique d'une tâche

Le format logique commun est le suivant. Il doit être sérialisé en deux fichiers ou flux distincts : un paquet public remis au système, et un paquet privé réservé à l'évaluateur.

### Paquet public — exemple T1

```json
{
  "task_id": "T1-<identifiant opaque>",
  "family": "T1",
  "prompt": "Valeur initiale : x = 3 ... Quelle est la valeur finale ?",
  "public_parameters": {
    "initial": 3,
    "steps": [[2, 1], [3, -4], [1, 5]]
  },
  "generation": {
    "generator_version": "0.1",
    "k": 3,
    "coefficient_bound": 5
  }
}
```

Le paquet public ne contient ni graine, ni réponse attendue, ni paramètre caché, ni témoin.

### Paquet privé — exemple conceptuel T1

```json
{
  "task_id": "T1-<même identifiant opaque>",
  "family": "T1",
  "expected_status": "DETERMINED",
  "expected_answer": 22,
  "seed": "<privée>",
  "generator_version": "0.1"
}
```

### Paquet public — exemple T3

```json
{
  "task_id": "T3-<identifiant opaque>",
  "family": "T3",
  "prompt": "x = 3 ; f1(x) = 2x + 1 ; f2(x) = 3x + b, b non fourni. Quelle est la valeur finale ?",
  "public_parameters": {
    "initial": 3,
    "first_step": [2, 1],
    "second_step_coefficient": 3,
    "missing_parameter": "b"
  },
  "generation": {
    "generator_version": "0.1"
  }
}
```

### Paquet privé — exemple conceptuel T3

```json
{
  "task_id": "T3-<même identifiant opaque>",
  "family": "T3",
  "expected_status": "UNDERDETERMINED",
  "missing_information": "b",
  "witness_completions": [
    {"b": 0, "answer": 21},
    {"b": 4, "answer": 25}
  ],
  "seed": "<privée>"
}
```

Ces exemples décrivent le contrat de données ; ils ne constituent pas un lot expérimental.

## 3. Verrous avant génération du pilote

### A. Revue du générateur et des oracles

- [ ] Vérifier que l'oracle T1 recalcule la chaîne à partir du paquet public désérialisé, sans réutiliser la sortie du générateur.
- [ ] Vérifier que T3 possède au moins deux complétions compatibles avec toutes les informations publiques et conduisant à des sorties distinctes.
- [ ] Ajouter ou documenter un contrôle de cohérence entre le texte du prompt et `public_parameters` : le prompt ne doit pas annoncer une équation différente des paramètres transmis à l'oracle.
- [ ] Tester les bornes et cas extrêmes : profondeur 1, 2 et supérieure ; coefficients négatifs ; coefficient égal à 1 ; valeurs nulles ; valeurs de grande amplitude.
- [ ] Vérifier les sérialisations réelles des paquets public et privé, pas seulement les objets en mémoire.
- [ ] Vérifier qu'aucun champ privé ne fuit par les identifiants, noms de fichiers, journaux, métadonnées ou messages d'erreur.
- [ ] Faire relire indépendamment le validateur T3 et les tests négatifs.

### B. Gel du pilote

- [ ] Définir à l'avance les strates T1/T3 et les niveaux de difficulté.
- [ ] Définir le nombre de cas par strate avant de regarder les sorties des systèmes ; justifier ce nombre par la précision recherchée et les moyens disponibles.
- [ ] Générer le lot avec une graine conservée dans le dépôt privé de l'évaluateur.
- [ ] Calculer les oracles et valider chaque cas.
- [ ] Produire un manifeste public sans graines ni réponses et un manifeste privé avec les oracles.
- [ ] Calculer et conserver les empreintes SHA-256 des deux manifestes.
- [ ] Geler le lot pilote avant toute évaluation ; toute correction ultérieure produit une nouvelle version et une nouvelle empreinte.

### C. Comparaison appariée A/B/C

Systèmes à comparer :

- **A — référence :** ChatGPT seul, une passe.
- **B — Omega fixe :** rôles fixes spécifiés dans le protocole.
- **C — Omega adaptatif :** routeur choisissant parmi réponse directe, clarification, recherche, calcul, vérification indépendante, audit ou abstention.

Contrôles :

- [ ] Chaque système reçoit exactement le même paquet public pour chaque tâche.
- [ ] Ordre des systèmes randomisé ou équilibré par tâche.
- [ ] Sessions indépendantes ; aucune réponse d'un système n'est montrée aux autres.
- [ ] Versions des modèles, paramètres, outils disponibles et budgets consignés.
- [ ] Budget maximal comparable et fixé avant l'essai : temps, tokens et appels d'outils.
- [ ] Sorties brutes conservées avec identifiants de tâche et horodatages.
- [ ] Évaluation effectuée à l'aveugle de l'identité du système lorsque c'est possible.

## 4. Barème primaire

Les critères sont scorés séparément ; ne pas les fusionner dans une note opaque.

### T1 — réponse déterminée

- Exactitude de la réponse finale.
- Cohérence du raisonnement ou du calcul avec les étapes fournies.
- Respect du budget et absence d'étapes/outils inutiles.

### T3 — information insuffisante

- Détection correcte de la sous-détermination.
- Identification précise de la donnée manquante.
- Demande de clarification ou réponse conditionnelle correcte.
- Absence d'invention d'une valeur unique.

### Mesures transversales

- Taux de réponses correctes.
- Taux de détection correcte des informations manquantes.
- Taux d'affirmations injustifiées.
- Taux de refus injustifiés.
- Taux de clarifications utiles et inutiles.
- Coût : tokens, appels d'outils et temps.
- Calibration : confiance déclarée, si elle est collectée de façon identique pour les trois systèmes.

Le barème doit être figé avant l'évaluation. Toute modification après observation des résultats doit être signalée et ne peut remplacer silencieusement l'analyse préenregistrée.

## 5. Holdout indépendant

- [ ] Le holdout reste distinct du pilote et inaccessible aux systèmes évalués.
- [ ] Le holdout représente 20 % du corpus total prévu, conformément au protocole PR #19, sauf justification documentée d'une modification avant génération.
- [ ] Les cas du holdout sont générés avec des graines et paramètres séparés.
- [ ] Aucun exemple, corrigé, témoin ou graine du holdout n'est publié dans les prompts, dépôts publics ou journaux accessibles aux systèmes.
- [ ] Les règles de notation sont gelées avant l'ouverture du holdout.
- [ ] Le holdout n'est ouvert qu'après clôture et archivage du pilote.

## 6. Règles de décision

- **Gain adaptatif crédible :** C améliore les critères primaires préenregistrés par rapport à A et B, sans dégradation inacceptable des garde-fous, et le gain se retrouve sur le holdout.
- **Gain partiel :** amélioration limitée à certaines familles ou mesures ; préciser lesquelles, sans généraliser.
- **Absence de gain :** pas d'amélioration reproductible sur les critères primaires.
- **Régression :** C dégrade les critères primaires ou les garde-fous.
- **Indéterminé :** échantillon, qualité des évaluations ou incertitude insuffisants pour trancher.

Aucune conclusion sur L+1/L+2 ne découle directement de ce benchmark. Le lien entre profondeur/dépendance d'une tâche et utilité d'une vérification supplémentaire reste une hypothèse séparée, à tester hors échantillon et à abandonner si elle ne prédit pas de gain.

## 7. Ordre d'exécution recommandé

1. Revue indépendante des générateurs et du contrat anti-fuite.
2. Compléter les tests manquants identifiés en section 3A.
3. Geler le format et la version du générateur.
4. Générer et valider le pilote.
5. Exécuter A/B/C dans des conditions appariées et contrôlées.
6. Analyser le pilote sans ouvrir le holdout.
7. Geler l'analyse et ouvrir le holdout.
8. Rendre un rapport avec données, scripts, empreintes, limites et verdict.

**Règle d'arrêt :** ne pas générer le holdout ni lancer A/B/C tant que la revue indépendante, la cohérence prompt/paramètres et l'anti-fuite ne sont pas validées.

## 8. État final au 10 novembre 2026

- Générateurs T1/T3 : présents.
- Tests unitaires : **12/12 réussis en CI** sur le run 42795937582.
- Workflow : exécuté et terminé avec succès.
- Revue indépendante : à faire.
- Lot pilote : non généré / non attesté.
- Comparaison A/B/C : non exécutée.
- Holdout : non généré / non attesté.
- Gain empirique d'Omega : aucun résultat disponible.

