# OMEGA-STATE-SPLIT-ACTIVE-02

Sélecteur actif de requêtes fondé sur un **espace de modèles borné** : après chaque requête facturée et sa réponse, il élimine les hypothèses incompatibles, puis recalcule le mot suivant.

**Préenregistrement avant code** : [commit a70c231](https://github.com/Abrasax63/Omega-pub/commit/a70c231753a2112dc0bc0501dd742b5aff4072ce), [protocole](PREREG_2026-11-17.md).

## Trois bras et nouvelles données
- `STATIC_DIVERSITY` : le calendrier figé de la PR #143, au plus 32 mots EQ de longueur 10.
- `FIXED_PREFIX` : huit mots de longueur 10 couvrant tous les préfixes binaires de longueur 3, référence simple avec un plafond maximal de 80 symboles.
- `ACTIVE_DISAGREEMENT` : sélection réitérée parmi les modèles encore cohérents, au plus 32 mots de longueur 10.

Les **24 systèmes TEST** proviennent d'un tirage fixe `random.Random(53117)` parmi les modèles compatibles à trois états accessibles et distinguables. Les 8 modèles déjà utilisés comme témoins dans la PR #143 sont exclus. Aucun nouveau modèle de langage, aucune API payante.

## Résultat local initial, à vérifier sur GitHub
`ACTIVE` **24/24** divergences détectées en **10,8333 symboles moyens** ; `FIXED_PREFIX` **24/24**, **25,0** ; `STATIC_DIVERSITY` **23/24**, **23,3333**. Le précritère correspond à `DESCRIPTIVE_ACTIVE_BENEFIT` sur ce banc synthétique borné. Ces chiffres ne démontrent **ni généralisation statistique ni intelligence autonome** ; ils ne certifient pas non plus que le modèle entier a été reconstruit.

L'écart avec STATIC se concentre dans un cas difficile où STATIC consomme 32 mots sans détecter de divergence alors que ACTIVE en utilise deux. Dans la majorité des autres cas, les deux commencent par le même mot. Il ne faut pas attribuer toute la différence avec FIXED à la seule mise à jour adaptative : le **premier choix de mot** est également différent.

## Reproduction
```sh
python -m unittest discover -s experiments/omega-state-split-active-02 -p test_active.py -v
python experiments/omega-state-split-active-02/active_lab.py --output /tmp/omega-active-02.json
```

Python standard uniquement. Les preuves et les coûts sont archivés par [workflow dédié](../../.github/workflows/omega-state-split-active-02.yml). DRAFT, aucune modification de `main` ni du CORE.