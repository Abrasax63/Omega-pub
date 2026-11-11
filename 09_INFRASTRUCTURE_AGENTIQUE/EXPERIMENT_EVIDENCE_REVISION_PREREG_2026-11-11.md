# OMEGA-EVIDENCE-001 — pré-enregistrement, révision de certificats à partir de changements Git réels

**11 novembre 2026 — GEL AVANT récupération de l’historique et calcul des résultats de l’épreuve.**

## Question et limitations
Tester la conservation d'une bibliothèque de **certificats de contenu versionnés** lorsqu'un dépôt public change. Il s'agit d'une expérience de **validité de provenance au sens du commit et du fichier**, **pas** de la vérité mathématique d'un théorème, de l'authenticité juridique d'une publication ou de la fiabilité d'un auteur. Deux digests opposés d'un même fichier sont **compatibles** s'ils correspondent à deux versions différentes ; ils sont **contradictoires uniquement en prétendant s'appliquer au même commit**.

Le but est de vérifier : 1) qu'un certificat ciblant une version passée reste conservé dans l'historique, 2) qu'il cesse d'être présenté comme actuel pour un contenu modifié, 3) que les certificats de dépendances inchangées restent valables, et 4) que l'avantage de coût résiste à la comparaison avec un **simple index de dépendances**, lequel connaît les mêmes changements.

## Source réelle gelée
Dépôt public **`pallets/flask`**, branche `main`, commit cible **`49943b5a94413a530761350f04e896f76e8d620e`** (GitHub : https://github.com/pallets/flask/commit/49943b5a94413a530761350f04e896f76e8d620e), identifié par GitHub avant lecture des diffs.

Rejouer les **40 transitions de premiers parents immédiatement antérieures à ce commit**, en incluant le commit cible comme dernier état : `git rev-list --first-parent --max-count=41 <SHA>`, puis renverser l'ordre. Aucun remplacement des commits qui ne modifient pas le corpus. **20 premières transitions = calibration descriptive**, **20 dernières = test gelé**. Le plan n'a pas d'hyperparamètres dépendants des résultats de calibration : il doit rester identique sur les 40.

À l'état initial des 41 commits, dresser la liste de tous les chemins versionnés du dépôt sous `src/flask/`, `tests/`, `docs/`, et suffixes `.py`, `.rst`, `.md`, `.toml`. Trier par `sha256(path UTF-8)` puis par chemin et garder les **128 premiers**, ou tous s'il y en a moins ; ne pas choisir les chemins après observation des changements. Toute absence de fichier en cours de parcours est une **suppression**, jamais un digest inventé.

Émettre des assertions de provenance sur les chemins échantillonnés, avec dépendances fixes :
- une assertion **par fichier** ;
- une assertion **par couple circulaire** de chemins consécutifs de l'ordre échantillonné ;
- une assertion **par triple circulaire** (indices i, i+1, i+2).
Ces assertions signifient exclusivement « les contenus SHA-256 des dépendances correspondent aux contenus du commit courant ». Ce ne sont pas des preuves du comportement du logiciel.

## Politiques préfixées
Chacune reçoit la même suite de commits, le même référentiel public, les mêmes métadonnées `git diff --name-only` et le même historique initial. Chaque vérification coûte **une lecture avec calcul SHA-256 d'un contenu de fichier** ; le traitement de métadonnées Git est commun et n'est pas facturé par la mesure principale. Aucune mesure de latence/tokens réelle ne peut être inférée de cette unité.

- **A `no_refresh`** : conserver les certificats initiaux en affirmant qu'ils sont encore actuels, sans vérifier. Contrôle négatif non fiable, pour mesurer les faux certificats.
- **B `full_reverify`** : lire et hacher tous les fichiers du portefeuille à chaque commit, sans limite de budget ; **référence haute couverture mais coût non égal**, rapportée séparément.
- **C `dependency_index_8`** : index simple chemin→assertions ; jusqu'à **8 fichiers modifiés** (tri déterministe) recontrôlés par transition. Mettre les autres certificats dépendants en **attente**, jamais présenter « courant » sans contrôle ; conserver l'historique antérieur des certificats.
- **D `omega_ledger_8`** : adaptateur expérimental de mémoire scientifique versionnée, même **budget 8** et mêmes métadonnées, vérifie les mêmes changements pertinents, conserve la chaîne de provenance et signale explicitement les conflits de version. Aucun crédit de supériorité si D et C produisent les mêmes décisions/coûts : l'index simple est la baseline forte.
- **E `invalidate_all_8`** : contrôle négatif qui rend toutes les assertions en attente après chaque commit et recontrôle au plus 8 fichiers ; cet exemple montre le coût de ne pas conserver les preuves non affectées.

Pour C et D, les dossiers touchés mais dont les octets restent identiques (ex. changement de mode) ne doivent pas être déclarés substantiellement contradictoires ; le nouveau SHA-256 décide après lecture. Les fichiers supprimés donnent `unavailable`, jamais une affirmation courante. Les changements hors du corpus ne doivent pas déclencher d'invalidation. Une réutilisation d'un digest antérieur n'efface pas l'historique.

## Mesures de coût / exactitude
Pour chaque commit et politique : nombre d'assertions présentées **courantes et effectivement exactes**, nombre de **fausses assertions courantes** (critique), nombre d'assertions **en attente/non disponibles**, nombre de fichiers réellement **hachés**, nombre d'attestations antérieures conservées et nombres de dépendances affectées. Le statut d'un certificat courant est correct si, pour toutes ses dépendances, le SHA-256 associé correspond au SHA-256 des **octets réels du fichier à cette révision**. Le correcteur calcule cette vérité **séparément après les décisions**, avec lecture hors budget commun identique pour les bras ; ne jamais fournir la vérité du correcteur aux politiques pendant leur choix.

Rapporter **TRAIN et TEST séparément**, ainsi que le nombre de transitions sans fichier pertinent modifié. Les références full/no_refresh ne sont pas des compétiteurs au budget 8 ; le verdict d'avantage propre à Omega est fondé **uniquement sur C contre D à budget et informations égaux**. En l'absence de gain sur C, verdict d'**absence d'avantage propre démontré**. Ne jamais reparamétrer après lecture des résultats.

## Hypothèses à falsifier, arrêts
1. Un événement Git réel provoque des changements de digest et des versions historiques incompatibles pour au moins une dépendance sélectionnée (sinon expérience insuffisamment discriminante, **indéterminée**, pas victoire).
2. Une modification n'invalide pas les assertions indépendantes.
3. L'ancien certificat reste consultable **pour son commit historique**, même si sa version courante est révoquée.
4. Les policies C/D **n'émettent aucun certificat actuel faux**, y compris après une suppression, un changement de mode, un retour à un ancien contenu et un événement dépassant le budget de huit contrôles.
5. Aucune lecture du corrigé avant la décision ; inclure des tests synthétiques adversariaux de diff tronqué, mal signé, faux digest et contenu de fichier contradictoire. La confiance dans le `git diff` dérivé du commit est une hypothèse de la simulation ; un faux index externe doit conduire à l'abstention ou être explicitement hors périmètre.
6. Auditer au moins un commit par une seconde voie `git diff-tree` / `git ls-tree` + SHA256 et contrôler indépendamment les métriques des baselines fortes.
7. Aucun mécanisme ne prétend certifier la véracité sémantique du contenu ni la signature cryptographique d'un auteur Git.

PR en brouillon, branche empilée sur #40. N'écrire ni `main`, ni SQLite, ni mémoire CORE. Ne pas transformer cet audit de provenance de fichiers en preuve d'intelligence scientifique générale.
