# P5 — pipeline d'analyse descriptive v0.2

**Statut :** outil préparatoire ; aucune donnée expérimentale réelle n'est incluse.
**Compatibilité :** protocole P5 v0.2 et validateur de notes v0.2.
**Confidentialité :** clé d'aveuglement et sorties brutes conservées hors du dépôt public.

## Objectif

Transformer des notes aveugles figées en comparaisons appariées par cas, sans
fabriquer de verdict scientifique. Le pipeline utilise uniquement la bibliothèque
standard Python ; aucune dépendance externe ni calcul statistique lourd n'est requis.

## Fichiers d'entrée

1. ratings.jsonl : une ligne par couple (cas, sortie opaque, évaluateur), conforme
   à prism/evaluation.py. Le fichier ne contient jamais le bras A/B/C.
2. blind_key.json : fichier privé, utilisé uniquement après gel des notes.

Format attendu de la clé (identifiants fictifs) :

    {
      "mappings": [
        {"case_id": "case-01", "blind_output_id": "opaque-1", "arm": "A"},
        {"case_id": "case-01", "blind_output_id": "opaque-2", "arm": "B"},
        {"case_id": "case-01", "blind_output_id": "opaque-3", "arm": "C"}
      ]
    }

Ne jamais déposer la clé réelle dans le dépôt public, un artefact CI public,
ni dans un espace accessible aux évaluateurs.

## Exécution

Depuis le dossier prism :

    from analysis import analyze_files

    result = analyze_files(
        ratings_path="/private/p5/ratings.jsonl",
        blind_key_path="/private/p5/blind_key.json",
        output_path="/private/p5/analysis.json",
        ratings_sha256=frozen_ratings_digest,  # fourni par le registre privé du gel
        expected_case_ids={"case-01", "case-02", "case-03", "case-04", "case-05"},
    )
    print(result["validation"])

Les identifiants attendus doivent correspondre au pré-enregistrement réel,
pas à des noms supposés. Les fichiers privés ne sont pas copiés dans le dépôt.

## Sorties

- moyennes et étendues des six dimensions, par cas et par bras ;
- étendue des désaccords entre évaluateurs, dimension par dimension ;
- comparaisons appariées C−A, C−B et B−A, séparées pour chaque dimension ;
- nombre de cas favorables, égaux et défavorables ;
- comptages d'erreurs rapportés par les évaluateurs, explicitement étiquetés.

Aucun score composite, test de significativité, intervalle artificiel,
classement global ou certification n'est calculé. Avec cinq cas hétérogènes,
les résultats restent descriptifs et exploratoires.

## Garde-fous

- Vérifier l'empreinte SHA-256 et la liste de cas pré-enregistrée, puis valider les
  notes avant de lire la clé. L'empreinte doit venir du registre de gel privé,
  conservé séparément avec contrôle d'accès et horodatage.
- La clé doit couvrir exactement chaque couple cas/sortie opaque, sans doublon.
- Chaque cas doit avoir exactement une sortie par bras et répétition.
  Pour plusieurs répétitions, passer le nombre pré-enregistré avec
  `repetitions=` et donner un entier de 1 à ce nombre dans chaque entrée
  `repetition` de la clé privée. Les notes restent opaques.
- Chaque évaluateur doit noter toutes les sorties d'un cas. Les répétitions
  sont moyennées à l'intérieur du cas et ne gonflent pas le nombre de cas.
- Les notes initiales et les arbitrages restent dans des fichiers séparés.
- Ne pas moyenner les coûts, durées ou appels répétés dans les lignes de notation :
  ces mesures appartiennent au journal d'exécution, une ligne par exécution.
- L'outil ne prouve ni l'aveuglement ni l'indépendance humaine ; ces points exigent
  une procédure et des attestations externes.

## Limite de lancement

Ce pipeline ne crée pas de holdout privé et ne génère aucune réponse A/B/C.
Le holdout v0.2 reste un pilote public, pas un test secret garanti. Le lancement
attend un nouveau jeu non exposé, son corrigé privé vérifié, les prompts et budgets
gelés, et deux évaluateurs réellement indépendants. Aucun accès au corrigé n'est
requis pour exécuter le pipeline.

## Calibration publique intégrée

Dans un checkout réunissant les modifications des PR #20 et #21, exécuter
`python p5_calibration.py` depuis `09_INFRASTRUCTURE_AGENTIQUE/prism`.
Le script utilise uniquement le cas public `P5V2-FORMAL-001`, le planificateur
P1 pour C, des rôles fixes pour B et un fournisseur simulé pour les trois bras.
Les notes, les durées et les tokens sont des valeurs synthétiques. Les
plafonds de l'essai sont deux appels, 256 tokens cumulés, deux secondes
simulées et zéro outil par bras.

Le registre P4 consigne une empreinte d'identité avant l'invocation du
fournisseur simulé. Les appendices P5 sont verrouillés et synchronisés sur
disque avant l'envoi. La télémétrie est rapprochée de son empreinte terminale. Le rapprochement exige une correspondance exacte
avec la télémétrie avant d'appliquer le pipeline d'analyse. L'essai retire
la première tentative de C tout en gardant les trois bras présents.
L'analyse doit alors s'arrêter avant de lire la clé et sans écrire de
rapport. Une seconde injection contrôle le rejet d'un dépassement de
tokens pour chaque bras.

Sur le même checkout, `python p5_http_calibration.py` exerce le transport HTTP
sur loopback. Un arrêt avant publication du fichier laisse une tentative
indéterminée qui bloque l'analyse. Un arrêt après publication durable et
avant l'événement terminal permet de récupérer la réponse et la télémétrie
sans rappeler le fournisseur. Le registre P4 fixe l'empreinte du contenu
avant publication et le rejeu vérifie cette empreinte avant de terminer la
tentative. Le test couvre aussi le délai de lecture HTTP et le budget de C.

Les fichiers de réponse et télémétrie de cet essai sont synthétiques et
stockés dans un répertoire temporaire. Le pilote réel exige un espace
privé contrôlé, la validation du SDK et de ses reprises, et une procédure
pour résoudre les envois qui restent indéterminés. Le verrou et la
synchronisation du prototype ciblent POSIX/Linux.

### Calibration du SDK Responses

Dans le checkout combiné, installer le SDK dans un environnement de test
isolé avec `python -m pip install openai==3.49.0`, puis lancer
`python p5_sdk_calibration.py` depuis `prism`. Le SDK parle à un serveur
local avec une clé factice et un transport sans proxy ni redirection.
Le test vérifie le plafond de sortie envoyé, le délai de lecture, et
l'absence de réessai implicite après HTTP 500 ou expiration. Après HTTP
500, le harnais conserve la tentative en état indéterminé au redémarrage.

Le client réserve une enveloppe d'entrée et transmet le reste comme
plafond de sortie. L'enveloppe d'entrée n'est pas un comptage préalable
des tokens du fournisseur. Le harnais contrôle le cumul sur l'usage
effectivement rapporté. Le délai SDK testé est un délai de lecture, pas
un chronomètre global de campagne. Le pilote exige encore de valider
la méthode de budget d'entrée et le modèle choisis.

### Cas public de réfutation

Exécuter `python p5_refutation_calibration.py` depuis `prism`. Ce contrôle
utilise `P5V2-ADV-001` et fonctionne sans SDK. Sur quatre états, les tables
(1, 2, 3, 0) et (1, 2, 3, 1) réalisent respectivement une permutation et
une collision entre 0 et 3. Les trois transitions observées sont communes.
Sur n états, les n−3 images restantes sont libres, donnant n^(n−3)
extensions. Pour rester injectives, elles doivent permuter les n−3 images
encore libres, donnant (n−3)! extensions. Le script confronte ces comptes
à l'énumération exhaustive de 4 à 7 états et rejette cinq certificats invalides.

B reprend les cinq rôles fixes de la calibration. C reçoit le même énoncé
avec le type mathématique et active réfutation et formalisation. Un second
passage, avec le seul indicateur de calcul explicite modifié, active aussi
le rôle computationnel. Ce contrôle mesure le routage, sans génération ni
notation de réponses de modèle. Pour une future comparaison de qualité,
figer l'encodage de la mission avant de produire les réponses.

### Essai documentaire B/C automatisé

Le cas public K-17 confronte deux notices fictives à une consigne interne.
Le barème vérifie la clause de transition citée, les deux délais
conditionnels, l'erreur du message interne et la date de réception manquante.

Sur le checkout combiné, avec le SDK 3.49.0 installé, exécuter
`python p5_documentary_bc_test.py` depuis `prism`. Le SDK utilise un
transport HTTP simulé. Une exécution complète fait deux comptages
d'entrée, puis deux générations sans historique et sans outil.
Un budget insuffisant bloque la génération. Un écart de comptage entre
prévol et réponse bloque le paquet de notation.

Après autorisation de dépense, choisir un snapshot de modèle qui accepte
les deux opérations Responses et renseigner la clé dans l'environnement.
La commande de lancement est :

```sh
python p5_documentary_bc.py /chemin/prive/k17-essai \
  --live --model SNAPSHOT --token-cap PLAFOND_TOTAL --output-cap PLAFOND_SORTIE
```

Utiliser un répertoire neuf hors de tout checkout Git. Transmettre seulement
`grading.json` au correcteur, qui fige sa notation avant de recevoir
`key-private.json`. L'ordre des requêtes et l'attribution X/Y sont tirés
séparément. Les sorties elles-mêmes peuvent parfois suggérer un bras.
Les données brutes, le journal et le plan exact restent dans le répertoire
privé. Les plafonds de tokens de génération ne sont pas un plafond
monétaire. La facturation du prévol et les tarifs du snapshot sont à
vérifier avant l'exécution réelle.
