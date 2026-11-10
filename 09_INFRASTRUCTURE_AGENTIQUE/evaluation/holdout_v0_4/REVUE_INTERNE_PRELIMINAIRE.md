# P5 v0.4 — revue interne préliminaire

**Date :** 2026-11-10  
**Branche :** `audit/p5-v0-4-candidate-2026-11-10`  
**Périmètre :** reconstruction indépendante des résultats mathématiques et examen adversarial des cinq énoncés publics.  
**Statut :** REVUE INTERNE PRÉLIMINAIRE — PAS UNE REVUE HUMAINE INDÉPENDANTE — PAS DE GEL — PILOTE NON AUTORISÉ.

## 1. Limite de la revue

Cette revue a été réalisée par le même assistant qui a participé à la préparation de v0.4. Elle ne satisfait donc pas l'exigence d'un évaluateur humain indépendant n'ayant pas participé à la rédaction. Elle fournit un contrôle supplémentaire, pas une certification externe.

Les énoncés étant déjà publics sur une branche publique, aucune propriété de secret ou d'aveuglement ne peut être restaurée par cette revue.

## 2. Reconstruction des résultats

### FORMAL

De la surjectivité de f∘g vers C, on déduit que pour tout c∈C il existe a∈A tel que f(g(a))=c. En posant b=g(a), on obtient f(b)=c : f est donc surjective.

Contre-modèle commun aux deux propriétés non forcées :
- g(u)=p et g(v)=q ;
- f(p)=0, f(q)=1 et f(r)=0.

Alors f∘g prend 0 et 1, g n'atteint pas r, et f(p)=f(r) malgré p≠r. Les trois conclusions du corrigé de conception sont correctes.

### COMPUTE

Reconstruction sans reprendre la chaîne de calcul du rapport :
- De x≡7 (mod 10), écrire x=7+10k.
- La condition modulo 9 donne 7+k≡4 (mod 9), donc k≡6 (mod 9).
- Écrire k=6+9t, donc x=67+90t.
- Modulo 11, 67+90t≡1+2t≡3, donc t≡1 (mod 11).
- Ainsi x=157+990n, n∈ℤ.

Contrôle direct : 157 mod 9 = 4 ; 157 mod 10 = 7 ; 157 mod 11 = 3. Les modules sont deux à deux premiers entre eux, donc la classe est unique modulo 9×10×11=990.

**Résultat : CALCUL EXACT.**

### DOC

Le cas est techniquement pertinent et distinct des cas de calcul/fonctions. Le corrigé de conception identifie correctement :
- l'insensibilité à la casse des chiffres hexadécimaux d'un triplet percent-encoded ;
- la normalisation par décodage des caractères non réservés ;
- le risque de changer la structure/interprétation en décodant génériquement un caractère réservé tel que `/`.

Point d'attention de conception : l'énoncé cite explicitement §2.1 et §6.2.2.2, mais une réponse robuste sur le caractère réservé doit aussi mobiliser §2.2 (et §2.3 pour la catégorie unreserved). L'énoncé demande bien de citer les sections pertinentes ; ce n'est donc pas une erreur de fond, mais l'évaluateur devra vérifier que le candidat retrouve ces sections au lieu de simplement répéter les deux références données.

### EXPL

Recalcul des taux :
- Hôpital 1 : A=9/10=90 % ; B=80/100=80 %.
- Hôpital 2 : A=1/100=1 % ; B=0/10=0 %.
- Agrégé A=10/110=1/11≈9,09 %.
- Agrégé B=80/110=8/11≈72,73 %.

Le renversement est réel. Il résulte ici des poids très différents des deux établissements dans les groupes A et B. Les seules fréquences fournies ne permettent pas d'identifier un effet causal : elles ne donnent ni mécanisme d'affectation, ni ajustement sur la gravité, ni contrôle des facteurs de confusion.

**Résultat : CALCUL EXACT pour les taux ; interprétation causale correctement limitée.**

### ADV

La liste (0,2) a pour moyenne 1 et aucun terme égal à 1. C'est minimal : une liste non vide de longueur 1 a nécessairement son unique terme égal à sa moyenne. La propriété de remplacement min(x_i)≤m≤max(x_i) est vraie pour toute liste réelle finie non vide.

**Résultat : CONTRE-EXEMPLE EXACT / MINIMAL.**

## 3. Examen adversarial et limites de conception

1. **Dépendance résiduelle à v0.3.** Les énoncés FORMAL et DOC de v0.4 sont repris textuellement de v0.3. C'est cohérent avec la décision de les conserver, mais ce ne sont pas de nouveaux items. Toute revendication d'indépendance doit donc se limiter à l'éloignement thématique vis-à-vis de v0.1 déjà examiné dans l'audit précédent ; elle ne doit pas être décrite comme une indépendance nouvellement démontrée.
2. **DOC : référence normative incomplète dans l'amorce.** Voir le point d'attention ci-dessus. Le barème devra exiger la distinction entre règle RFC et comportement d'implémentation.
3. **EXPL : éviter une conclusion causale.** Le barème doit pénaliser explicitement l'affirmation que A ou B est causalement supérieur sur la seule base de ces agrégats.
4. **ADV : préciser la convention de longueur.** Le prompt dit « finite nonempty list » et demande la plus petite longueur ; la convention est suffisamment claire, mais le barème doit accepter toute liste de deux réels distincts dont la moyenne n'est aucun des deux, pas uniquement (0,2).
5. **Calibration absente.** Aucun barème détaillé, seuil de réussite, niveau de difficulté étalonné, procédure d'annotation, test de fidélité inter-évaluateurs ou budget n'est inclus ici. La correction des réponses de référence ne suffit pas à démontrer que le protocole P5 est prêt.
6. **Aucun test de modèle.** Aucun modèle A/B/C n'a été interrogé ; aucun échantillon de réponses n'a été noté. Aucune performance comparative ne peut être inférée.

## 4. Verdict

- FORMAL : **CORRECT — repris de v0.3**.
- COMPUTE : **CALCUL EXACT**.
- DOC : **FOND CORRECT — barème à expliciter sur §2.2/§2.3**.
- EXPL : **CALCUL EXACT — prudence causale nécessaire**.
- ADV : **RÉFUTATION EXACTE ET MINIMALE**.
- Indépendance anti-fuite : **NON CERTIFIÉE**.
- Revue externe indépendante : **NON EFFECTUÉE**.
- Holdout secret / aveugle : **NON CERTIFIABLE**.
- Gel du corrigé : **NON EFFECTUÉ**.
- Pilote A/B/C : **NON AUTORISÉ**.

## 5. Étape nécessaire avant tout gel

Faire relire séparément les cinq énoncés et un corrigé complet par un évaluateur humain qui n'a pas participé à leur rédaction. Obtenir ses objections et décisions de correction, puis produire le barème, les seuils, le protocole d'annotation et le nouveau jeu privé non exposé. Les empreintes ne devront être calculées qu'après ces corrections et le gel effectif des fichiers privés.
