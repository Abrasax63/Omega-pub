# V19 — reconstruction depuis les seuls préfixes
17 novembre 2026. Base `d9211bd1d52d06f742fd99c2b57b9d2455a2060f`. Question : les deux préfixes jusqu’à L+1 et le cycle suffisent-ils au calcul effectif ? Le candidat reconstruit les arêtes sur les sommets d’image connue, puis projette avec le garde existant. L’oracle exhaustif seul reçoit le système complet pour calculer l’ombre de référence.

Le témoin précédent exige une observation supplémentaire à L. À L+1, le candidat retrouve les deux ombres, de tailles 0 et 8. Une première implémentation échouait sur les deux points fixes : elle reconnaissait les échanges mais omettait l’invariance d’une paire fixe. La correction compare les ensembles d’images.

Famille distincte : C4 et C3 disjoints, deux feuilles vers les sommets périodiques, contraintes forcées cohérentes, toutes les paires et L dans {2,3,4}. Résultat calculé : 0 écart sur 4 536 cas, dont 588 ombres vides. Durées locales cumulées sur un passage : 0,124 s pour reconstruire et projeter, 1,132 s pour projeter exhaustivement à partir des contraintes complètes. Mesure indicative, hors préparation des données pour les deux méthodes. Le domaine testé suppose la cohérence globale des contraintes forcées. Originalité bibliographique non évaluée.

Rejouer depuis research/code : `python3 audit_v19_reconstruct_prefix.py`. SHA-256 `168133bd17a6d2e352779b10b82f86464a9c16394ac42edb57d7789c5b29c99e`. Prochain test : distinguer, à L, les cas déjà décidables de ceux qui exigent réellement une observation supplémentaire.
