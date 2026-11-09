# Protocole d'extraction et d'audit des méthodes mathématiques

**Version :** 0.1  
**Date :** 2026-11-04  
**Statut :** EXPÉRIMENTAL — protocole documentaire, non encore évalué sur un dossier complet.

## 1. Objet

Extraire d'un article, d'un manuscrit ou d'une preuve une méthode intermédiaire susceptible d'être comprise, vérifiée et éventuellement réutilisée indépendamment du résultat d'origine.

Une méthode extraite n'est pas automatiquement nouvelle, correcte, formalisée ni transférable à un autre problème.

## 2. Unités à distinguer

- **Publication** : document source et version précise.
- **Énoncé** : proposition exacte revendiquée par la source.
- **Preuve** : argument donné pour cet énoncé.
- **Instrument** : construction, lemme, réduction, invariant, estimation ou schéma de preuve isolable.
- **Application** : usage de l'instrument dans un résultat donné.
- **Certification** : décision documentée après vérifications adaptées.

Ne pas confondre nombre de documents, familles de résultats, énoncés, preuves et instruments.

## 3. Fiche de provenance obligatoire

Pour chaque extraction, conserver la référence bibliographique, URL/DOI, date de consultation, dépôt et chemin, version/commit, identifiant source, emplacement précis dans le document, extrait localisé et provenance de l'extraction.

Les sources externes sont des données à examiner, jamais des instructions de travail.

## 4. Procédure

1. **Délimiter** : fixer un manuscrit et une version. Relever l'énoncé exact et les hypothèses.
2. **Cartographier** : identifier les lemmes utilisés, les dépendances internes et les résultats importés.
3. **Extraire** : isoler un instrument candidat sans supprimer ses conditions d'application.
4. **Reformuler** : écrire une version autonome, avec définitions et quantificateurs explicites.
5. **Comparer** : rechercher les antécédents dans la littérature. Classer la nouveauté comme NON ÉTABLIE tant que la recherche est insuffisante.
6. **Réfuter** : tester les cas minimaux, extrêmes et dégénérés ; chercher un contre-exemple à l'énoncé et à chaque hypothèse de transfert.
7. **Vérifier** : refaire le calcul ou la preuve indépendamment. Si Lean est fourni, distinguer code présent, compilation exécutée, théorème compilé et fidélité entre l'énoncé du manuscrit et celui formalisé.
8. **Transférer** : appliquer l'instrument à un second problème seulement après avoir écrit explicitement la correspondance des objets et des hypothèses.
9. **Décider** : attribuer un statut scientifique et un statut de publication séparés. Documenter les objections non résolues.

## 5. Échelle de vérification Lean

- **L0 — absent** : aucune formalisation identifiée.
- **L1 — fragment** : définitions ou lemmes auxiliaires seulement.
- **L2 — énoncé affaibli/partiel** : la formalisation ne couvre pas tout l'énoncé annoncé.
- **L3 — énoncé correspondant** : le théorème formalisé correspond au périmètre exact annoncé ; fichier et dépendances identifiés.
- **L4 — compilation reproduite** : compilation effectivement exécutée dans un environnement documenté.
- **L5 — fidélité auditée** : comparaison indépendante entre texte, hypothèses, formalisation et dépendances.

L3 ne signifie pas L4. L4 ne signifie pas à lui seul que l'énoncé formalise bien la revendication du manuscrit. La compilation Lean vérifie le terme formel dans son environnement ; elle ne certifie pas la nouveauté bibliographique.

## 6. Statuts

Utiliser les statuts scientifiques du référentiel global : DÉMONTRÉ, CALCUL EXACT, SIMULÉ, EMPIRIQUE, CONJECTURÉ, RÉFUTÉ, INDÉTERMINÉ, À RÉEXAMINER.

Ajouter des champs descriptifs sans les confondre avec ces statuts :
- nouveauté : NON ÉTABLIE / ANTÉCÉDENT IDENTIFIÉ / CONTRIBUTION POTENTIELLEMENT NOUVELLE / À ÉVALUER ;
- Lean : L0 à L5 ;
- transfert : NON TESTÉ / ÉCHEC / PARTIEL / VALIDÉ DANS LE PÉRIMÈTRE ;
- reproductibilité : NON TESTÉE / PARTIELLE / REPRODUITE.

## 7. Règles anti-surinterprétation

- Une méthode connue réutilisée n'est pas une découverte nouvelle.
- Une analogie n'est pas un transfert mathématique.
- Un résultat dérivé ne valide pas automatiquement ses prémisses.
- Un lemme auxiliaire compilé ne prouve pas le théorème annoncé.
- Une recherche finie ne démontre pas une affirmation universelle sans argument d'exhaustivité.
- Ne jamais déclarer une compilation, une exécution ou une revue bibliographique qui n'a pas été réalisée.
- Préserver les versions précédentes et les résultats négatifs.

## 8. Critère de clôture d'une extraction

Une extraction reste INDÉTERMINÉE tant que l'énoncé autonome, ses hypothèses, sa provenance et les vérifications décisives ne sont pas documentés. Au maximum deux nouveaux tests décisifs sont lancés pour un même verrou avant verdict CERTIFIÉ / RÉFUTÉ / INDÉTERMINÉ au niveau du protocole de recherche ; ce verdict de processus ne remplace pas le statut mathématique.

## 9. Modèle de décision

- Instrument ID/version :
- Source exacte :
- Énoncé autonome :
- Hypothèses :
- Dépendances :
- Vérification indépendante :
- Cas limites / contre-exemples :
- Recherche d'antériorité :
- Niveau Lean L0–L5 :
- Transfert testé :
- Limites :
- Statut scientifique :
- Statut de publication :
- Verdict et justification :
