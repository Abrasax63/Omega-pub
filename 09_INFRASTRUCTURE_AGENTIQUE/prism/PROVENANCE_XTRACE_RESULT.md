# Essai sur des journaux GitHub Actions

Run 43480869950, jobs build 132076679364 et reserved 132076679324. Les cinq fichiers ont la même empreinte SHA-256. Le premier run a détecté des octets différents dus à un échappement de fin de ligne ; le run retenu a été produit après correction.

Lancer provenance_xtrace.py avec les deux journaux bruts dans l’ordre build, reserved. Le candidat est construit sur deux traces annotées puis évalué sur trois sorties distinctes du même workflow. Sur ces trois sorties, la règle fixe qui lit la même trace et le candidat donnent chacun une copie, un recalcul et une abstention attendue. Aucun gain sur la règle fixe. La règle à marqueurs explicites de la PR #79 s’abstient sur ce format.

Les deux comparateurs partagent un extracteur écrit pour ce corpus. Le comparateur fixe connaît l’expression exacte du fixture. L’essai est contrôlé, avec une collecte des journaux opérée dans la session, et ne valide ni un nouveau format externe ni une amélioration autonome inter-cycle. Le candidat basé sur les préfixes peut confondre deux programmes ayant le même préfixe.
