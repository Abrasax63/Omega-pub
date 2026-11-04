# V19 — Audit d’assemblage, orientation et petit modèle de coexistence
Date : 15 octobre 2026

## Statut général
Travail interne RAVI-2. Aucun résultat de ce rapport ne constitue une validation externe ni une revendication de nouveauté bibliographique. Les calculs ci-dessous sont exacts en arithmétique binaire ; le théorème de petit modèle est accompagné d’une preuve directe.

## A. Reproduction indépendante de la classification locale
La génération a été reconstruite sans réutiliser les anciens fichiers CSV :
- cycle fixé `T(c_i)=c_(i+1 mod 5)`;
- deux trajectoires non diagonales jusqu’au temps 5;
- nouveaux états introduits canoniquement;
- congruence fonctionnelle `a=b => T(a)=T(b)`;
- contraintes forcées exactes `Tu=Tv` ou `{Tu,Tv}={u,v}`;
- trois égalités du mauvais événement à L=3;
- projection par parités sur C5.

Résultat exact :
- 3 341 diagrammes locaux non diagonaux;
- 13 classes propres modulo D5;
- répartition par codimension 1/2/3 : 4 / 5 / 4.

Cela reproduit exactement la carte `OBS-V19-C5-13` et lève la réserve antérieure « énumération complète non relancée ».

## B. Raffinement orienté : 14 classes modulo C5
Pour un même opérateur T, le cycle distingué est orienté : `T(c_i)=c_(i+1)`.
Les rotations sont des automorphismes du cycle orienté, mais une réflexion conjugue T à T^(-1) et ne doit pas être appliquée indépendamment à chaque ombre lors d’un problème de coexistence.

En quotientant seulement par rotations C5 :
- 14 classes propres;
- répartition codimension 1/2/3 : 4 / 6 / 4.

Douze classes D5 restent une seule classe C5 ; une unique classe D5 de codimension 2 se scinde en deux classes chirales.
Une paire canonique de représentants de cette scission est :
- `x0+x2=1; x0+x1=1`
- `x0+x4=1; x0+x3=1`
Ces deux systèmes sont images l’un de l’autre par réflexion, mais pas par rotation.

Conséquence méthodologique : `13 D5` reste correct pour la classification d’une ombre isolée ; pour la coexistence dans un même T, l’alphabet minimal à tester est au moins le raffinement orienté `14 C5`.

## C. Compatibilité par paires
Pour chacune des 105 paires non ordonnées avec répétition des 14 classes orientées, un endofonction complète cohérente et deux paires d’états ont été construites puis revérifiées par projection exacte.
- 105/105 compatibles;
- taille maximale des témoins produits : 17 états.

Donc le graphe de compatibilité pair-à-pair des 14 classes orientées est complet.
Aucune obstruction de coexistence ne peut être expliquée par l’interdiction d’un simple couple de classes orientées.

## D. Compatibilité de triples au quotient D5
Pour les 13 classes D5, les 455 multisets de trois classes ont chacun un témoin complet :
- 445 par union disjointe de témoins sans point fixe externe et à ports d’entrée disjoints;
- 10 cas résiduels par partage explicite de queues / registre fixe.
Les 455 certificats sont fournis séparément.

Interprétation : au niveau grossier des 13 classes D5, les obstructions responsables des gaps ne sont ni binaires ni ternaires. Cependant ce résultat ne remplace pas l’analyse orientée : le quotient D5 peut masquer l’information chirale.

## E. Théorème de petit modèle pour k ombres
### Énoncé
Soit une endofonction finie T avec cycle distingué C_q, q>=3, observation binaire, horizon L>=2, et contraintes forcées cohérentes. Considérons k paires dont on veut conserver simultanément les k ombres sur C_q.

Si ces k ombres coexistent dans un système fini quelconque, elles coexistent dans un système fini de taille au plus

`N <= q + 2 k (L+3) + max(3, 2k)`.

### Preuve
Pour chaque paire j, `OBS-V19-LOCAL-L2` implique que son ombre dépend seulement de C_q et des deux préfixes de trajectoire aux temps 0..L+2.
Prendre l’union U de ces k petits modèles. Alors
`|U| <= q + 2 k (L+3)`.

La restriction de T à U est une fonction partielle. Les seuls états dont l’image peut rester indéfinie sont les états terminaux au temps L+2 ; il y en a au plus 2k.
Soit r leur nombre. Ajouter un cycle externe D de longueur `m=max(3,r)` et envoyer injectivement chaque terminal indéfini vers un sommet distinct de D.

Cette complétion :
1. ne modifie aucun préfixe jusqu’au temps L+2, donc ne modifie aucune des k ombres par le théorème de localité;
2. n’introduit aucun point fixe ni 2-cycle dans D;
3. crée au plus une nouvelle arête de fusion par terminal, entre ce terminal et le prédécesseur cyclique du sommet de D visé;
4. conserve donc la cohérence des contraintes forcées.

On obtient une endofonction totale de taille au plus la borne annoncée.

### Corollaire
Pour q,L,k fixés, la question « ces k ombres peuvent-elles coexister ? » possède une propriété de petit modèle indépendante de la taille ambiante et est décidable par recherche finie.

## F. Tests adversariaux
En plus de la preuve :
- compression/complétion testée sur 1 347 familles de 2 ou 3 paires provenant de tous les systèmes cohérents avec C5 jusqu’à N=8 : 0 divergence;
- reproduction indépendante 3 341 -> 13 D5 -> 14 C5 : PASS;
- 105 témoins de paires orientées revérifiés exactement;
- 455 témoins de triples D5 revérifiés exactement.

## G. Littérature ciblée
Connu : weighted pair graphs / observability graphs et réduction à des automates finis pour les Boolean control networks (Zhang & Zhang, IEEE TAC 2016 ; survey Zhang 2023).
Connu dans un autre contexte : théorèmes de petit modèle pour le contrôle par bisimulation sous observation partielle (Zhou & Kumar, IEEE TASE 2007).
Non retrouvé tel quel dans la recherche ciblée : la borne de petit modèle ci-dessus pour la coexistence de plusieurs ombres locales d’une endofonction, ni le raffinement 13 D5 -> 14 C5 pour conserver l’orientation dans l’assemblage.
Originalité : INDÉTERMINÉE.

## H. Prochaine expérience
Abandonner le graphe simple sur 13 classes comme objet principal.
Construire le complexe de coexistence sur :
1. les 14 classes orientées C5;
2. puis les ombres géométriques étiquetées compatibles avec une orientation de cycle;
3. enfin les circuits positifs et multiplicités.

Chercher le premier ordre k où la compatibilité orientée cesse d’être complète, ou montrer que l’obstruction dépend non des classes seules mais des copies géométriques / coefficients.