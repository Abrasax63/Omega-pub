# Omega100 — CUMULATIVE18, reproduction et rétention

25 novembre 2026, 20 h 53 CET. Branche `experiment/omega-100-2026-11-18`, départ `fd1413397febe79588553c58333f62bdb0c8a2d1`. Programme et 068 relus, 68 fiches numérotées et 069 libre. Le [run CUMULATIVE18](https://github.com/Abrasax63/Omega-pub/actions/runs/45668076345) à `d1dcfb17262a9911d22601255f4bb812ceb304e3` est terminé. Question du run : un deuxième bloc, avec ou sans répétition, permet-il d'acquérir la sélection de mots adjacents tout en préservant les compétences antérieures ?

**VÉRIFIÉ, résultat négatif sur les seuils du pilote.** Le fichier de 256 réponses du premier bloc reproduit est identique octet pour octet à l'archive du bras adaptatif PILOT14 (`878f777a96f6e74bc99e1974dde193615f7cfadd15cf205df29c5ab42f22d540`). Les manifestes rapportent aussi le même digest de l'adaptateur et 128 mises à jour. Les poids n'ont pas été recalculés. Recalcul indépendant des 1 280 sorties de rétention et transfert archivées, avec oracle direct et contrôle des empreintes des prompts. Une trace dupliquée est rejetée.

| Évaluation | Avant le bloc | Préfixe partagé | Nouveau seul | Avec répétition |
|---|---:|---:|---:|---:|
| Nouvelle tâche, exactes /64 | 2 | 14 | 31 | 25 |
| Nouvelle tâche, paires /32 | 0 | 4 | 12 | 10 |
| Appartenance, variation d'exactes /64 | 0 | −2 | −7 | −20 |

Les deux candidats finaux ont chacun 64 étapes, dont 32 partagées. Aucun n'atteint 61/64 réponses et 29/32 paires sans régression. Le plan avec répétition est moins bon que le bras nouveau seul sur la nouvelle tâche et plus régressif sur l'appartenance. La conclusion porte sur cette allocation, cette graine et cette cohorte de même auteur. Examen indépendant et rétention durable après redémarrage non testés. Référence conservée. [Seuils et code épinglés](https://github.com/Abrasax63/Omega-pub/blob/d1dcfb17262a9911d22601255f4bb812ceb304e3/research/learning_hub/primitive_screen01/retention15.py).

Audit en 0,016 s. Run archivé : 2 455,49 s. `timeout 10s python3 audit_cumulative18.py` avec artefact 15051981140 nommé next0.zip, ZIP adaptatif PILOT14 d'origine dans ../pilot14/pilot14-adaptive.zip et les générateurs retention15.py, transfer13.py au SHA du run. SHA-256 archive `194174f5c62ef93d9f5bc7e2627faf4d0c89640641ed3028c6feb343c866ba8b`, code `ea39d2e4dbf161c8a4a914652ca2749eb96763b546967183a435f3ba5af54780`, agrégats `9b4a6575aa8cc91783e5588c188155092643f0b1dbf377007565d1268e2d61d1`. Aucun corrigé publié. Cet audit porte sur CUMULATIVE18 et n'a pas consommé CUMULATIVE01.

Lectures complémentaires des agrégats vérifiés par digest Actions : [RELATION20](https://github.com/Abrasax63/Omega-pub/actions/runs/45672459372) rapporte direction 17→35/64 et paires 2→6/32, position 11→43/64 et paires 1→13/32, sous cohorte exploratoire. [PROTECT22](https://github.com/Abrasax63/Omega-pub/actions/runs/45679902900) mesure quatre pas réversibles, hausses de loss des ancres 10→4 et sur contrôle disjoint d'entraînement 8→7, zéro mise à jour conservée. Ces agrégats n'ont pas été rescorrés. [PROTECT24](https://github.com/Abrasax63/Omega-pub/actions/runs/45685909054) encore en cours au contrôle. Pas de nouvelle conclusion COPY-SFT01.

**069 NON EXÉCUTÉE — cycle sans expérience nouvelle.** Pas de moteur ni poids de base utilisables localement. A/P/B, rétention et transfert sur la cohorte vierge non mesurés. Prochain test décisif pour la rétention : comparer une seule intervention anti-régression avec nouveau seul sur une cohorte indépendante, à étapes et budgets appariés, en mesurant d'abord l'appartenance. Le test numéroté croisant ordre et étiquettes reste en attente du moteur. Aucun entraînement, coût payant ou composant supplémentaire.

Registre lu au SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`, `existing_omega100` considéré, pertinent, utilisé pour l'audit et utile pour vérifier l'échec du critère cumulatif.
