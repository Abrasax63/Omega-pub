# BR-DESC-02 — Bonne marginale, mauvais ordre temporel

**Statut : CALCUL EXACT pour l'identité de covariance ; garantie exacte de fausse alerte pour la machine rationnelle spécifiée ; puissance et délais évalués par simulation.**

## Énoncé réutilisable
Deux descriptions peuvent produire exactement la même fréquence marginale d'observation tout en différant dans leurs dépendances temporelles. Une validation fondée uniquement sur les fréquences peut donc accepter une description qui représente mal l'ordre des événements.

Dans le modèle à cinq phases étudié, tous les noyaux considérés préservent la distribution uniforme et donnent
`P(Y_t=1)=21/50=0,42`, tandis que
`Cov(Y_t,Y_{t+2}) = -(64/625)(1-λ)^2`.
La marginale ne sépare donc pas le régime de référence d'un régime devenu indépendant, alors que la corrélation à retard 2 le fait.

## Détecteur
Pour la machine rationnelle spécifiée, la construction par supermartingale donne sous le modèle nul exact :
`P_0(au moins une fausse alerte, à un instant quelconque) <= 1 %`.

Les taux de détection et délais rapportés dans la source sont **simulés**. Ils ne constituent pas une garantie générale de puissance ni de délai.

## À réutiliser pour
- auditer une description au-delà de ses statistiques à un temps ;
- construire des tests de changement de dynamique lorsque les marginales sont invariantes ;
- distinguer **prédiction de fréquence** et **représentation de la structure temporelle** ;
- chercher le plus petit observable relationnel qui falsifie une description.

## Hypothèses / limites
- les formules sont propres au modèle spécifié dans la source ;
- le contrôle exact de fausse alerte suppose le modèle nul déclaré et l'arithmétique rationnelle/arrondie de la construction ;
- les performances de détection sont simulées ; aucun théorème général de délai n'est revendiqué ;
- les outils de détection sont connus (filtrage HMM, quantification de croyance, mélange prédictif, supermartingale de test).

## Source principale
`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md`

## Relation conceptuelle
`BR-DESC-02 ILLUSTRE BR-DESC-01`.

Cette relation est **conceptuelle et non causale** : la preuve de covariance et la validité du détecteur ne dépendent pas de `BR-DESC-01`.

## Dernier audit
`/Recherche/03_AUDITS_CERTIFICATS/BR-DESC-02_AUDIT_2026-10-14.md`