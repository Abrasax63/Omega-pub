# V19 — recherche de contre-exemple après une lecture hors terminaux

18 novembre 2026, vers 07 h (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, base `dd040e7d98140d70b31c61fe227b97ae68305b8a`. [Cycle précédent](OBS-V19-NONLOOP-COMPLETIONS_2026-11-18.md), [définition et sources](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/053e2f9dd7c9f8a83ef803f174cc1c8c5402378f).

Conjecture : avec deux terminaux distincts dont les images sont inconnues, une première lecture dont l’image sort de cet ensemble suffit à déterminer l’ombre globale. Hypothèses : endofonction cohérente, cycle distingué C3, horizon L=2 ou 3, support étiqueté de dix états. Critère de réfutation : deux complétions cohérentes donnant des ombres distinctes après la même première lecture. Référence fixe : demander les deux transitions terminales, budget maximal de deux transitions. L’oracle hors ligne énumère les colorations globales et ne modélise pas le coût d’acquisition.

1. Contrôle négatif : la première lecture en boucle du dossier C3 précédent doit laisser plusieurs ombres. Sur ses préfixes disjoints, fixer le côté, l’image lue hors terminaux et l’image d’un sommet non observé, puis balayer l’image de l’autre terminal. Résultat : 160 sous-lots, 150 admettent une complétion, zéro divergence dans ces sous-lots.
2. Protocole complémentaire fixé avant son balayage : 6 000 tirages de fonctions prolongeant C3, graine 1718, toutes les paires et les deux horizons. Après filtrage par cohérence et par observation admissible, balayer chaque image du terminal non lu en gardant les autres transitions fixes. Résultat : 1 881 premières lectures admissibles comptées avec multiplicité, zéro contre-exemple par cette variation. Les deux étapes sont des recherches finies. Le second balayage échantillonne les fonctions et les projections sont calculées exactement.

**EXÉCUTÉ, conjecture INDÉTERMINÉE.** Une ombre constante par sous-lot ne prouve pas qu’elle reste constante quand d’autres transitions inconnues changent simultanément. Aucun gain de lecture mesuré et aucun changement du vérificateur. Originalité bibliographique non évaluée.

Depuis research/code : `python3 audit_v19_outside_terminal.py`, `python3 audit_v19_single_read.py`, `python3 audit_v19_shadow_guard.py`. Les trois passent. Temps de l’audit : 7,997 s en local. SHA-256 du harnais `22ac33a30985eaa4ac3bc741d9da60ed9eee053b309f050cbdae44286c5de60b`.

Prochain test : regrouper les complétions par observation visible avant de comparer les ombres, en faisant varier simultanément les transitions inconnues sur un support plus petit. Prochain cycle : provenance.
