# Pilote bibliothèque V19

Point d'entrée facultatif pour un cycle local, depuis la racine d'un clone complet d'Omega-pub.

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/v19_library/run.py --output /tmp/omega-v19-cycle.json
```

Utiliser un nouveau chemin par exécution. Les commits des PR #2, #5 et #18 doivent être présents dans le clone. Si une source manque, le pilote échoue avant d'émettre un verdict. L'inventaire de la PR #5 référence l'index et la fiche reconstituée de la PR #2. Le manifeste fixe explicitement les liens vers l'audit et le test de la PR #18. Le journal produit contient les chemins, commits et SHA-256. Les sources privées citées dans la fiche sont des références historiques.

## Exécution du pilote

Le fichier [result.json](result.json) conserve la sortie du script d'origine et le résultat de la projection par un second calcul. Les deux parcours partagent l'énumération des cycles. Le second reconstruit les contraintes et utilise l'union-find à parité sur **toutes** les composantes. Les 325 468 comparaisons global/local concordent dans le domaine testé. Le journal contient aussi un écart de sémantique du script historique.

Pour T = (0,0,3,4,2), B = (2,3,4), paire (0,1) et L = 2, la fusion impose c(0) ≠ c(1) et l'événement impose c(0) = c(1). L'ombre est donc vide. Le script historique renvoie les huit colorations de B car sa propagation démarre uniquement sur B. Cette contradiction est présente dans les deux graphes comparés. Elle ne fournit aucun contre-exemple à leur égalité.

## Raccord mathématique à relire

Pour comparer l'ombre globale au sous-graphe induit par les états visibles, il suffit que chaque chemin forcé entre deux ancrages (états du cycle et états touchés par les égalités de l'événement) soit visible. Les portions restantes des composantes forcées peuvent être coloriées indépendamment ou prolongées depuis leur seul point de contact. D'après la classification P1–P4 dans l'audit, les seuls sommets intérieurs d'un tel chemin appartiennent au noyau invariant. Dans le cas d'un 2-cycle tous deux sont vus au plus deux pas après une feuille ancrée, ou un pas après un sommet du noyau déjà ancré. Dans le cas de deux points fixes, chaque sommet intérieur est soit lui-même un ancrage, soit l'image d'une extrémité transitoire ancrée. Les ancrages de B ne peuvent appartenir à un noyau invariant.

Ce raisonnement vise l'égalité avec le **graphe induit construit en disposant de T**. Une suffisance à partir des seules données du préfixe demande en plus de déterminer les parités pertinentes à partir des images effectivement observées. En particulier, vérifier le noyau du 2-cycle lorsque le second sommet apparaît exactement au dernier temps visible et que son successeur n'est pas fourni. Cette étape et la conformité à la définition primaire de V19 restent à relire. Le statut général du pilote est indéterminé. Les statuts archivés restent inchangés.

## Vérification suivante — données observées jusqu'à L+1

[Le nouveau calcul](prefix.py) reçoit seulement le cycle ordonné et les deux
trajectoires jusqu'au temps L+1 pour calculer son résultat local. Il construit
les arêtes forcées uniquement lorsque les deux images sont connues. Le calcul
global reçoit séparément T complète. [Résultat du rejeu](prefix-result.json) :
325 468 accords sur N ≤ 6 et L = 2 ou 3. Rejeu depuis le dossier du prisme :

```sh
python3 -m v19_library.prefix --output /tmp/omega-v19-prefix.json
```

### Preuve dans le modèle binaire de contraintes du pilote

Soit un ancrage tout sommet du cycle distingué B ou des deux trajectoires aux
temps 0,…,L−1. Toute égalité de l'événement touche des ancrages. Les contraintes
forcées sont des inégalités binaires. Sous leur cohérence, les arêtes de fusion
M forment un appariement (une fibre de taille trois donnerait un triangle).
Les arêtes invariantes I forment aussi un appariement : elles relient les
partenaires d'un 2-cycle ou les deux points fixes, et trois points fixes sont
exclus par cohérence. Une arête M ne peut lier deux périodiques, puisque T est
injective sur ce sous-ensemble. Les composantes sont donc des chemins : au
plus une arête M de chaque côté d'une arête I, ou une arête M isolée.

Chaque ancrage de trajectoire livre ses deux transitions suivantes et chaque
ancrage de B livre ses transitions cycliques. Considérons un chemin forcé
entre deux ancrages :

- Une seule arête est directement lisible par les images des deux ancrages.
- Un chemin de longueur au moins deux comporte I. Si un bout est un sommet
  invariant ancré, ses deux transitions révèlent le 2-cycle complet. Pour deux
  points fixes, l'autre sommet est ancré ou son caractère fixe est observé
  via les deux transitions depuis la feuille ancrée qui s'y attache.
- Si les deux bouts sont des feuilles, dans le cas du 2-cycle leurs images
  sont les deux sommets du noyau, dans l'ordre opposé à leurs attaches M.
  Chacune des deux feuilles montre donc une transition du 2-cycle. Dans le
  cas de deux points fixes, chacune montre une boucle du noyau.

Toutes les arêtes de ces chemins sont donc déduites à partir des transitions
lues, même quand la trajectoire d'une seule feuille finit sur le second sommet
du noyau. Les chemins capturent toutes les relations de parité imposées entre
ancrages. Une coloration satisfaisant ces relations s'étend à chaque composante
forcée par cohérence, indépendamment des autres. Cette extension conserve
toutes les égalités de l'événement et la coloration de B. Réciproquement,
une solution globale satisfait les contraintes lues. Ainsi le calcul local
donne exactement l'ombre globale pour tout horizon L ≥ 2 dans ce modèle.

### Borne inférieure uniforme

Pour L = 2, prendre B = (3,4,5) et les trajectoires issues de 2 et 3.
Les applications T = (1,0,0,4,5,3) et T' = (1,1,0,4,5,3) ont les mêmes
préfixes jusqu'au temps L, (2,0,1) et (3,4,5), et des contraintes forcées
cohérentes. Sous T, M lie 2 et 1, et I lie 1 et 0. Par conséquent 2 et 0
ont la même couleur, donc 3 et 4 aussi. Sous T', seule M lie 0 et 1,
ce qui n'impose aucune relation supplémentaire entre 3 et 4. Les ombres
comptent respectivement quatre et huit colorations. Le temps L ne suffit
donc pas uniformément dans ce modèle.

Le [document primaire V19](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/02_MATHEMATIQUES/defauts_recollement/sources/V19/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE_2.md) utilise le même critère de contrainte forcée (section 2), les mêmes hypothèses et les mêmes égalités d’événement (section 4). Une relecture indépendante de cette preuve reste à effectuer avant toute promotion du statut historique.
