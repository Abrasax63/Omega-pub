# Reprise croisée et test borné — 20 octobre 2026

## Provenance et travaux déjà aboutis

Sources relues : RESEARCH_SNAPSHOT_ACTIVE.md v33 ; MEMORY_INDEX.md v36 (lecture partiellement tronquée dans la sortie disponible) ; RAVI2_DISCOVERY_V02_VERDICTS_2026-10-20.json ; BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md ; COMMIT_SINGLE_GAP_COMPLEXITY_2026-10-19.md ; RESEARCH_METHOD_RAVI2.md v3 ; SCIENTIFIC_COMMIT_PROTOCOL.md. Les cartes et audits Q-PRED-HIDDEN et Discovery v0.2 ont également été lus dans cette conversation.

- Mealy–V19 : transfert de bornes non trivial déjà réfuté, ne pas rouvrir sous une reformulation.
- Spectre minimal V19 : démontré mais redondant comme brique autonome.
- Temps : complexité de la famille spécialisée déjà généralisée au mot à un seul gap exceptionnel ; ne pas refaire ce résultat.
- Quantique : séparation prédictive cachée déjà enregistrée ; dimension produit d, saturation corrélée d² dans le modèle déclaré ; cardinal brut inadéquat.
- Schrödinger : résultats de fermeture polynomiale et de secteur sextique récupérés selon le snapshot ; aucune résolution générale attestée. Cartes détaillées non réauditées ici.

Cette reprise utilise les traces persistées des autres conversations, sans prétendre avoir accès à leur intégralité. L'absence de résultat d'une recherche Library ne prouve pas l'absence de travaux antérieurs.

## Question nouvelle bornée

Pour prolonger le cas à un seul gap exceptionnel, le multiensemble des gaps cycliques entre les 1 suffit-il à déterminer la complexité en facteurs p(L) ?

Nécessité : décider quelles données conserver avant de chercher une formule à plusieurs gaps. Discrimination : un contre-exemple exclut toutes les formules ne dépendant que des gaps triés. Testabilité : énumération finie puis reconstruction indépendante des extensions droites. Budget : deux expériences, exécutées ci-dessous.

## Résultat exact

Les mots cycliques A=1110010 et B=1101100 ont chacun période fondamentale 7 et quatre symboles 1. Leurs gaps, depuis l'origine écrite, sont respectivement (1,1,3,2) et (1,2,1,3). Ils ont donc le même multiensemble {1,1,2,3}, mais p_A(3)=7 et p_B(3)=5.

Facteurs de longueur 3 de A : {001,010,011,100,101,110,111}.
Facteurs de longueur 3 de B : {001,011,100,101,110}.

Cela réfute, par contre-exemple fini, la suffisance des gaps triés, même en fixant la période fondamentale et le nombre de 1. L'effet ne vient donc pas simplement d'une différence de période. L'exemple utilise deux gaps exceptionnels 2 et 3 autour d'un gap de base 1.

Un second couple obtenu par insertion d'un zéro après chaque symbole donne les gaps triés {2,2,4,6} : voir les données intégrales. Il élimine l'objection du gap de base égal à 1.

## Contrôles et limites

Expérience 1 : tous les mots binaires non constants primitifs de longueurs 2 à 14 ont été regroupés par gaps triés, puis comparés par énumération des facteurs. Comptages exacts ci-dessous ; mots étiquetés, sans quotient par rotation.
Expérience 2 : pour les quatre témoins, les ensembles d'extensions droites sont reconstruits séparément et vérifient p(L+1)-p(L)=nombre de facteurs spéciaux à droite pour toutes les longueurs 1≤L<T. Calcul entier sans tolérance numérique.

Statut : CALCUL EXACT / conjecture testée RÉFUTÉE. Ce n'est pas une nouvelle loi physique ni une formule générale pour plusieurs gaps. Originalité : INDÉTERMINÉE, aucune nouveauté revendiquée. Pas de promotion dans les bases scientifiques ; aucun compteur ni DEPEND_DE modifié. Le cadre des facteurs spéciaux est classique : de Luca et Mignosi, Words and special factors, Theoretical Computer Science (2001), https://www.sciencedirect.com/science/article/pii/S0304397599003345 (référence repérée par recherche, texte intégral non audité ici).

Verrou fermé : gaps triés seuls suffisants ? NON. Pour reprendre, conserver l'ordre cyclique des gaps ou un résumé démontré suffisant de leurs contextes ; ne pas prolonger le même verrou par une suite indéfinie de métriques candidates. Prochaine question possible, distincte : classification exacte des facteurs spéciaux avec exactement deux gaps exceptionnels et leur séparation fixée. Non exécutée ici.

## Données complètes

```json
{
  "status": "CALCUL EXACT; réfutation de la suffisance du multiensemble de gaps",
  "not_promoted": true,
  "total_primitive_labelled_words": 32474,
  "divergent_groups_across_lengths": 257,
  "enumeration": [
    {
      "T": 2,
      "primitive_labelled_words": 2,
      "gap_multiset_groups": 1,
      "groups_with_different_profiles": 0
    },
    {
      "T": 3,
      "primitive_labelled_words": 6,
      "gap_multiset_groups": 2,
      "groups_with_different_profiles": 0
    },
    {
      "T": 4,
      "primitive_labelled_words": 12,
      "gap_multiset_groups": 3,
      "groups_with_different_profiles": 0
    },
    {
      "T": 5,
      "primitive_labelled_words": 30,
      "gap_multiset_groups": 6,
      "groups_with_different_profiles": 0
    },
    {
      "T": 6,
      "primitive_labelled_words": 54,
      "gap_multiset_groups": 8,
      "groups_with_different_profiles": 0
    },
    {
      "T": 7,
      "primitive_labelled_words": 126,
      "gap_multiset_groups": 14,
      "groups_with_different_profiles": 2
    },
    {
      "T": 8,
      "primitive_labelled_words": 240,
      "gap_multiset_groups": 19,
      "groups_with_different_profiles": 5
    },
    {
      "T": 9,
      "primitive_labelled_words": 504,
      "gap_multiset_groups": 28,
      "groups_with_different_profiles": 10
    },
    {
      "T": 10,
      "primitive_labelled_words": 990,
      "gap_multiset_groups": 39,
      "groups_with_different_profiles": 16
    },
    {
      "T": 11,
      "primitive_labelled_words": 2046,
      "gap_multiset_groups": 55,
      "groups_with_different_profiles": 28
    },
    {
      "T": 12,
      "primitive_labelled_words": 4020,
      "gap_multiset_groups": 72,
      "groups_with_different_profiles": 43
    },
    {
      "T": 13,
      "primitive_labelled_words": 8190,
      "gap_multiset_groups": 100,
      "groups_with_different_profiles": 63
    },
    {
      "T": 14,
      "primitive_labelled_words": 16254,
      "gap_multiset_groups": 132,
      "groups_with_different_profiles": 90
    }
  ],
  "witnesses": [
    {
      "word": "1110010",
      "gaps": [
        1,
        1,
        3,
        2
      ],
      "primitive": true,
      "profile": [
        2,
        4,
        7,
        7,
        7,
        7,
        7
      ],
      "right_special": [
        {
          "L": 1,
          "right_special": [
            "0",
            "1"
          ]
        },
        {
          "L": 2,
          "right_special": [
            "01",
            "10",
            "11"
          ]
        },
        {
          "L": 3,
          "right_special": []
        },
        {
          "L": 4,
          "right_special": []
        },
        {
          "L": 5,
          "right_special": []
        },
        {
          "L": 6,
          "right_special": []
        }
      ]
    },
    {
      "word": "1101100",
      "gaps": [
        1,
        2,
        1,
        3
      ],
      "primitive": true,
      "profile": [
        2,
        4,
        5,
        6,
        7,
        7,
        7
      ],
      "right_special": [
        {
          "L": 1,
          "right_special": [
            "0",
            "1"
          ]
        },
        {
          "L": 2,
          "right_special": [
            "10"
          ]
        },
        {
          "L": 3,
          "right_special": [
            "110"
          ]
        },
        {
          "L": 4,
          "right_special": [
            "0110"
          ]
        },
        {
          "L": 5,
          "right_special": []
        },
        {
          "L": 6,
          "right_special": []
        }
      ]
    },
    {
      "word": "10101000001000",
      "gaps": [
        2,
        2,
        6,
        4
      ],
      "primitive": true,
      "profile": [
        2,
        3,
        5,
        7,
        11,
        14,
        14,
        14,
        14,
        14,
        14,
        14,
        14,
        14
      ],
      "right_special": [
        {
          "L": 1,
          "right_special": [
            "0"
          ]
        },
        {
          "L": 2,
          "right_special": [
            "00",
            "10"
          ]
        },
        {
          "L": 3,
          "right_special": [
            "000",
            "010"
          ]
        },
        {
          "L": 4,
          "right_special": [
            "0000",
            "0010",
            "1000",
            "1010"
          ]
        },
        {
          "L": 5,
          "right_special": [
            "00010",
            "01000",
            "01010"
          ]
        },
        {
          "L": 6,
          "right_special": []
        },
        {
          "L": 7,
          "right_special": []
        },
        {
          "L": 8,
          "right_special": []
        },
        {
          "L": 9,
          "right_special": []
        },
        {
          "L": 10,
          "right_special": []
        },
        {
          "L": 11,
          "right_special": []
        },
        {
          "L": 12,
          "right_special": []
        },
        {
          "L": 13,
          "right_special": []
        }
      ]
    },
    {
      "word": "10100010100000",
      "gaps": [
        2,
        4,
        2,
        6
      ],
      "primitive": true,
      "profile": [
        2,
        3,
        5,
        7,
        9,
        10,
        11,
        12,
        13,
        14,
        14,
        14,
        14,
        14
      ],
      "right_special": [
        {
          "L": 1,
          "right_special": [
            "0"
          ]
        },
        {
          "L": 2,
          "right_special": [
            "00",
            "10"
          ]
        },
        {
          "L": 3,
          "right_special": [
            "000",
            "010"
          ]
        },
        {
          "L": 4,
          "right_special": [
            "0000",
            "1000"
          ]
        },
        {
          "L": 5,
          "right_special": [
            "01000"
          ]
        },
        {
          "L": 6,
          "right_special": [
            "101000"
          ]
        },
        {
          "L": 7,
          "right_special": [
            "0101000"
          ]
        },
        {
          "L": 8,
          "right_special": [
            "00101000"
          ]
        },
        {
          "L": 9,
          "right_special": [
            "000101000"
          ]
        },
        {
          "L": 10,
          "right_special": []
        },
        {
          "L": 11,
          "right_special": []
        },
        {
          "L": 12,
          "right_special": []
        },
        {
          "L": 13,
          "right_special": []
        }
      ]
    }
  ]
}
```

## Code minimal de reproduction des témoins

```python
from collections import defaultdict
for w in ["1110010", "1101100", "10101000001000", "10100010100000"]:
    n=len(w)
    positions=[i for i,c in enumerate(w) if c=="1"]
    gaps=[b-a for a,b in zip(positions,positions[1:])]+[n+positions[0]-positions[-1]]
    p=[len({"".join(w[(i+j)%n] for j in range(L)) for i in range(n)}) for L in range(1,n+1)]
    assert all(w!=w[:d]*(n//d) for d in range(1,n) if n%d==0)
    for L in range(1,n):
        extensions=defaultdict(set)
        for i in range(n):
            extensions["".join(w[(i+j)%n] for j in range(L))].add(w[(i+L)%n])
        assert p[L]-p[L-1]==sum(len(v)==2 for v in extensions.values())
    print(w, gaps, p)
```


# Développement 2 — deux gaps exceptionnels identiques

## Domaine et formule candidate

Soient g≥1, δ≥1 et 1≤a<b. Posons P=10^{g−1}, W=P^a 0^δ P^b 0^δ et T=(a+b)g+2δ. Les gaps sont tous g sauf deux gaps g+δ. Les séparations entre défauts sont décrites par a et b.

Pour 1≤L≤T, la formule **candidate**, non promue, est :

p(L)=2+min(L−1,g+δ−2)+min(max(L−g,0),(b−1)g)+min(max(L−(a+1)g,0),ag+δ).

Le terme final dépend de la séparation. La formule générale n'est pas certifiée par le seul succès des tests ci-dessous.

## Classification candidate des facteurs spéciaux

Soit B_L le suffixe de longueur L de …PPP, et C_L le suffixe de longueur L de …PPP 0^δ P^a. Les facteurs spéciaux à droite seraient exactement les trois familles distinctes :

- Z_L=0^L, pour 1≤L≤g+δ−2 ;
- B_L, pour g≤L≤bg−1 ;
- C_L, pour (a+1)g≤L≤(2a+1)g+δ−1.

Si cette classification est démontrée pour tous les paramètres, sommer p(L+1)−p(L)=#RS_L avec p(1)=2 fournit la formule. Les deux premières familles sont sans défaut traversé ; la troisième traverse le premier défaut et explique l'interaction avec le second. Cette description est une piste de preuve, pas un substitut à la démonstration d'exhaustivité.

## Deux expériences décisives exécutées

1. Comptage direct des facteurs pour g,δ,a∈{1,…,4}, b∈{a+1,…,7} : **288 familles, 6 720 couples famille/longueur**, aucune divergence avec la formule candidate.
2. Reconstruction des ensembles exacts d'extensions pour g,δ∈{1,…,6}, a∈{1,…,5}, b∈{a+1,…,9} : **1 080 familles, 40 500 couples famille/longueur**, égalité exacte des ensembles de facteurs spéciaux aux trois familles candidates et distinction des familles lorsqu'elles coexistent. Aucun échec.

Ces deux expériences constituent le budget complet de ce verrou ; aucune nouvelle grille ne doit être ouverte par simple reformulation. Verdict général : **INDÉTERMINÉ**, formule candidate appuyée par CALCUL EXACT sur les domaines déclarés. Condition de réouverture : preuve analytique d'exhaustivité, ou contre-exemple indépendant hors grille ; pas une nouvelle recherche aveugle extensive.

## Témoin contrôlé : deux défauts égaux, même période et mêmes gaps

Fixer g=2,δ=1,a+b=6. Les deux mots ont longueur et période fondamentale 14, quatre gaps ordinaires 2 et deux gaps exceptionnels 3.

- (a,b)=(1,5) : W=10010101010100 ; p(6)=9, calcul direct.
- (a,b)=(2,4) : W=10100101010100 ; p(6)=7, calcul direct.

La dépendance à la séparation subsiste donc même lorsque les deux gaps exceptionnels sont identiques. C'est un contre-exemple exact à la suffisance du multiensemble dans cette sous-classe plus restrictive, indépendamment de la formule candidate générale.

## Redondance interne et limites

- Si g=δ=1, W=1^a0 1^b0. Après complémentation, il possède exactement deux 1 à gaps a+1 et b+1. C'est déjà le théorème SINGLE-GAP avec k=2, g'=a+1, h'=b+1. Ce sous-cas n'est pas une nouvelle brique.
- Si a=b, W est le carré de P^a0^δ ; la période fondamentale change. La formule candidate suppose strictement a<b et n'est pas extrapolée au cas symétrique.
- Aucun énoncé de flèche du temps, d'irréversibilité ou de fermeture quantique n'est déduit de ces comptages combinatoires.
- Originalité externe : INDÉTERMINÉE. Repérage bibliographique : Blanchet-Sadri, Chen, Munteanu, A note on constructing infinite binary words with polynomial subword complexity, RAIRO 47 (2013), 195–199, DOI 10.1051/ita/2013033, https://www.numdam.org/article/ITA_2013__47_2_195_0.pdf. Porte sur mots infinis et fonctions de gaps ; ce repérage ne constitue pas un audit complet de notre formule cyclique.
- Base principale et miroir expérimental inchangés. Aucun statut de brique ni dépendance modifié.

## Code de reproduction des deux expériences

```python
from collections import defaultdict
from itertools import product

def formula(g,d,a,b,L):
    return (2+min(L-1,g+d-2)
            +min(max(L-g,0),(b-1)*g)
            +min(max(L-(a+1)*g,0),a*g+d))

count=lengths=0
for g,d,a in product(range(1,5),range(1,5),range(1,5)):
    for b in range(a+1,8):
        P='1'+'0'*(g-1)
        w=P*a+'0'*d+P*b+'0'*d
        T=len(w)
        for L in range(1,T+1):
            actual=len({(w+w)[i:i+L] for i in range(T)})
            assert actual==formula(g,d,a,b,L)
            lengths+=1
        count+=1
print('direct',count,lengths)

count=lengths=0
for g,d,a in product(range(1,7),range(1,7),range(1,6)):
    for b in range(a+1,10):
        P='1'+'0'*(g-1)
        w=P*a+'0'*d+P*b+'0'*d
        T=len(w)
        periodic=P*(2*T+1)
        C=periodic+'0'*d+P*a
        for L in range(1,T):
            extensions=defaultdict(set)
            for i in range(T):
                extensions[(w+w)[i:i+L]].add(w[(i+L)%T])
            actual={u for u,v in extensions.items() if len(v)==2}
            pred=set()
            if L<=g+d-2: pred.add('0'*L)
            if g<=L<=b*g-1: pred.add(periodic[-L:])
            if (a+1)*g<=L<=(2*a+1)*g+d-1: pred.add(C[-L:])
            assert actual==pred
            assert len(pred)==(int(L<=g+d-2)+int(g<=L<=b*g-1)
                              +int((a+1)*g<=L<=(2*a+1)*g+d-1))
            lengths+=1
        count+=1
print('special',count,lengths)
```


# Développement 3 — preuve générale et audit bibliographique borné

Cette section remplace le statut de formule candidate du Développement 2 pour la validité mathématique interne. Le texte antérieur reste conservé comme provenance. Statut courant : **DÉMONTRÉ INTERNE EN STAGING**, sans validation externe ni certification formelle par assistant de preuve. Originalité : **INDÉTERMINÉE**. L'intégration dans le noyau RAVI-2 et son miroir n'est pas réalisée par ce rapport ; aucun compteur des bases n'est modifié.

## Théorème

Pour des entiers g≥1, δ≥1 et 1≤a<b, poser P=10^{g−1}, W=P^a0^δP^b0^δ et T=(a+b)g+2δ. Soit p(L) le nombre de facteurs distincts de longueur L du mot périodique bi-infini W^∞. Pour 1≤L≤T :

p(L)=2+min(L−1,g+δ−2)+min(max(L−g,0),(b−1)g)+min(max(L−(a+1)g,0),ag+δ).

Les facteurs spéciaux à droite sont exactement les trois familles Z, B, C du Développement 2. Les intervalles de longueurs sont ceux indiqués, et les facteurs appartenant aux différentes familles sont distincts lorsqu'ils coexistent.

## Preuve générale

Un facteur binaire est spécial à droite si ses occurrences peuvent être suivies de 0 et de 1. Tous les facteurs sont prolongeables ; le comptage par préfixe donne donc p(L+1)−p(L)=nombre de facteurs spéciaux à droite de longueur L. Cette identité est démontrée directement ici : chaque facteur possède une ou deux extensions ; compter les extensions ajoute une unité exactement pour chaque facteur à deux extensions.

### 1. Facteurs entièrement nuls

Les blocs maximaux de zéros ont longueurs g−1 et h−1, où h=g+δ. Ainsi 0^L a les deux extensions exactement lorsque 1≤L≤h−2 : il apparaît avant la fin d'un grand bloc, suivi de 0, et à sa fin, suivi de 1. Pour L≥h−1 il ne peut être suivi de 0. Cela donne exactement Z_L.

### 2. Toutes les ambiguïtés contenant un 1 se ramènent à deux coupures

Soit u spécial et contenant un 1. Dans une occurrence suivie de 1, le nombre de zéros terminaux de u est soit g−1 soit h−1. Le second cas est impossible : une occurrence de u suivie de 0 contiendrait alors, après son dernier 1, au moins h zéros, tandis que le maximum est h−1. Il reste exactement g−1 zéros terminaux, donc L≥g.

L'occurrence suivie de 0 se termine nécessairement au début de l'un des deux ajouts 0^δ : après les g−1 premiers zéros d'un gap exceptionnel. Ce sont les coupures E_a et E_b situées juste après les blocs P^a et P^b et avant les zéros ajoutés.

L'occurrence suivie de 1 est une coupure ordinaire O_{r,j} après j blocs P dans l'une des deux plages, avec r∈{a,b} et 1≤j≤r−1. Le cas r=1 ne fournit aucune telle coupure.

Tout facteur spécial non nul est donc un suffixe commun d'un contexte à E_c, c∈{a,b}, et d'un contexte à O_{r,j}. Réciproquement, chaque suffixe commun contenant un 1 est spécial puisque les deux symboles suivants sont différents.

### 3. Longueurs maximales des suffixes communs

Comparons les contextes à gauche de E_c et O_{r,j}.

Si c≠j, ils partagent exactement min(c,j) blocs P, puis g−1 zéros. Au symbole précédent, le contexte dont la plage est la plus courte atteint les zéros ajoutés, alors que l'autre atteint le 1 du bloc P précédent. Les symboles divergent puisque δ≥1. La longueur du plus long suffixe commun est donc :

lcs(E_c,O_{r,j})=(min(c,j)+1)g−1, pour c≠j.

Le cas c=j est possible uniquement pour c=j=a et r=b, car j≤r−1 et a<b. Les deux contextes partagent alors, depuis la coupure vers la gauche : a blocs P, δ zéros ajoutés, puis a blocs P et g−1 zéros. La divergence suivante compare le début du précédent ajout de zéros dans la plage courte avec un 1 de la plage longue. Ainsi :

lcs(E_a,O_{b,a})=(2a+1)g+δ−1.

Ces longueurs sont strictement inférieures à T ; la comparaison ne suppose aucune identité des phases.

### 4. Exhaustivité des familles B et C

Pour E_b, on a toujours j<b. Le maximum des suffixes communs est bg−1, atteint à O_{b,b−1}. Les suffixes correspondants sont exactement B_L, pour g≤L≤bg−1.

Pour E_a, la comparaison O_{b,a} donne tous les suffixes jusqu'à (2a+1)g+δ−1 ; les autres comparaisons ne dépassent pas (a+1)g−1. Pour L≤(a+1)g−1, le suffixe à E_a est encore celui du contexte purement P-périodique. Il est donc déjà B_L, et bg−1≥(a+1)g−1. À partir de L=(a+1)g, il voit le zéro supplémentaire du précédent grand gap ; il devient C_L et diffère de B_L au symbole situé (a+1)g positions avant la coupure. La famille C existe ainsi exactement pour :

(a+1)g≤L≤(2a+1)g+δ−1.

Les familles B et C contiennent un 1, contrairement à Z ; B et C diffèrent dès qu'elles coexistent. Ceci prouve l'exhaustivité et la distinction des trois familles, pour tous les paramètres du théorème.

### 5. Sommation

On a p(1)=2 et, pour L≥1,

p(L+1)−p(L)=1[L≤g+δ−2]+1[g≤L≤bg−1]+1[(a+1)g≤L≤(2a+1)g+δ−1].

La somme de ces trois indicatrices pour les longueurs 1,…,L−1 donne exactement les trois termes min/max de l'énoncé. La formule annoncée est démontrée. Les tests finis restent des contrôles distincts de cette preuve, pas son fondement.

## Corollaire : horizon exact de reconstruction de phase

Le mot W est primitif. En effet, les grands gaps h sont identifiables intrinsèquement et sont exactement deux par période écrite. Une période plus courte imposerait deux copies d'une période contenant un seul grand gap ; les deux distances cycliques entre grands gaps seraient alors identiques, donc a=b, contrairement à l'hypothèse. Une répétition de multiplicité supérieure à deux est impossible puisque le nombre de grands gaps serait un multiple supérieur à deux.

On a donc T phases différentes. L'observation de longueur L distingue toutes les phases si et seulement si p(L)=T. Dans la formule, chaque terme min/max est borné par son plateau, et la somme des plateaux vaut T. Tous les termes doivent être saturés. Le premier exige L≥g+δ−1, le deuxième L≥bg, le troisième L≥(2a+1)g+δ. Le troisième domine la première condition. D'où :

L_phase = max(bg,(2a+1)g+δ).

Ainsi, à gaps triés et période fixés, la séparation peut modifier à la fois p(L) et l'horizon de reconstruction. Pour g=2,δ=1,a+b=6 :

- (a,b)=(1,5) : L_phase=10 ;
- (a,b)=(2,4) : L_phase=11.

Ce corollaire est déduit de la formule, sans nouvelle campagne expérimentale. Il concerne un cycle réversible fini observé en binaire ; il ne démontre aucune flèche physique du temps.

## Audit d'originalité : résultat borné

### Sources primaires effectivement consultées

1. Julien Cassaigne, Complexité et facteurs spéciaux, Bulletin of the Belgian Mathematical Society – Simon Stevin 4(1), 67–88 (1997), DOI 10.36045/bbms/1105730624. PDF de l'archive du journal : https://www.maths.tcd.ie/EMIS/journals/BBMS/Bulletin/bul971/cassaigne.pdf. Consultation des définitions et du lien entre facteurs spéciaux et différences de complexité. Cette technique générale est classique et ne constitue pas notre nouveauté.
2. Irina Gheorghiciuc, The subword complexity of a class of infinite binary words, prépublication arXiv:math/0512256 (2005) ; publication référencée dans [3] : Advances in Applied Mathematics 39 (2007), 237–259. https://arxiv.org/abs/math/0512256 et https://arxiv.org/pdf/math/0512256. Consultation de l'introduction, des hypothèses injective / blockwise injective et des énoncés présentés. Ces hypothèses ne couvrent pas directement notre fonction de gaps périodique non constante : une même valeur y réapparaît après une valeur différente. Ce constat ne prouve pas qu'aucun autre résultat de l'article ou de la littérature ne redonne notre formule.
3. Francine Blanchet-Sadri, Bob Chen, Sinziana Munteanu, A note on constructing infinite binary words with polynomial subword complexity, RAIRO – Theoretical Informatics and Applications 47 (2013), 195–199, DOI 10.1051/ita/2013033. https://www.numdam.org/article/ITA_2013__47_2_195_0.pdf. Texte de cinq pages consulté. Le résultat principal construit des mots infinis à croissance polynomiale ; il ne présente pas la formule cyclique ci-dessus.

### Recherche et limites

Requêtes ciblées en anglais et en français sur complexité en facteurs, gap functions, deux écarts/défauts, mots périodiques et facteurs spéciaux. Une seconde recherche par un autre moteur a aussi été tentée ; sa couverture était médiocre sur plusieurs requêtes et n'est pas traitée comme preuve d'absence d'antériorité. La page ScienceDirect de Words and special factors a renvoyé un refus 403 : son texte n'a pas été audité, aucune conclusion d'originalité ne s'appuie sur lui.

La formule exacte de notre famille n'a pas été localisée dans les passages et résultats consultés. **Je ne peux pas confirmer ça** s'agissant d'une affirmation de nouveauté scientifique : absence de correspondance trouvée ne signifie pas absence d'antériorité.

### Redondance interne

La méthode prolonge celle de BR-WORD-SINGLE-GAP-COMPLEX-01, mais la famille générale contient deux grands gaps et introduit un terme d'interaction dépendant de a. Le sous-cas g=δ=1 se ramène exactement, par complémentation, à la brique existante avec k=2, g'=a+1 et h'=b+1 ; aucune nouveauté n'est revendiquée pour ce sous-cas. La recherche dans les cartes consultées n'a pas retrouvé l'énoncé général ; elle n'est pas une recherche exhaustive de toutes les conversations.

### Verdict séparé

- Validité mathématique : DÉMONTRÉ INTERNE EN STAGING, par la classification exhaustive ci-dessus.
- Contrôles : les deux expériences déjà exécutées concordent, budget respecté ; aucune troisième campagne.
- Originalité de la méthode : CONNUE / CLASSIQUE.
- Originalité de la formule particulière et du seuil explicite : INDÉTERMINÉE.
- Validation externe : AUCUNE.
- Certification RAVI-2 complète dans les bases et synchronisation : NON EFFECTUÉES dans ce rapport ; conserver hors noyau jusqu'à intégration et audit indépendant du certificat. Cela ne suspend pas la preuve rédigée, mais interdit de présenter une promotion des bases comme déjà accomplie.

Le verrou de preuve de cette famille est fermé au niveau interne ; celui de la priorité scientifique reste INDÉTERMINÉ. Ne pas ouvrir automatiquement une cascade à trois défauts. La prochaine action de certification est une relecture indépendante du lemme des suffixes et l'intégration versionnée du résultat si cette revue valide le certificat.


# Décision documentaire RAVI-2 — commit 25

Revue de validité : PASS au niveau interne pour le domaine strict g,δ≥1 et 1≤a<b. Le lemme des suffixes a été relu par analyse des coupures, et les deux contrôles entiers ont été reproduits à partir du code archivé, avec les mêmes sorties : direct 288/6720 et special 1080/40500. Cette reproduction n'est pas comptée comme une troisième expérience.

Décision : intégrer BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01 comme DÉMONTRÉ interne, avec originalité INDÉTERMINÉE. Le terme « certifié » dans le registre désigne cette validation interne documentée, sans revue humaine externe, sans second modèle et sans assistant de preuve formelle. Les deux contrôles sont indépendants dans leur mode de calcul, pas dans l'identité de leur auteur.

La cartographie bibliographique ciblée est venue après le développement : non-conformité de séquence conservée dans le certificat et le registre bibliographique, jamais réécrite comme un audit initial. Cette réserve interdit de revendiquer une nouveauté, mais n'invalide pas l'argument mathématique autonome.

Aucun nouveau DEPEND_DE : la preuve est autonome. Ne pas annoncer une généralisation de toutes les familles single-gap ; seul le sous-cas g=δ=1 a la correspondance par complémentation explicitée plus haut. Les recherches de priorité demeurent INDÉTERMINÉES et closes sans revendication.

Le certificat JSON, les contrôles et le manifeste TWO_EQUAL_GAPS_COMMIT_VERIFY_2026-10-20.json accompagnent le commit versionné des deux bases et des index. Les sections précédentes « staging », « bases inchangées » et « attente de revue » sont les états historiques avant cette revue. L'état de persistance doit être confirmé séparément par les résultats réels des écritures ; ce texte seul ne prouve pas une synchronisation.