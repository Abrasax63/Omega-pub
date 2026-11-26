# V19 — décider un noyau à quatre égalités par son cycle signé

19 novembre 2026, 16 h 22 (Paris). **EXÉCUTÉ / VÉRIFIÉ pour le verdict ; gain de coût dépendant de la famille.** Branche `work/omega-math-brick-pilot-2026-11-14`, SHA initial `106134c049a6ca80940fab21db797fa896468bf0`. Suite du [minimum à cinq états](OBS-V19-PIVOT-MINIMUM_2026-11-19.md), après le [cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/7a38095338f07af879cfe470495a40085ad1a914).

L'ombre retient les colorations du cycle qui s'étendent à un système global cohérent. Sources relues et épinglées : [audit L+1](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur PR #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [code PR #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/research/code/test_v19_locality_l_plus_1.py). Le garde existant donne zéro divergence face au projecteur exhaustif pour les 2 projections du témoin historique et les 4 536 projections de la famille C5 de non-régression. Voir [rejeu](../code/v19-signed-core-guard.txt).

[Protocole](../code/v19-signed-core-protocol.md) fixé avant test. Pour F cohérent et quatre relations d'événement, le candidat décide uniquement l'incohérence minimale par suppression. Il accumule les degrés et les signes une fois F quotienté, sans lancer de projection ni trier les requêtes. Référence fixe : filtre du cycle simple non signé du pilote précédent, puis cinq projections exhaustives sur les survivants. Oracle indépendant : cinq projections sans filtre. Le contrôle C4 pur est négatif et le témoin à cinq états du pilote est positif pour les deux méthodes.

Justification : un représentant par composante de F transforme les quatre égalités en arêtes XOR signées. Toute incohérence implique un cycle de signe impair, par exemple l'arête qui contredit la parité propagée le long d'un arbre couvrant et le chemin qui la ferme. Si la contradiction est minimale à quatre arêtes, ce cycle utilise les quatre. Avec quatre arêtes, il est simple et comporte quatre sommets distincts. Réciproquement un cycle simple de signe impair est incohérent, tandis que la suppression d'une de ses arêtes donne un chemin cohérent. C'est une preuve du critère, avec l'hypothèse F cohérent. Le verdict ne fournit pas la projection entière.

| Campagne | Requêtes | Noyaux positifs | Erreurs fixe / signé | Projections fixe / signé | Temps fixe / signé |
| --- | ---: | ---: | ---: | ---: | ---: |
| Réserve principale, q=5 et 6 | 11 117 | 0 | 0 / 0 | 0 / 0 | 101,37 / 241,68 ms |
| Réserve supplémentaire, C4 et C2 distincts | 1 526 | 112 | 0 / 0 | 1 760 / 0 | 225,12 / 11,65 ms |

Après la campagne principale sans positif, un [contrôle supplémentaire](../code/v19-signed-core-power-protocol.md) a été fixé avant son balayage, sans modifier le candidat. Sur les deux campagnes, l'oracle fait 63 215 projections. Le temps de la référence et du candidat comprend leur filtre ou quotient respectif, hors oracle de notation. Les temps sont ponctuels, pas une mesure de débit stabilisée. Les 112 positifs sont des requêtes du lot fini, pas des découvertes distinctes.

**Décision :** conserver le filtre fixe comme référence générale. La réduction du temps et des appels est mesurée sur le lot où le filtre laisse des survivants. La réserve principale réfute une amélioration générale de coût pour ce candidat tel quel. Le [candidat](../code/signed_core.py) et les mesures sont conservés pour étude. Aucune revendication bibliographique. Prochain essai : réutiliser le quotient non signé du filtre pour ne calculer les potentiels signés que sur les requêtes survivantes, puis tester le coût total et les erreurs sur de nouvelles familles. Prochain cycle alterné : provenance.

```sh
cd research/code
timeout 30 python signed_core.py
timeout 30 python signed_power.py
timeout 30 python audit_v19_shadow_guard.py
```

Reproduction : le harnais importe `pivot`, nom local de `audit_v19_pivot.py`. Le copier avec ses dépendances dans un dossier temporaire avant les commandes, ou y renommer la copie en `pivot.py`. Empreintes SHA-256 : harnais `df3328f587113d47b65bf2748ede0c023eaf9270a62307f9aefa1a4f0d38a4d9`, [réserve principale](../code/v19-signed-core-results.jsonl) `668c534bab5a118b28ca11d3da2ebe52f25925b2915e7c4ad37ab737a0d71ff3`, [complément](../code/v19-signed-core-power.json) `513e20a055e22626e0bfed162db5a59d8af1b6d950a18c6ebac29fa35c112edd`.
