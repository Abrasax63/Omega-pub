# Omega100 — audit des consignes minimales RELIABILITY02

25 novembre 2026, 17 h 29 CET. Branche `experiment/omega-100-2026-11-18`, départ `2047a7b91ac15535617b821aa6a2ebb740df7f79`. Programme et 068 relus, 68 fiches et 069 libre. Question du run préexistant : une consigne minimale améliore-t-elle les quatre opérations de lecture de Qwen2.5-0.5B-Instruct, révision `c89bee90d9f811437d9735454613c35b4a3c4dc8`, sans dégrader l'inversion ? Référence : consigne originale sur les mêmes cas. Seuils du [code épinglé](https://github.com/Abrasax63/Omega-pub/blob/7af15509e3d0f5da8937c2e96ac00c947d5cae3e/research/learning_hub/primitive_screen01/reliability02.py) : 48/64 dans chaque opération, 20/32 par classe et par paires pour l'appartenance, +8 réponses exactes sur deux des trois opérations cibles, perte d'au plus trois sur l'inversion.

**VÉRIFIÉ — hypothèse du run réfutée.** Recalcul indépendant à partir des 512 sorties, des questions et d'un oracle par opération, avec couverture et empreintes de prompts vérifiées. Une sortie manquante ou dupliquée invalide la trace. Les deux conditions de formulation sont appariées sur 256 cas synthétiques et sont issues du même auteur.

| Opération | Original exact / normalisé | Minimal exact / normalisé | Format invalide original → minimal |
|---|---:|---:|---:|
| Copie | 43 / 43 | 13 / 13 | 21 → 51 |
| Sélection | 9 / 9 | 8 / 8 | 27 → 28 |
| Appartenance | 0 / 45 | 0 / 18 | 1 → 34 |
| Inversion | 62 / 62 | 58 / 58 | 1 → 3 |

Chaque bras contient 64 cas par opération. En appartenance, les bonnes réponses normalisées « Yes » et « No » sont 18/32 et 27/32 pour l'original, puis 3/32 et 15/32 pour le minimal. Les paires entièrement réussies passent de 14/32 à 0/32. La normalisation autorisée retire les blancs aux bords et un point final. Le score strict compte 0/64 dans les deux bras. La forme minimale a changé plusieurs éléments de la consigne, donc le recul ne peut être attribué exclusivement à sa longueur. Référence conservée. [Run RELIABILITY02](https://github.com/Abrasax63/Omega-pub/actions/runs/45647049169).

Lecture des agrégats complémentaires, ZIP vérifiés contre le digest Actions : [POSITION03](https://github.com/Abrasax63/Omega-pub/actions/runs/45652065395), copie de contrôle 55/64 et 24/32 paires, position ordinale 11/64 et 0/32 paires, deux formats avec étiquettes 0/64 valides. [PRIMITIVES01](https://github.com/Abrasax63/Omega-pub/actions/runs/45642125410), aucun des deux petits modèles n'a passé tous les seuils, SmolLM2 à 1/64 pour l'appartenance et Qwen à 0/64 (score strict). Ces deux agrégats n'ont pas été recalculés depuis les sorties.

`timeout 10s python3 audit_reliability02.py`, 0,013 s local. Archives Actions d'origine à nommer rel0.zip (15038530848), rel1.zip (15038450980), rel2.zip (15037169150), run2.zip (15038023415). SHA-256 dans les agrégats. Code `1d2030d0a73fe04da7aae3413ea94451d68c95b3201b432eec701b9a3f45cd90`, agrégats `c4e7d07a792a78d341dd525adcd145a3aeb96a8619af4fb97db23b63f583979f`. Run antérieur : 465,09 s d'inférence cumulée, 23 105 tokens d'entrée et 2 839 de sortie. Aucun coût payant ni publication de corrigés lors de l'audit. Le verdict COPY-SFT01 demeure dans son audit antérieur, sans nouvelle alerte.

**069 NON EXÉCUTÉE — cycle sans expérience nouvelle.** Aucun moteur ni poids de base utilisable trouvé localement. A/P/B, rétention, transfert et régressions d'une cohorte vierge non mesurés. Le prochain test demeure l'appartenance isolée avec ordre et étiquettes croisés sur cas nouveaux. La consigne originale doit servir de référence forte, avec forme de consigne et correcteur de sortie contrôlés séparément. Aucun test numéroté supplémentaire à engager avant de disposer de ce moteur.

Registre lu et SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`. `existing_omega100` considéré, pertinent, exécuté pour l'audit, utile pour confirmer la régression liée à la formulation. Aucun nouveau composant utilisé.
