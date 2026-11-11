# Protocole expérimental — adaptativité du Prisme Omega (v0.1)

**Date :** 10 novembre 2026  
**Branche :** `work/benchmark-prisme-adaptatif-v0-1-2026-11-10`  
**Base :** `architecture/memoire-agentique-native-2026-11-05`  
**Statut :** protocole proposé, non exécuté ; aucun résultat expérimental revendiqué.

## 1. Question de recherche

L'architecture adaptative d'Omega améliore-t-elle, à budget comparable, la qualité et la calibration des réponses en choisissant le niveau de vérification nécessaire, plutôt qu'en appliquant systématiquement une analyse simple ou une décomposition multi-rôles ?

Question secondaire : les propriétés de dépendance et de profondeur observées dans nos modèles mathématiques peuvent-elles fournir des indicateurs utiles pour décider quand approfondir une analyse ?

**Précaution centrale :** le résultat mathématique L+1 (absence de contre-exemple dans l'énumération finie n≤6, L=2,3) ne démontre aucune règle de routage d'agents. Le benchmark doit tester séparément la valeur de l'adaptativité. Toute correspondance entre profondeur orbitale et profondeur de raisonnement reste une hypothèse opérationnelle, pas un théorème.

## 2. Hypothèses falsifiables

- H1 — À budget moyen comparable, Omega adaptatif réduit le taux d'erreur par rapport à ChatGPT seul.
- H2 — À budget moyen comparable, Omega adaptatif réduit le taux d'erreur par rapport à Omega à rôles fixes.
- H3 — L'adaptatif détecte mieux les cas sous-déterminés et s'abstient plus justement, sans augmenter excessivement les faux refus.
- H4 — Des indicateurs explicites de dépendance (nombre de prémisses nécessaires, profondeur de chaîne, présence d'une information cachée, contradiction entre sources) prédisent une partie du bénéfice d'une vérification supplémentaire.
- H5 — Le gain subsiste sur un jeu de test tenu à l'écart de la conception et des réglages.

Chaque hypothèse peut être réfutée. Un résultat nul est informatif.

## 3. Trois systèmes comparés

A. **Référence simple** : un seul modèle, une seule passe, sans décomposition orchestrée. Les outils externes sont désactivés sauf lorsqu'ils sont explicitement autorisés dans le sous-ensemble correspondant.

B. **Omega à rôles fixes** : même modèle de base et même budget maximal ; rôles prédéfinis (formalisation, réfutation, vérification/calcul, synthèse) exécutés systématiquement, même si certains rôles sont inutiles.

C. **Omega adaptatif** : un routeur examine le problème, estime les risques et choisit parmi : réponse directe ; clarification ; recherche de source ; calcul/test ; deuxième perspective indépendante ; audit contradictoire ; abstention. Il doit consigner la raison de chaque escalade et le critère d'arrêt.

**Équité de comparaison :** même modèle de base, mêmes consignes de vérité, mêmes outils autorisés, mêmes données, mêmes limites de temps et de budget par tâche. Comparer à la fois (i) qualité à budget égal et (ii) coût nécessaire pour atteindre un seuil de qualité donné. Enregistrer tokens, appels d'outils, temps écoulé et nombre de passes.

## 4. Batterie de tâches

La batterie initiale comprend six familles. Les réponses de référence et les critères de notation doivent être écrits avant l'exécution.

| Famille | Construction | Ce qu'elle teste | Signal attendu d'escalade |
|---|---|---|---|
| T1. Déduction déterminée | Petits systèmes finis avec règles explicites et solution calculable exactement | Exactitude sans sur-analyse | Peu de dépendances, calcul court |
| T2. Dépendance en chaîne | Problèmes où la conclusion dépend de 2, 3, 4… prémisses liées | Détection de profondeur réelle | Longueur de chaîne et dépendances |
| T3. Information manquante | Énoncés volontairement sous-déterminés ; plusieurs réponses compatibles | Capacité à demander une précision ou s'abstenir | Variable nécessaire absente |
| T4. Contre-exemples et cas limites | Règles générales confrontées à petits cas minimaux, extrêmes ou atypiques | Réfutation avant conclusion | Généralisation fragile, quantificateurs |
| T5. Recherche documentaire | Questions dont la réponse dépend de sources externes datées et vérifiables | Recherche, provenance, recoupement | Fraîcheur, désaccord ou source faible |
| T6. Contradictions | Dossier contenant assertions incompatibles, versions ou données divergentes | Détection et résolution explicite des conflits | Incohérence entre éléments |

T1–T4 doivent d'abord être générées de façon synthétique avec un oracle exact (énumération, solveur ou calcul vérifié). T5–T6 forment un lot distinct : leurs références sont établies par deux évaluateurs indépendants et chaque source doit être archivée avec sa date. Ne pas mélanger les scores synthétiques et documentaires sans présenter les résultats par famille.

### Taille initiale proposée

- Pilote : 12 tâches par famille (72 tâches), pour déboguer le protocole.
- Évaluation : au moins 50 tâches par famille (300 tâches), avec variantes paramétriques et graines consignées.
- Holdout : 20 % des tâches, scellées avant le réglage du routeur ; aucun exemple ni paraphrase proche ne doit apparaître dans le pilote.

Ces tailles sont des objectifs de conception, pas des résultats déjà obtenus. Une analyse de puissance pourra les augmenter si les différences observées sont faibles.

## 5. Mesures

**Mesures principales**
1. Exactitude / validité : proportion de réponses conformes à l'oracle ou à la grille de référence.
2. Détection du manque d'information : rappel et précision sur T3.
3. Détection des contradictions : rappel, précision et qualité de résolution sur T6.
4. Calibration : adéquation entre confiance annoncée et fréquence réelle de réussite ; utiliser Brier score si une probabilité numérique est recueillie.
5. Coût : tokens, appels d'outils, temps et coût monétaire disponible.

**Mesures de sécurité méthodologique**
- Faux refus sur les tâches déterminées.
- Affirmations non sourcées sur T5.
- Erreurs introduites par les étapes supplémentaires.
- Taux d'escalade inutile : escalade sans amélioration de qualité.
- Taux d'arrêt prématuré : absence d'escalade alors qu'une vérification aurait corrigé l'erreur.

Ne pas réduire tous ces axes à un score composite unique. Publier les résultats par famille et les compromis qualité/coût.

## 6. Fiche de décision du routeur

Pour chaque tâche, le routeur doit produire avant de répondre une fiche structurée :

- Déterminabilité : déterminée / sous-déterminée / inconnue.
- Dépendances nécessaires : liste des prémisses ou données manquantes.
- Risques : ambiguïté, fraîcheur, calcul, contradiction, généralisation.
- Action choisie : direct / clarification / source / calcul / perspective indépendante / audit / abstention.
- Motif observable de l'action.
- Critère d'arrêt : quel résultat permet de conclure ?
- Résultat après vérification : confirmé / corrigé / indéterminé.
- Coût total.

Les catégories ne doivent pas être déduites après coup de la réponse : elles sont enregistrées avant l'exécution afin d'éviter un classement rétrospectif favorable.

## 7. Déroulement et indépendance

1. Geler les tâches, les réponses de référence, les budgets et les règles de notation.
2. Faire exécuter A, B et C sur les mêmes tâches, dans un ordre randomisé.
3. Utiliser des identifiants anonymes ; les évaluateurs ne savent pas quelle configuration a produit la réponse.
4. Pour les tâches synthétiques, comparer automatiquement à l'oracle exact.
5. Pour les tâches documentaires, deux évaluateurs notent indépendamment ; arbitrage des désaccords documenté.
6. Répéter un sous-échantillon avec une nouvelle graine ou un nouvel ordre pour mesurer la variance.
7. N'ajuster le routeur que sur le pilote ; ne jamais retoucher ses règles après ouverture du holdout.
8. Publier les échecs, les cas indéterminés et les coûts, pas seulement les réussites.

## 8. Analyse

Pour chaque famille, rapporter :
- score et intervalle de confiance à 95 % ;
- différence appariée A–B, A–C et B–C ;
- coût médian et distribution des coûts ;
- matrice des erreurs et des escalades ;
- exemples de gains, de régressions et de cas sans différence.

L'unité statistique est la tâche, avec appariement entre configurations. Les variantes issues d'un même gabarit doivent être regroupées lors du calcul d'incertitude afin de ne pas les traiter comme entièrement indépendantes.

Un gain n'est retenu que s'il est reproductible sur le holdout, matériel au regard d'un seuil fixé avant l'analyse, et obtenu sans dégradation inacceptable des faux refus ou du coût.

## 9. Test spécifique du lien avec L+1/L+2

Ne pas injecter directement les symboles L+1 ou L+2 dans le routeur. Construire d'abord une représentation neutre des tâches :
- profondeur minimale de dépendance connue ;
- quantité d'information disponible dans le préfixe fourni ;
- existence d'une information tardive qui change ou non la conclusion ;
- différence entre conclusion globale et conclusion calculée à partir du préfixe.

Sur T1–T4, ces variables sont calculables exactement. Tester ensuite si elles prédisent le bénéfice marginal d'une étape supplémentaire. Il faut comparer ce prédicteur à des baselines simples (longueur du prompt, nombre de prémisses, ambiguïté détectée). Si les variables de profondeur n'apportent aucune prédiction hors échantillon, le lien opérationnel n'est pas utile et doit être abandonné.

Le résultat L+1 actuel sert uniquement à motiver des cas où une profondeur supplémentaire pourrait être redondante. Il ne fournit ni seuil, ni règle de routage, ni preuve de gain pour Omega.

## 10. Conditions de verdict

- **GAIN ADAPTATIF ÉTABLI** : C dépasse A et B sur le holdout selon les critères préenregistrés, à coût comparable ou avec un compromis coût/qualité explicitement meilleur.
- **GAIN PARTIEL** : avantage limité à certaines familles ; le routeur doit être restreint à ces familles.
- **PAS DE GAIN DÉMONTRÉ** : différences faibles, instables ou absentes.
- **RÉGRESSION** : C dégrade la qualité, la calibration ou la sécurité méthodologique.
- **INDÉTERMINÉ** : puissance ou qualité des références insuffisante.

Aucun résultat de ce benchmark ne certifiera à lui seul une proposition mathématique de V19. Réciproquement, un théorème sur L+1/L+2 ne certifiera pas l'efficacité de l'architecture Omega.

## 11. Livrables avant toute conclusion

- générateur versionné des tâches synthétiques ;
- oracle et tests unitaires ;
- jeu pilote et holdout séparés ;
- spécification des trois configurations et budgets ;
- journal brut des exécutions ;
- script d'analyse et rapport reproductible ;
- registre des écarts au protocole ;
- verdict par hypothèse, y compris les hypothèses réfutées.

**Décision actuelle :** protocole défini ; aucune comparaison A/B/C exécutée. Prochaine étape technique : construire T1 et T3 avec oracle exact, puis vérifier que les trois configurations peuvent être exécutées dans des conditions réellement comparables.
