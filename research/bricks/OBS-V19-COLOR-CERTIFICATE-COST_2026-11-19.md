# V19 — certificat global de coloration et coût complet

19 novembre2026,06h27 (Paris). **IMPLÉMENTÉ / EXÉCUTÉ : calcul fini exact ; critère de gain non satisfait.** Branche `work/omega-math-brick-pilot-2026-11-14`, départ [2c21aed9d6f6355594acf436a2e75827d3dae24f](https://github.com/Abrasax63/Omega-pub/commit/2c21aed9d6f6355594acf436a2e75827d3dae24f). Dernier [cycle mathématique](OBS-V19-DISJOINT-COHERENCE_2026-11-19.md), dernière [provenance](https://github.com/Abrasax63/Omega-pub/commit/5a0b349c8c6e219a406ebfeea1615511cab5df0f).

Définition source revérifiée : projection des colorations globalement extensibles, y compris les composantes hors cycle. L'audit #5 poursuit explicitement la propagation depuis les états encore non colorés. Sources relues et épinglées : [audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question unique : un certificat de coloration globale peut-il couvrir les composantes disjointes tout en abaissant le coût complet ? [Préenregistrement](../code/v19-color-certificate-prereg-2026-11-19.md) avant tests. Développement C4+3 états disjoints (27 applications, contrôle antérieur) ; nouvelle réserve C6+4 états disjoints (256 applications), paire(0,1), horizon2. Témoin négatif premier : fibre distante de trois états ou plus. Référence fixe `guarded_shadow`, oracle indépendant `exhaustive_shadow` sur toutes les affectations binaires.

Prototype : construire une coloration par parcours de toutes les composantes, puis vérifier n couleurs binaires et toutes les arêtes XOR avant projection. Le certificat positif contient n valeurs : il exige donc une information globale supplémentaire, et non seulement la première transition lue. Sa validation inspecte n valeurs et m contraintes (coût O(n+m) pour ces données). Un certificat absent/invalide ne prouve pas l'incohérence ; dans le pipeline testé, l'ombre vide provient de la détection de contradiction par le constructeur complet.

Critère préfixé : zéro divergence et zéro certificat falsifié accepté ; conservation active seulement si construction+validation+projection battent la référence dans les trois reprises à cas égaux. Budget283cas,<30s, aucune exécution externe.

| Jeu | Cas | Certificats positifs | Ombres vides | Tronqués rejetés | Falsifications d'arête rejetées | Divergences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C4+3 développement | 27 | 23 | 4 | 23 | 21 | 0 |
| C6+4 réserve | 256 | 191 | 65 | 191 | 177 | 0 |

Les 14 certificats positifs réservés sans arête forcée de parité1 n'ont pas de mutation d'arête de ce type ; ils sont néanmoins testés par troncature. Sur les65 systèmes incohérents réservés, le faux certificat tout-zéro est rejeté.

Coût réservé, trois reprises référence/candidat (s) : 0,013191/0,012602 ; 0,012747/0,014740 ; 0,013290/0,011342. Construction seule0,000544 s ; validation seule0,000208 s, ce dernier lot rejetant immédiatement les65 absences de certificat. Ces petits temps fluctuent : aucune supériorité stable n'est établie. Une seconde mesure instrumentée a ajouté la séparation construction/validation, sans changer les critères ni les entrées ; les deux mesures ne satisfont pas le critère de trois gains consécutifs.

Décision : référence inchangée, prototype conservé comme candidat évalué uniquement. Pas de correction active, pas de gain scientifique revendiqué. Validité constatée dans la famille finie ; aucune suffisance universelle L+1 démontrée. Originalité bibliographique non évaluée.

Non-régressions rejouées : témoin cinq états,2projections,zéro erreur du garde ; famille C5 distincte,4536projections,zéro erreur du garde. Les erreurs historiques du projecteur non gardé ne sont pas un résultat nouveau.

Depuis `research/code` :
```sh
python audit_v19_color_certificate.py
python audit_v19_shadow_guard.py
```
Harnais SHA-256 `d2cacce64102c29059a02b0f3cb1e9c066132d100d110da3d9e81971e3a2c009`. [Sorties instrumentées](v19-color-certificate-results-2026-11-19.jsonl), SHA-256 `0f48cb4d7e36b896c70cb26259191ca624825d072eacf9cdcfe1f96a20fe613d`.

Prochain test décisif : mesurer l'amortissement d'un certificat de contraintes forcées réutilisé pour plusieurs événements, en incluant son coût initial et en invalidant le cache à la moindre modification de T. Référence complète pour chaque événement. Prochain cycle alterné : provenance.
