# Protocole Work — commit scientifique
Version1.0 — instruction utilisateur du14 octobre2026. Applicable aux reprises scientifiques importantes.
Cycle obligatoire : CHARGER → RECONSTRUIRE → COMPARER → DÉTECTER LES ÉCARTS → AUDITER → FALSIFIER → COMMIT → PROPAGER → CONTRÔLER → PERSISTER → VÉRIFIER → SNAPSHOT.
Lire les index et méthodes dans /Recherche/00_INDEX_ET_METHODES, puis les sources primaires pertinentes. Un résumé/snapshot oriente la recherche mais ne prouve rien.
Distinguer DÉMONTRÉ, CALCUL EXACT, SIMULÉ, EMPIRIQUE, CONJECTURÉ, RÉFUTÉ, INDÉTERMINÉ, À RÉEXAMINER.
Comparer documents et cartes : résultats absents, obsolètes, changements de statut, corrections, liens manquants/invalides, questions déjà résolues, provenance insuffisante. La source la plus récente n'est pas automatiquement la plus fiable.
Avant promotion : énoncé exact, domaine, hypothèses, preuve/données/code, contre-tests, corrections ultérieures, provenance, dépendances et niveau réel de certification. Reconstruction ou réfutation lorsque possible. Sans vérification suffisante, garder hors noyau certifié.
Commit dans RESEARCH_MEMORY.sqlite : identifiant stable, version, énoncé, statut, domaine, hypothèses, preuves, contre-tests, sources, code/données, dates, projet, lifecycle. Les sources internes et audits de modèles ne constituent pas une validation externe.
Relations : REMPLACE, RESTREINT, REFUTE, GENERALISE, ILLUSTRE, DEPEND_DE. Une relation conceptuelle n'est jamais causale par défaut.
Réfutation/restriction : conserver la version précédente ; désactiver sa capacité de prémisse ; identifier les dépendants causaux réels ; réexaminer seulement ceux dont la justification est affectée ; journaliser raisons et propagation. Pas de rollback thématique.
Contrôler réellement intégrité, clés étrangères, références, versions, statuts contradictoires, arcs causaux dangereux, cycles, rollback, cartes/index. Les contrôles SQL ne remplacent pas un examen scientifique de contradiction.
Persister la base, les index/méthodes modifiés, l'audit, les artefacts utiles et le snapshot. Conserver l'identité Library des fichiers remplacés et un garde de version. Relire/rematérialiser les fichiers sauvegardés ; comparer contenu/hash ; refaire les contrôles sur la base persistée.
Snapshot compact par programme : résultat, certification, correction, limites, hypothèses/dependances critiques, problème ouvert, verrou et prochaine expérience. Conserver le passé à part.
Rapport final : AJOUTÉS ; MODIFIÉS ; RÉFUTÉS/REMPLACÉS ; DÉPENDANCES MODIFIÉES ; NON PROMUS et raisons ; CONTRÔLES réellement exécutés ; FICHIERS PERSISTÉS.
Priorité : conserver → signaler → auditer → seulement ensuite promouvoir.
Ne jamais déclarer une lecture, un test ou un enregistrement non effectué.
