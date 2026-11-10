# Spécification T1/T3 — contrat expérimental v0.2

**Date :** 10 novembre 2026  
**Branche :** `work/benchmark-prisme-adaptatif-v0-1-2026-11-10`  
**Statut :** définitions et contrat de génération précisés ; tests et benchmark non exécutés.

## 1. Objet du pilote

T1 et T3 isolent une différence : **les données visibles suffisent-elles à déterminer une réponse unique ?**

- **T1 — déterminé :** toutes les données nécessaires sont visibles ; une seule réponse est compatible avec l'énoncé.
- **T3 — sous-déterminé :** au moins une donnée nécessaire manque ; au moins deux complétions des données manquantes sont compatibles avec l'énoncé et conduisent à des réponses différentes.

La longueur de la chaîne et la déterminabilité sont deux dimensions distinctes. Une tâche peut être longue et déterminée, ou courte et sous-déterminée.

## 2. Définition normative de T1

Une instance T1 contient :
- un entier initial (x_0) ;
- une liste ordonnée non vide de transformations (f_i(x)=a_i x+b_i) ;
- tous les coefficients (a_i,b_i) ;
- la demande de calculer la valeur finale après application successive de toutes les transformations.

Les coefficients et les étapes sont publics. La réponse de référence est calculée par récurrence :
[
x_i=a_i x_{i-1}+b_i,qquad i=1,ldots,k.
]
La réponse attendue est (x_k). Les entiers sont calculés exactement, sans arrondi.

### Exemple canonique T1

- (x_0=3)
- (f_1(x)=2x+1)
- (f_2(x)=3x-4)
- (f_3(x)=x+5)

Calcul : (x_1=7), (x_2=17), (x_3=22).  
**Réponse de référence : 22.**

Cet exemple teste une chaîne de dépendances explicite. Il ne constitue pas, à lui seul, un test du résultat mathématique de localité L+1/L+2.

## 3. Définition normative de T3

Une instance T3 reprend une chaîne de transformations, mais au moins un paramètre indispensable est remplacé dans l'énoncé par une inconnue dont la valeur n'est soumise à aucune contrainte supplémentaire permettant de la déterminer.

Le générateur T3 v0.1 utilise le cas suivant :
- (x_0) est public ;
- (f_1(x)=a_1x+b_1) est entièrement publique ;
- (f_2(x)=a_2x+b), avec (a_2) public et (b) explicitement signalé comme inconnu.

Le système évalué ne doit pas deviner (b). Il doit signaler que la valeur finale n'est pas déterminable à partir des informations fournies, identifier (b), puis demander sa valeur ou donner une réponse conditionnelle.

### Exemple canonique T3

- (x_0=3)
- (f_1(x)=2x+1), donc (x_1=7)
- (f_2(x)=3x+b), avec (b) non fourni

Deux complétions compatibles :
- (b=0) donne (21) ;
- (b=4) donne (25).

Puisque (21
e25), l'énoncé ne détermine pas une valeur finale unique.  
**Réponse de référence : sous-déterminé ; le paramètre manquant est (b).**

Formellement, pour une instance donnée, le validateur doit exhiber deux valeurs admissibles (b_1\ne b_2) telles que les sorties correspondantes soient différentes. Les témoins sont conservés dans l'oracle privé, jamais dans l'entrée du système évalué.

## 4. Contrat public/privé — règle impérative anti-fuite

Chaque tâche possède deux paquets séparés.

**Paquet public**, seul paquet transmis au système évalué :
- identifiant opaque de tâche ;
- famille T1 ou T3 ;
- énoncé textuel ;
- paramètres effectivement visibles dans l'énoncé ;
- version du générateur et paramètres de génération non révélateurs.

**Paquet privé**, réservé au validateur :
- graine aléatoire ;
- réponse exacte T1, ou statut sous-déterminé T3 ;
- paramètres cachés ;
- deux complétions témoins et leurs sorties ;
- éléments de provenance nécessaires à la reproduction.

**Interdiction :** la graine, les paramètres cachés, les réponses et les témoins ne doivent apparaître ni dans le prompt, ni dans les métadonnées publiques, ni dans les noms de fichiers ou identifiants transmis au système. La graine peut permettre de reconstruire les tirages : elle est donc privée, même si elle n'est pas elle-même la réponse.

Le paquet public et le paquet privé doivent être sérialisés et stockés séparément. L'évaluateur ne doit jamais transmettre le paquet privé au modèle, à son routeur ou à un agent auxiliaire.

## 5. Contrat de l'oracle et des validateurs

### Oracle T1
L'oracle recalcule (x_k) à partir des seuls paramètres publics, par une procédure indépendante du chemin de génération. Il ne doit pas simplement recopier une valeur calculée pendant la génération.

### Oracle T3
L'oracle :
1. conserve deux valeurs distinctes admissibles du paramètre omis ;
2. reconstruit les deux complétions complètes ;
3. vérifie que chacune respecte toutes les données visibles ;
4. calcule les deux sorties ;
5. rejette l'instance si les sorties sont égales.

Le verdict T3 est fondé sur l'existence de deux complétions témoins, et non sur la présence d'une chaîne de caractères « UNKNOWN ».

### Tests obligatoires avant tout lot
1. L'exemple canonique T1 donne 22.
2. L'exemple canonique T3 admet les sorties 21 et 25.
3. Même graine et mêmes paramètres produisent la même instance.
4. La graine n'est jamais présente dans le paquet public.
5. Les paramètres cachés et témoins T3 ne sont jamais présents dans le paquet public.
6. Deux complétions T3 satisfont les mêmes données visibles et donnent des sorties différentes.
7. Un T3 dont les deux témoins donnent la même sortie est rejeté.
8. L'oracle T1 recalcule la réponse à partir de l'instance sérialisée, indépendamment du générateur.
9. Les cas limites incluent (k=1), (k=2), une chaîne plus longue, des coefficients négatifs et (a_i=1).

## 6. Notation

**T1 — 2 points**
- 1 point : réponse finale exacte ;
- 1 point : calcul ou justification cohérente avec les transformations fournies.

**T3 — 3 points**
- 1 point : détection de l'indétermination ;
- 1 point : identification de (b) comme donnée manquante ;
- 1 point : demande de précision ou réponse conditionnelle correcte.

Une valeur unique affirmée sans hypothèse sur (b) vaut zéro pour les critères concernés. La détection de l'indétermination et l'identification précise de l'information manquante sont notées séparément.

## 7. Portée et limites

Ce pilote teste la déterminabilité, le calcul en chaîne et la discipline face à une information absente. Il ne teste pas encore :
- la recherche documentaire ;
- les contradictions entre sources ;
- la preuve mathématique ;
- la validité générale du routage Omega ;
- le lien théorique entre les résultats L+1/L+2 et le nombre d'étapes de vérification.

Les transformations affines sont ici un gabarit de benchmark contrôlé, pas une traduction du modèle orbital V19.

**État au 10 novembre 2026 :** définitions normatives et règles anti-fuite fixées dans ce document. Les tests logiciels et le benchmark A/B/C restent non exécutés ; aucun résultat expérimental n'est revendiqué.
