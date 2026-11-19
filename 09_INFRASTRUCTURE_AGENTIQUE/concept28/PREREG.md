# CONCEPT28 — alignement de concepts NL/Lean, sans génération ni appel modèle

**Préenregistré le 19 novembre 2026 avant l'élaboration du lexique et avant de lire les nouveaux énoncés.** Branche issue de CONTRAST27 #214. Objectif : falsifier une solution alternative **plus modeste** aux deux modèles Qwen qui viennent d'échouer la reconnaissance A/B.

## Constat précédent (données de développement, NE PAS recycler comme nouveau holdout)
CONTRAST27 : 24 sources × deux ordres × deux Qwen ; Qwen 0,5B a donné 14/48 réponses correctement appariées, 17 erronées, 17 refus. Qwen 3B : 2/48 bien appariées, 0 erreur et 46 refus. **0/24 sélection stable à l'inversion** pour les deux modèles. Les réponses de ces 24 cas deviennent des exemples de diagnostic, pas des données d'évaluation nouvelle.

## Hypothèse testable
Une **représentation intermédiaire très restreinte**, qui associe des termes mathématiques du langage naturel à des constantes/tokens Lean **sans prétendre traduire des théorèmes**, peut-elle retrouver le bon document de référence plus souvent que les **correspondances lexicales triviales** sur une nouvelle cohorte ?

## Jeu futur déterministe **avant inspection**
- Source : ProofNet-Verified, commit exact `b7ca411a2abaa6caf3580192b30d865e5bd10bc4`, sources de référence préexistantes revues avec humains + IA par leurs auteurs ; aucun nouvel annotateur pour Omega.
- **24 cas neufs**, en 12 paires : difficiles/proches `(31,32),(33,34),(35,36),(37,38),(39,41),(42,43)` ; plus éloignées `(44,180),(45,181),(46,182),(47,183),(48,184),(49,185)`. Aucun numéro de PROOFNET26 ni CONTRAST27 n'est repris. Ces négatifs sont des paires construites : **non-équivalence sémantique pas indépendamment annotée**.
- Les couples proches et éloignés **doivent être rapportés séparément**, le score global pouvant masquer la trivialité des négatifs éloignés. Aucune exclusion/remplacement d'un cas a posteriori.
- Figer les 24 blob SHA originaux avant exécution de l'évaluateur et conserver les textes bruts et théorèmes Lean sans modifier les hypothèses.
- L'algorithme et le lexique de concepts sont **figés avant l'évaluation** sur ces nouveaux textes. Les entrées NL/Lean du nouveau holdout ne doivent pas être lues pour ajuster les règles.

## 2 baselines sans modèle
1. **Naïf** : tokeniser les mots apparents en NL et dans la signature Lean, supprimer les mots-outils/identifiants trop courts, choisir uniquement si le nombre de mots identiques distingue les candidats.
2. **Concepts typés** : liste bornée et publiée de concepts mathématiques (groupes, espaces vectoriels, connexité, ensembles, limite, etc.) vers constantes Lean (Group, Module, IsConnected, Tendsto, ...) ; scores pondérés des mêmes marqueurs **explicites**, seuil d'au moins 2 et marge d'au moins 2 pour un choix ; sinon `NONE`. Ne jamais créer une hypothèse absente, un domaine ou une preuve.
- Pour chaque cas, deux alternatives A/B équilibrées ; toutes les métriques sont évaluées contre le **lien original de source**, et non contre une preuve de non-équivalence du négatif : nombre de choix, bons appariements, mauvais appariements, abstentions, précision conditionnelle et couverture.
- Tests adversariaux : permutation des candidats invariance, falsification des empreintes Git, source hors corpus, inconnus, chevauchement de mots sans sémantique, candidats identiques, prompts contenant le nom de l'exercice et faux accord sur concepts partagés. Aucun mécanisme ne doit transformer un concept détecté en théorème certifié.

## Interprétation
- Si le détecteur conceptuel n'améliore pas la couverture et/ou la précision par rapport au naïf, **réfuter l'apport du lexique actuel** ; ne pas complexifier le projet à partir des mêmes données.
- Si un gain existe sur les cas éloignés uniquement, ce sera **une capacité de tri par domaine**, pas une preuve de compréhension des mathématiques, ni une réponse à la généralisation hors domaines.
- Un gain sur les paires proches suggère une première capacité de discrimination fine, mais les négatifs n'étant pas annotés indépendamment, l'équivalence mathématique réelle demeure **indéterminée**.
- Pas de LLM supplémentaire, pas de GPU, aucune API payante, pas de Lean compilé, aucune certification ni modification de `main`. CI en lecture seule et PR DRAFT.
