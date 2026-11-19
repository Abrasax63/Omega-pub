# Reader21 — préenregistrement : passerelle sémantique conservatrice + appels Web bornés

Date : 2026-11-19. Branche de recherche empilée sur Reader20 (#189) ; aucune modification de `main`.

## Objectif double
1. Accepter une formulation **française plus naturelle mais encore bornée** pour trois familles existantes : produits entiers, congruences de systèmes dynamiques finis et 2-colorabilité de graphes. Déduire un contrat exact et n'appeler Reader20 que si toutes les hypothèses sont textuellement explicites. L'abstention est un résultat valide, jamais transformé en `false`. Aucune prétention à comprendre toute la langue scientifique.
2. Donner à Omega de **vrais appels HTTP(S)** de recherche bibliographique et de lecture documentaire : metadata Crossref publique, sans clé, et lecture de Markdown publié dans **le dépôt public Omega-pub seulement**. Tous les contenus web sont considérés comme données non fiables. Aucun appel web ne peut déclencher seul un calcul, une promotion ou une modification de code.

## Gel des tests AVANT code
- Nouveau jeu de douze formulations françaises, figé dans `FR_CASES_FROZEN.md` AVANT implémentation, en alternant 6 énoncés compatibles et 6 énoncés devant provoquer `ABSTAIN` (hypothèses omises, ambiguïtés, contradictions, injection textuelle). Le format de source est un Markdown avec sections `## Cas XX` et une phrase chacune.
- Les trois familles ont **2 exemples compatibles chacune**, 6 cas négatifs. Les références attendues ne sont **pas exposées à l'adaptateur**. Protocole local, annotations de l'auteur **non indépendantes** ; ce n'est pas un benchmark externe.
- Calcul réel des cas acceptés par Reader20 `parse_claim` puis `evaluate_exact`; trace phrase, lignes du blob, AST, calcul, refus. Validation de l'AST via reconstruction du contrat et refus si des nombres non couverts ou des limites implicites existent.
- Contrôle de sécurité web : domaine inconnu, IP, HTTP, localhost, credentials URL, port, fragments, sous-domaines malveillants, redirection, contenu trop grand, type invalide, timeout/429/5xx et injection dans le texte. Tous ces cas sont des échecs sûrs, pas des preuves. Seuls les endpoints construits par le programme sont admis; jamais un `fetch(url)` arbitraire.
- **Appels réels figés** : une recherche `finite dynamical systems observability` dans Crossref (`/works?query.bibliographic=...&rows=3&select=DOI,title,issued,URL,type`) et un téléchargement Markdown `https://raw.githubusercontent.com/Abrasax63/Omega-pub/main/02_MATHEMATIQUES/observabilite_temporelle/OBS-V8-FACT-INF.md`. Maximum 2 requêtes, 3 références, 256 KB par réponse, 10 secondes de délai d'ouverture, 0 secret. Le document téléchargé peut évoluer sur `main` et sera archivé avec hash SHA256 du corps réellement reçu; ne jamais prétendre figer son contenu à l'avance.
- En cas d'échec distant, enregistrer `REMOTE_FETCH_FAILED` avec exception sans réessayer via un autre domaine ou abaisser la politique. La CI de sécurité sans réseau peut réussir; le résultat web ne sera annoncé fonctionnel que si le run réel renvoie des corps et hashes pour les deux appels. Crossref renvoie des **métadonnées déposées**, jamais des validations de théorèmes.

## Contrôles et politiques
- Web accessible **uniquement via un module `web_access.py`** du pilote. HTTPS, hôtes littéraux `api.crossref.org` et `raw.githubusercontent.com`, sans redirections, sans proxies hérités, port 443, réponse binaire bornée, lecture seule et jamais de clé payante.
- Le module retourne des objets `UNTRUSTED_WEB_DATA` avec URL, hash, taille, extrait, date d'accès et état; aucune méthode de ce module ne peut appeler `evaluate_exact`, GitHub write, shell ou LLM. Les sources web ne sont pas des instructions de configuration ou de modification du code.
- Le parseur n'accepte que six formes phrastiques ancrées et documentées, avec paramètres/domaines explicites et sans ligne additionnelle. Répartition des cases entre les 3 familles connue avant code. Distinguer `SOURCE_ANCHORED`, `PARSE_SUPPORTED`, `EXACT_CHECKED_RESTRICTED`, `ABSTAIN_UNSUPPORTED`, `WEB_FETCHED_UNTRUSTED`.
- Les tests de non-régression de Reader20 doivent rester réussis ; 0 modification de son code.
- Contrôle additionnel : même erreur numérique n'autorise jamais de modifier le texte source. L'AST et le verdict sont dérivés de la source, et `false` signifie `assertion réfutée sous hypothèses` uniquement.
- Aucune évaluation indépendante humaine n'est disponible. Sans celle-ci : ne pas affirmer une amélioration de compréhension du langage naturel sur des publications scientifiques.

## Tests décisifs
- Lecture sûre et AST routés : 6/6 cas compatibles, 6/6 refus, 0 promotion, contrôles négatifs, citations exactes. Comparer avec le routeur strict Reader20 qui n'accepte pas une phrase libre.
- Appels HTTP : 2/2 statuts `WEB_FETCHED_UNTRUSTED` sur GitHub Actions si les fournisseurs répondent dans les délais, un DOI et un fichier Markdown archivés avec hashes ; sinon succès limité au module/contrôles offline, et échec d'accès réel à signaler.
- Toute conclusion au-delà de cette grammaire, notamment compréhension libre, nouveauté mathématique, confiance bibliographique ou autonomie du modèle, reste `NON_DÉMONTRÉ`.
