# BR-DESC-01 — Suffisance pour une tâche ≠ autonomie de mise à jour

**Statut : DÉMONTRÉ sur le modèle de référence ; principe général connu.**

## Énoncé réutilisable
Une description peut être exactement suffisante pour une tâche prédictive donnée tout en étant insuffisante pour être mise à jour de façon autonome à partir d'elle-même et de la nouvelle observation.

Dans le cas de référence étudié sur un cycle de longueur première `p`, avec sortie binaire non constante, deux catégories peuvent suffire à déterminer la loi d'une seule sortie, alors que toute description non constante admettant une mise à jour déterministe exacte doit avoir `p` catégories. L'écart entre coût de prédiction ponctuelle et coût d'autonomie peut donc croître sans borne avec `p`.

## À réutiliser pour
- distinguer **compression suffisante pour une tâche** et **état fermé sous mise à jour** ;
- tester si une « réparation » est réellement nécessaire ;
- éviter d'interpréter la perte d'autonomie comme une perte immédiate de précision prédictive ;
- définir séparément coût de représentation, coût de mise à jour et accès au micro-état.

## Hypothèses / limites
- le résultat quantitatif `2` versus `p` appartient au modèle de cycle premier spécifié dans la source ;
- il ne constitue pas une revendication de nouveauté scientifique générale ;
- il ne dit rien, à lui seul, sur une réalisation physique ou quantique.

## Source principale
`/Recherche/03_AUDITS_CERTIFICATS/descriptions_audit_2026-10-14.md`

## Relation conceptuelle
`BR-STATE-01` fournit le cadre général de fermeture/réparation. Cette relation est **conceptuelle et non causale** : la preuve quantitative `2` versus `p` de cette brique est autonome et ne doit pas être invalidée automatiquement si une autre composante de `BR-STATE-01` est révisée.

## Dernier audit
`/Recherche/03_AUDITS_CERTIFICATS/BR-DESC-01_AUDIT_2026-10-14.md`