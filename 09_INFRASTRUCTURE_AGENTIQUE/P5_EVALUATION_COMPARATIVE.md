# P5 — protocole d’évaluation comparative du prisme Omega

**Version :** 0.2 — durcissement pré-enregistrement  
**Statut :** protocole préparé ; pilote non lancé ; aucune sortie A/B/C ni notation humaine  
**Branche de travail :** `architecture/memoire-agentique-native-2026-11-05`  
**Provenance du durcissement :** PR #9 (`audit/p5-hardening-2026-11-09`)  
**Périmètre :** mesurer l’utilité du routage adaptatif, jamais certifier une vérité scientifique.

## 1. Question et hypothèse nulle

Question : sur les mêmes missions, C (routage adaptatif) produit-il de meilleurs résultats que A (réponse directe) et B (rôles fixes), à ressources comparables ?

Hypothèse nulle opérationnelle : aucune amélioration de C n’est présumée. Une égalité, une régression ou des résultats indéterminés sont des issues recevables. Le pilote à cinq cas est exploratoire et ne permet pas une conclusion statistique générale.

## 2. Bras comparés

- **A — référence :** réponse directe, sans décomposition explicite.
- **B — fixe :** même modèle principal, ensemble de rôles fixé avant l’essai et appliqué de manière constante.
- **C — adaptatif :** plan produit par le planificateur adaptatif de la version testée.

Les rôles de B et C sont des perspectives d’un même agent, non des agents indépendants. Il faut donc parler de « perspectives » et non de validation multi-agent indépendante.

## 3. Gel des cas et contamination du corrigé

Le jeu pilote v0.1 contient cinq cas, un par strate. Il est trop petit pour estimer un effet de domaine ou une supériorité générale.

**Alerte critique :** le corrigé v0.1 a été commité dans un dépôt public. Il doit être considéré comme compromis et ne peut plus servir de corrigé secret pour une évaluation véritablement aveugle. Le supprimer aujourd’hui ne supprimerait pas les copies, clones ou historiques déjà accessibles. Ne pas lancer une notation aveugle avec ce corrigé.

Pour poursuivre un test réellement aveugle :
1. créer un nouveau jeu v0.2 indépendant, sans réutiliser les énoncés exacts v0.1 ;
2. garder le corrigé et les critères détaillés dans un espace privé non accessible aux systèmes évalués ni aux évaluateurs pendant la génération ;
3. ne publier dans le dépôt public que les identifiants, la procédure et les empreintes cryptographiques du jeu/corrigé, jamais le corrigé ;
4. faire vérifier le contenu et le corrigé par un responsable qui ne participe pas à la génération ni à la notation ;
5. enregistrer les empreintes avant les essais et ne modifier ensuite ni cas, ni barème, ni prompts.

Le jeu v0.1 peut rester un jeu de développement/public, mais ses résultats ne devront pas être présentés comme aveugles si les réponses de référence ont été exposées aux systèmes ou aux évaluateurs.

## 4. Pré-enregistrement obligatoire

Avant la première génération, remplir et verrouiller un manifeste contenant au minimum :

- identifiant/version et empreinte SHA-256 de chaque cas ;
- empreinte du corrigé privé, non publié ;
- identifiant exact du modèle, fournisseur, version/snapshot et paramètres ;
- date/heure, environnement et limites de contexte ;
- prompt système et prompt utilisateur exacts de A, B et C ;
- commit Git du planificateur et configuration de B ;
- outils autorisés, versions et règles d’accès aux sources ;
- budget maximal par cas et par bras (tokens ou autre unité disponible), nombre maximal d’appels et plafond de durée ;
- ordre de génération randomisé et graine conservée ;
- règles de gestion des erreurs, interruptions et données manquantes ;
- barème et règle d’arbitrage ;
- identité/indépendance des évaluateurs, conservée séparément des réponses.

Ne pas inventer les valeurs manquantes : inscrire « non disponible » ou bloquer le lancement jusqu’à décision. Les budgets doivent être identiques ou leurs écarts consignés explicitement. Aucun résultat ne doit être comparé si les conditions ne sont pas suffisamment comparables.

## 5. Génération

Pour chaque cas :
1. lancer A, B et C dans des sessions séparées et réinitialisées ;
2. randomiser l’ordre des bras par cas ;
3. ne pas transmettre les réponses d’un bras à un autre ;
4. utiliser le même énoncé et le même contexte initial ;
5. capturer prompt exact, contexte, commit, modèle, outils, appels, tokens/coûts disponibles, durée, erreurs et sortie brute ;
6. conserver la correspondance entre identifiants opaques et bras dans un fichier séparé, privé et non transmis aux évaluateurs.

Aucun bras ne doit accéder au corrigé privé.

## 6. Notation aveugle

- Au moins deux évaluateurs réellement indépendants doivent noter chaque sortie.
- Chaque évaluateur note les trois sorties de chaque cas, avec des identifiants opaques, sans connaître les bras ni les notes de l’autre.
- Les évaluateurs ne doivent pas avoir participé à la conception des réponses évaluées ni avoir accès au corrigé secret pendant la génération.
- Les notes initiales sont figées avant arbitrage et avant dévoilement des bras.
- Les désaccords sont arbitrés selon une règle pré-enregistrée ; notes initiales et arbitrage restent séparés.
- Si ces conditions ne sont pas réunies, qualifier l’évaluation de non aveugle ou non indépendante, jamais d’indépendante.

## 7. Grille et mesures

Chaque dimension est notée de 0 à 4 :
- exactitude ;
- justification et qualité des sources ;
- réfutation et contre-exemples ;
- calibration et reconnaissance des limites ;
- traçabilité ;
- préservation des désaccords et hypothèses concurrentes.

Compter séparément les affirmations non étayées, erreurs matérielles et contre-exemples manqués. La longueur et le nombre de rôles ne donnent aucun point en soi.

Mesures opérationnelles : durée, appels/outils, tokens et coût si disponibles, échecs, perspectives planifiées/exécutées, erreurs et données manquantes. Publier chaque dimension séparément ; ne pas inventer de score composite ni de pondération après observation des résultats.

## 8. Analyse et conclusion

- Comparaison appariée par cas ; présenter chaque cas et chaque strate.
- Décrire les effectifs, données manquantes, désaccords et incertitudes.
- Ne pas traiter cinq cas hétérogènes comme un échantillon représentatif.
- Distinguer qualité, coût/latence, traçabilité et robustesse.
- Toute modification du planificateur après examen du jeu exige une nouvelle version de test indépendante.
- Conclusion autorisée pour v0.1 : seulement « signal exploratoire » ou « indéterminé ». « Amélioration démontrée » exige un échantillon adéquat, un protocole pré-enregistré, des évaluateurs indépendants et des résultats robustes.

## 9. Capacités et limites du validateur

Le validateur v0.2 contrôle la structure des notes : trois sorties opaques par cas, au moins deux évaluateurs communs à toutes les sorties d’un cas, couverture des cas attendus, absence de doublons et valeurs numériques finies. Il ne vérifie pas l’identité réelle ou l’indépendance des évaluateurs, la randomisation, l’aveuglement, la qualité du corrigé ou la vérité des réponses. Il ne calcule aucune significativité et ne délivre aucune certification RAVI-2.

Le prototype P1–P4 ne lance pas de modèles ni les bras A/B/C. La génération et la collecte doivent donc être conduites et consignées séparément.
