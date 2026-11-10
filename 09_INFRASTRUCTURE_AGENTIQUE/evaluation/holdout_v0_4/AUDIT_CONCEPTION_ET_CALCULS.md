# P5 v0.4 — audit de conception et de calcul

**Date :** 2026-11-10  
**Branche :** `audit/p5-v0-4-candidate-2026-11-10`  
**Statut :** CANDIDAT PUBLIC / NON GELÉ / NON UTILISABLE COMME HOLDOUT AVEUGLE.

## 1. Périmètre et provenance

v0.4 est créé comme nouvelle version, sans écraser v0.1, v0.2 ou v0.3. Les cas FORMAL et DOC sont conservés conformément à la décision précédente. COMPUTE, EXPL et ADV sont remplacés par trois familles distinctes : congruences chinoises, paradoxe de Simpson, et propriété de la moyenne arithmétique.

La création de cette branche et la publication des énoncés rendent cependant v0.4 visible dans le dépôt public. **Cette version ne peut donc pas être qualifiée de holdout secret ni être utilisée pour un test aveugle contre un système susceptible d'avoir accès au dépôt.** Il s'agit d'un candidat de conception et de validation seulement. Un véritable holdout devra être créé et distribué dans un espace privé, avec accès contrôlé.

## 2. Vérification des nouveaux cas

### COMPUTE — système de congruences

Les congruences sont :
- x ≡ 4 (mod 9)
- x ≡ 7 (mod 10)
- x ≡ 3 (mod 11)

Les modules sont deux à deux premiers entre eux ; leur produit vaut 990. En posant x = 7 + 10k, la première congruence donne k ≡ 6 (mod 9), donc x = 67 + 90t. La troisième donne 1 + 2t ≡ 3 (mod 11), donc t ≡ 1 (mod 11).

La classe de solutions est donc **x ≡ 157 (mod 990)**. Vérification directe : 157 = 9×17+4 = 10×15+7 = 11×14+3. L'unicité modulo 990 découle du théorème chinois des restes.

### EXPL — renversement de Simpson

Taux par établissement :
- Hôpital 1 : A = 9/10 = 90 % ; B = 80/100 = 80 %.
- Hôpital 2 : A = 1/100 = 1 % ; B = 0/10 = 0 %.

Taux agrégés :
- A = (9+1)/(10+100) = 10/110 = 1/11 ≈ 9,09 %.
- B = (80+0)/(100+10) = 80/110 = 8/11 ≈ 72,73 %.

A est supérieur dans chaque strate, tandis que B est très supérieur après agrégation. Le renversement est dû aux répartitions très différentes des patients entre établissements. Ces données descriptives seules ne démontrent pas un effet causal : elles ne contrôlent pas les facteurs de sélection, la gravité initiale ni les autres variables confondantes.

### ADV — moyenne arithmétique

L'affirmation est fausse. Contre-exemple minimal : la liste (0,2), de moyenne 1, dont aucun élément n'est égal à 1. Une liste de longueur 1 a nécessairement son unique élément égal à sa moyenne ; aucune liste plus courte non vide ne peut donc réfuter l'affirmation.

Propriété correcte : pour toute liste réelle finie non vide, min(x_i) ≤ m ≤ max(x_i). En particulier, au moins un élément est inférieur ou égal à m et au moins un élément est supérieur ou égal à m.

## 3. Cas conservés

FORMAL : si f∘g est surjective sur C, alors f est surjective sur C. Avec g(u)=p, g(v)=q, f(p)=0, f(q)=1, f(r)=0, la composée est surjective, g n'est pas surjective et f n'est pas injective. Ce modèle réfute les deux propriétés non forcées.

DOC : l'audit du texte primaire RFC 3986 confirme que la casse des chiffres hexadécimaux dans un triplet percent-encoded est indifférente (§2.1 et §6.2.2.1) ; la normalisation par décodage vise les caractères non réservés (§6.2.2.2, avec §2.3) ; le slash est réservé (§2.2), donc %2F ne doit pas être décodé en / de manière générique, car cela peut modifier la structure du URI. Source primaire : https://www.rfc-editor.org/rfc/rfc3986.html.

## 4. Audit de proximité et limites

- Par rapport à v0.1, les trois nouveaux cas évitent les thèmes des fonctions finies, des trajectoires observées et de l'injectivité/surjectivité.
- FORMAL et DOC demeurent les deux cas précédemment jugés suffisamment distincts sur le plan conceptuel par l'audit v0.3/v0.1.
- La proximité conceptuelle n'est pas une preuve d'absence de fuite.
- Tous les énoncés v0.4 sont publiés sur une branche publique. L'indépendance comme holdout aveugle est donc **NON CERTIFIABLE**.
- Aucun corrigé privé v0.4 n'est déposé dans le dépôt. Aucun digest de corrigé n'est revendiqué.
- Aucun modèle A/B/C, évaluateur ou budget n'a été engagé ; aucune génération ni notation n'a été exécutée.

## 5. Décision

**G4 : BLOQUÉE pour un usage aveugle.** La conception des exercices et les calculs de contrôle sont prêts pour revue, mais l'exposition publique interdit de présenter ce jeu comme secret. G5–G10 restent à renseigner et à vérifier. Aucun pilote A/B/C n'est autorisé.

Prochaine étape nécessaire : faire relire les énoncés et corrigés par une personne indépendante, puis créer un nouveau jeu privé non exposé (nouveaux identifiants et énoncés, corrigé privé, accès journalisé et empreintes recalculées sur les fichiers réellement gelés).