# V19 — valeur d’une seule transition

17 novembre 2026. Base `1305dba2b61615ea73583a08edbab6b94aa3682d`. Rejeu diagnostique des 70 reports du [pilote adaptatif](OBS-V19-ADAPTIVE-PREFIX_2026-11-17.md), sur la même famille. Référence : ombre exhaustive et demande groupée des deux transitions. Le même certificat est appliqué après lecture de chaque côté séparément, puis après lecture des deux. Toute décision doit égaler exactement l’ombre de référence.

Résultat : gauche seule 0, droite seule 70, chacune séparément 0, aucune seule 0, transitions partagées 0. Les 70 inversions de l’ordre des trajectoires inversent le côté suffisant. Dans chaque report, l’autre transition est déjà connue grâce au cycle ou aux préfixes. Sur les deux témoins d’ambiguïté antérieurs, les images terminales sont distinctes et inconnues, et le certificat attend les deux transitions. Cela ne prouve pas qu’aucun autre certificat ne pourrait conclure plus tôt.

Sur ces 70 cas, les deux demandes naïves représentent 140 transitions, contre 70 lectures nouvelles si on consulte d’abord les données déjà connues. Un comparateur groupé qui fait cette même consultation obtient également 70 lectures et 70 allers-retours. Aucun avantage propre à un ordre appris n’est établi sur ce lot.

Depuis research/code : `python3 audit_v19_single_read.py` et `python3 audit_v19_adaptive_prefix.py`, réussis localement. SHA-256 du harnais `d4626cb53331e8f5eddbebed0b32882b4662b1b780a38b83da2e10e130409a95`. Aucun changement du vérificateur. Prochain test : réserver une famille avec deux images terminales réellement inconnues et chercher si une seule lecture suffit parfois au certificat.
