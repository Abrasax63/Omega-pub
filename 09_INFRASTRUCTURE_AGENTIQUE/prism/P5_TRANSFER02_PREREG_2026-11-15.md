# P5-TRANSFER-02 — protocole gelé avant lecture des nouveaux journaux

Date : 2026-11-15. Code et tests de l'extracteur experimental gelés au commit `2f725b3685f09220efe36e54e347f8e93286149b`. **Aucun des journaux H1–H4 ci-dessous n'a été ouvert pour l'expérience actuelle avant ce gel.**

## Question

La synthèse d'une table de signatures de transformations (« archive-pipeline » et « ninja-link »), à partir de cas historiques, permet-elle de reconnaître de nouvelles traces de même catégorie sans faux positif ? Le meilleur témoin fixe utilise **exactement le même extracteur** et les mêmes signatures autorisées ; le bénéfice spécifique de l'apprentissage ne sera reconnu que s'il surpasse ce témoin à accès égal. Un résultat identique signifie parité, non « intelligence gagnée ».

## Ensemble d'apprentissage antérieur

Extraits de journaux déjà examinés en exploration (curl/curl `f49c9c95bc31643518b86249e2a7f014699df305`) : job **C3 132705913199** (archive) et **C4 132705914296** (lien). Les libellés de ces deux opérations proviennent de la syntaxe et du script épinglé. Ces cas **ne comptent pas** au test. La correspondance est construite avant lecture des H1–H4. Les opérations non identifiées conduisent à `indéterminé`.

## Cohorte prédéfinie depuis les métadonnées GitHub (pas le contenu)

| ID | Source, run, job, nom GitHub | Cible |
| --- | --- | --- |
| H1 | [curl/curl Source 43679197664 / 132705913153 — CM integration windows-2022](https://github.com/curl/curl/actions/runs/43679197664/job/132705913153) | `source.tar.gz` |
| H2 | [curl/curl Linux 43679197809 / 132705914221 — CM mbedtls-prev](https://github.com/curl/curl/actions/runs/43679197809/job/132705914221) | `src/curl` |
| H3 | [docker/build-push-action 43583601993 / 132413316822 — provenance image](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316822) | `localhost:5000/name/app:latest` (hors domaine fichier, contrôle de non-déclenchement) |
| H4 | [docker/build-push-action 43583601993 / 132413316950 — digest docker](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316950) | `/tmp/buildx-build` (cible test négative, présence non présumée) |

Checkouts : curl/curl `f49c9c95bc31643518b86249e2a7f014699df305`; docker/build-push-action `562e51947939164e4fe808a6eab5101977e509e0`. Source épinglée curl : `tests/cmake/test.sh` pour l'archive, `src/CMakeLists.txt` pour la liaison. Deux paires de jobs corrélés : aucune affirmation de quatre reproductions indépendantes.

## Conditions de comparaison

- Comparer le candidat appris et le témoin fixe, chacun sur le **même** journal complet, **le même** script source au checkout épinglé, et les mêmes cibles.
- Un verdict `recalcul` porte sur la présence d'indices de transformation par programme, et non sur l'identité binaire, l'unicité mondiale des écrivains ou une preuve formelle.
- L'annotation de vérité opérationnelle est un audit séparé : vérifier le script et le journal, reporter toute contradiction ; pour un cas inaccessible ou ambigu : `indéterminé`, **sans remplacement de cas**.
- Score : confirmations correctes, fausses confirmations et abstentions ; zéro faux positif requis ; le gain propre exige **strictement plus de confirmations correctes** que le comparateur fixe sans augmenter les fausses confirmations. Les statistiques de ces quatre cas seront descriptives.
- Ne pas modifier les signatures ou seuils après examen des quatre journaux. Tout correctif ultérieur aura un nouveau suffixe de version et une autre cohorte gelée.
- Ni fusion dans `main`, ni nouvelle exécution GitHub Actions déclenchée, ni promotion CORE. Les tests locaux et la recherche des journaux sont séparés d'une CI effectivement attestée.

## Risques déjà connus

Le parseur est expérimental et limité à deux formes CMake ; il n'interprète pas toutes les commandes shell, ni les alias de chemin, ni les substitutions, ni les écritures cachées. Il dispose d'un garde de conflits explicites mais **pas** d'une preuve générale d'absence de seconde écriture. La vérification indépendante des octets demanderait des artefacts et des empreintes amont distincts. La syntaxe apprise ne prouve pas une amélioration du choix de stratégies face à un optimiseur classique.
