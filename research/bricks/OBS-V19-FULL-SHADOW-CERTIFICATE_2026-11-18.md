# V19 — certificat de graphe pour une ombre complète

18 novembre 2026, 22 h 00 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [b7b54f5](https://github.com/Abrasax63/Omega-pub/commit/b7b54f5cb933f4f19ea7b2d4d8c11347675aa862), [dernier calcul](OBS-V19-FREE-DESTINATION_2026-11-18.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/e356af5fe37c78fd338d6781b4cb08e734b986a7).

L’ombre projette les solutions de toutes les contraintes globales sur les variables du cycle. Sources : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question fixée avant test : la cohérence du graphe XOR et la présence d’au plus une variable du cycle par composante suffisent-elles à expliquer l’ombre complète ? Hypothèses : variables binaires libres, seules contraintes de parité entre paires, projection sur des variables distinctes du cycle. Référence fixe : toutes les affectations binaires de l’espace entier. Critère : zéro certificat accepté à tort, zéro désaccord sur les familles annoncées, coût de vérification inférieur à l’oracle. Budget identique de complétions pour les deux méthodes. Avant les familles, trois témoins indépendants : contradiction XOR, composante joignant deux variables projetées, composantes séparées cohérentes.

**Preuve élémentaire du critère.** Dans une composante cohérente, choisir la couleur d’une variable fixe toutes les autres par propagation des parités. Une composante sans variable projetée admet une solution. Une composante avec une seule variable projetée permet ses deux valeurs. Les composantes sont indépendantes : toute coloration des variables projetées s’étend alors globalement. Réciproquement, une contradiction empêche toute solution, et deux variables projetées d’une même composante ont une parité imposée ; toutes leurs colorations ne peuvent donc s’étendre. Le critère caractérise ainsi l’ombre complète pour ce contrat de contraintes. Originalité bibliographique non évaluée.

| Famille | Complétions cohérentes | Certificats complets | Faux accords / rejets | Certificat | Oracle |
| --- | ---: | ---: | ---: | ---: | ---: |
| C4, horizon 3, un état libre | 316 | 316 | 0 / 0 | 0,001878 s | 1,410828 s |
| Réserve distincte C5, horizon 2, un état libre | 268 | 268 | 0 / 0 | 0,002951 s | 0,607463 s |

Les 338 affectations initiales C4 et 288 C5 ont été filtrées par cohérence. Les trois contrôles passent. **VÉRIFIÉ sur le domaine annoncé, certificat expérimental conservé.** Gain mesuré de calcul sur le prédicat « ombre complète ». Un lot chronométré par méthode. Les entrées sont identiques et l’acquisition des transitions n’est pas comprise dans le coût. Cette fonction ne renvoie pas l’ombre partielle quand le certificat échoue ; cette tâche reste au projecteur existant. Aucune promotion canonique.

Le garde historique concorde à nouveau avec l’oracle sur les 2 projections du témoin à cinq états et les 4 536 de la famille C5 distincte. Le test de lecture simple passe. La conjecture générale sur une seule lecture reste indéterminée.

Rejouer depuis `research/code` : `python audit_v19_free_certificate.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du harnais/certificat `0e3d9cf6768222e548bbebb1f4970a8167a0de6613f74938a328f12a7b09bf3e`.

Prochain test mathématique : C4, horizon 2, deux états libres, rechercher une complétion où le certificat échoue puis comparer les ombres dans les groupes partageant la même première lecture. Prochain cycle alterné : provenance.
