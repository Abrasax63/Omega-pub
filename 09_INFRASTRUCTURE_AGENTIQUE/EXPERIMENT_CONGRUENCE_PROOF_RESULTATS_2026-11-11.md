# OMEGA-CONG-001 — révision logique et test de congruence, résultats contrôlés

**11 novembre 2026. Statut : CALCUL EXACT DANS LE MODÈLE FINI, VALIDATION INDÉPENDANTE DE CODE ; AUCUNE SUPÉRIORITÉ OMEGA ÉTABLIE.**

## Pré-enregistrement vérifiable

- Cas construits, gelés **avant le solveur** : commit [`7d6185185f3deddef95553d7af1dead31ef3c88b`](https://github.com/Abrasax63/Omega-pub/commit/7d6185185f3deddef95553d7af1dead31ef3c88b), fichier `prism/congruence_revision_cases_v01.json`.
- Contrat de test, catégories de verdict et concurrent ATMS fort : commit [`91b7d9b0d63049a124c328404441a276adc1cb4c`](https://github.com/Abrasax63/Omega-pub/commit/91b7d9b0d63049a124c328404441a276adc1cb4c), avant code et résultats.
- Quatre suites **publiques et construites** de retraits/activations de contraintes `x ≡ r (mod m)`, avec `m | 60`. Leurs scénarios n'ont pas été collectés indépendamment du concepteur et n'impliquent ni modèle de langage ni recherche scientifique nouvelle.
- Deux scénarios de calibration (24 états) et deux de test (26 états), soit **50 états**, **276 évaluations « hypothèses actives × question »** (120 calibration et 156 test).

## Vérification mathématique

**Voie 1 : symbolique**, solveur CRT généralisé sur les hypothèses du support. Pour fusionner `x ≡ a (mod L)` et `x ≡ b (mod m)`, existence si et seulement si `gcd(L,m)` divise `b−a`. Une fusion cohérente donne le résidu `a'` et le module `lcm(L,m)`. Pour une requête `x ≡ r (mod q)` :
- `ENTAILED` si `q | L` et `a ≡ r (mod q)` ;
- `REFUTED` si `a−r` n'est pas divisible par `gcd(L,q)` ;
- `UNDETERMINED` sinon ;
- `INCONSISTENT_ENVIRONMENT` si les prémisses actives ne possèdent aucun modèle (sans explosion logique).

**Voie 2 : ATMS fini**, vérifier indépendamment les ensembles de solutions des prémisses par énumération des 60 résidus et calculer toutes les justifications minimales pour l'inclusion de taille au plus 3. Une justification n'est admissible que si elle est elle-même cohérente, utilise seulement des hypothèses **actives** et implique ou exclut effectivement la requête. Les deux voies ont les mêmes hypothèses, requêtes et événements.

**Pourquoi trois prémisses suffisent dans CE cadre :** tout module divise `60 = 2²·3·5`. Dans un ensemble cohérent, sélectionner au plus une congruence portant l'exposant maximal de 2, une portant celui de 3 et une portant celui de 5 préserve le `lcm` de tous les modules ; les résidus compatibles déterminent alors la même classe de solutions. Un ensemble incohérent de congruences d'une variable possède déjà une paire incompatible par le critère PGCD du CRT généralisé. **Ces propriétés ne sont pas extrapolées à des preuves arbitraires.**

## Résultats par partition

| Statut | Calibration (120 jugements) | Test (156 jugements) | Total |
|---|---:|---:|---:|
| Conclusion démontrée | 55 | **75** | 130 |
| Conclusion réfutée | 28 | **25** | 53 |
| Indéterminée | 12 | **14** | 26 |
| Environnement contradictoire | 25 | **42** | 67 |
| **Total** | 120 | **156** | **276** |

Dans l'ensemble du corpus, 276 supports de preuve actifs ont été inspectés : 128 en calibration, **148 en test**. Dans **87 jugements** (41 calibration, **46 test**), au moins **deux voies de justification distinctes** restaient actives. La rétractation d'une hypothèse n'enlève pas une conclusion démontrée par une autre preuve toujours active ; en environnement contradictoire, **aucune réponse globale n'est présentée comme théorème**.

**Erreurs de verdict du moteur symbolique contre l'énumération des 60 résidus : 0/276.** **Erreurs dans les supports actifs émis et vérifiés séparément : 0/276.** Le registre symbolique Omega et le concurrent ATMS fini ont **des verdicts, supports et détections de conflits identiques sur tous les états**. **Avantage propre à Omega : NON DÉMONTRÉ.**

### Révision réellement discriminante

Exemple tiré de `CONG-A-alternative` :

`A : x ≡ 2 (mod 6)`, `B : x ≡ 8 (mod 12)`. L'une et l'autre prouvent `x ≡ 2 (mod 3)`. Après retrait de A, **B suffit encore**. Après retrait de B également, la conclusion devient **INDÉTERMINÉE**, et non fausse. Lorsqu'on ajoute en plus une hypothèse incompatible, le bon statut global est **INCONSISTENT_ENVIRONMENT**, et non une quelconque conclusion déduite par explosion.

Un autre exemple : `x ≡ 0 (mod 2)` réfute `x ≡ 1 (mod 2)`, mais ne démontre ni ne réfute `x ≡ 0 (mod 4)`. Cette distinction est vérifiée par les tests.

## Double calcul et traçabilité

- [GitHub Actions `43093004116`](https://github.com/Abrasax63/Omega-pub/actions/runs/43093004116) — **SUCCESS**, huit tests Python adversariaux, rejeu complet, vérificateur JavaScript indépendant et archive exacte.
- `prism/congruence_independent_crosscheck.mjs` reconstruit en JavaScript **les 276 statuts, les 276 supports actifs, les 67 contradictions et les 87 cas d'alternatives**, sans invoquer le code de CRT Python ni celui de génération des supports.
- Les contre-tests refusent : preuve fabriquée, prémisse rétractée, preuve reposant sur un ensemble impossible, identifiants inconnus, modules invalides et confusion entre réfutation et absence de preuve.
- [Registre complet des 50 états, supports et versions](https://github.com/Abrasax63/Omega-pub/actions/runs/43093004116/artifacts/13889612095). Les archives sont versionnées par numéro de révision synthétique, pas par commit externe.
- Les résultats de la suite RCE existante sont validés dans le workflow PR associé ; **ne pas prétendre qu'un nouveau moteur multi-agent ou une preuve Lean a été exécuté**.

## Limites et interprétation

1. Il s'agit de **quatre scénarios mathématiques construits par le concepteur**, non d'un holdout indépendant. La séparation calibration/test ne représente pas une indépendance structurelle ou une généralisation à des théories mathématiques inconnues.
2. Les deux calculateurs et le vérificateur indépendant utilisent le même **énoncé modulaire connu** ; le second chemin vérifie la mise en œuvre, mais pas la vérité d'une source externe.
3. Les hypothèses sont des entrées déclaratives ; rien ne vérifie l'authenticité d'un témoin, d'une publication ou d'une source. Une contradiction d'hypothèses entraîne une suspension conservatrice des conclusions globales ; des politiques plus sophistiquées pourraient raisonner en environnements alternatifs.
4. Le registre de versions enregistre les prémisses actives et leurs preuves. Il ne mesure ni latence, ni coût réel de vérification, ni contexte de langage naturel, ni capacité à découvrir une preuve.
5. ATMS est un concept classique de maintenance des justifications. Il a obtenu **strictement les mêmes résultats** que le prototype Omega. La réussite mathématique n'est **pas** une nouveauté de recherche démontrée.

## Décision scientifique

**Acquis :** conservation et révision de plusieurs justifications, refus des fausses preuves, gestion explicite des contradictions, double vérification exacte sur les 60 résidus.

**Reste à établir :** reconnaissance des hypothèses dans une documentation réelle, transformation fiable d'un énoncé naturel en proposition formelle, contrôle de provenance, choix d'une nouvelle vérification utile, coût de cette vérification et avantage face à un ATMS fort utilisant les mêmes informations.

**Prochain verrou conseillé :** une épreuve comparative sur des preuves formelles et des dépendances de théorèmes **externes**, avec un vrai vérificateur de termes de preuve, changements contradictoires de prémisses et un coût de vérification mesuré. Ne pas promouvoir la seule expérimentation construite comme supériorité scientifique.

La PR reste DRAFT empilée sur #42 ; **aucun changement de `main`, CORE ou SQLite**.
