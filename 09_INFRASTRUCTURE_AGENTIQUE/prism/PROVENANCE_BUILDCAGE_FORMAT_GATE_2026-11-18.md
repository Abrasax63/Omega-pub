# Provenance — le raccord hors ligne rejette le format natif Buildcage

18 novembre 2026, 20 h 45 (Paris). **EXÉCUTÉ — blocage technique reproduit ; évaluation scientifique INDÉTERMINÉE.** Branche `work/omega-provenance-lab`, départ [bad65dd](https://github.com/Abrasax63/Omega-pub/commit/bad65dd9f40bf5b2fc0af83255ec67231e58d0e5). [Dernier cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/b7b54f5cb933f4f19ea7b2d4d8c11347675aa862).

Question technique fixée avant test : le raccord peut-il lire directement les 117 événements JSONL de l’archive Buildcage, avec conservation des empreintes ? Critère de succès : produire les cas structurés depuis ce format natif. Échec : rejet explicite du format. Budget : un fichier externe déjà archivé et un contrôle local BuildKit supporté. La trace réutilisée a déjà été inventoriée dans [le cycle d’admissibilité](PROVENANCE_BUILDCAGE_ARCHIVE_GATE_2026-11-18.md). Cet essai vérifie une interface nouvelle et ne constitue pas un workflow externe inédit.

Le [catalogue du run 44095200035](https://github.com/buildcage/isolated-run/actions/runs/44095200035) confirme l’artefact 14334230388 et son SHA-256 `309128af20bae722d0812cb1a9ccd126fc2eb7f08ba387228d1ad6d190bdd8e4`. Son membre `filesystem-audit.jsonl` a l’empreinte `d3b9092834780c69d1d7278176ed196e6a3e60ecfa5148674e62947cb5f67b09`. Le manifeste technique utilise `format=buildcage-jsonl` et une sentinelle indéterminée explicitement sans vérité terrain scientifique. Aucun corrigé réservé n’est intervenu.

Résultat : un rejet `ValueError: Unsupported journal format.` pour le JSONL natif. Le contrôle BuildKit de l’archive du raccord produit un cas structuré. Deux appels au lecteur, 0,0011 s lors du dernier rejeu. Le raccord ne sait traiter que les branches `buildkit` et `bash-step` de son contrat courant. Aucune conversion du JSONL en prétendu journal Bash effectuée. Aucun candidat scientifique, comparaison à la règle fixe et métriques de provenance non mesurées. Référence conservée. Le manque de témoin indépendant de réécriture reste également à résoudre avant l’évaluation de provenance.

Archive du raccord contrôlée au SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Patch appliqué en copie temporaire après `git apply --check`. Les blobs locaux des trois modules provenance_lab, provenance_cycle et provenance_xtrace ont été comparés à ceux de la branche. Suite existante : 66/66. Pas de `propose` ou `check`, la pièce étant refusée par l’entrée du raccord.

Rejouer depuis la racine de la copie temporaire portant le raccord :
```sh
PYTHONPATH=09_INFRASTRUCTURE_AGENTIQUE/prism python \
  09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_buildcage_format.py \
  /chemin/external.zip /chemin/Omega_raccord_horaire_PR81.zip /tmp/omega-format-gate
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q
```
SHA-256 du harnais `ec084c70e094dbcbae424bde10b3b349c52cdc30834cd34ef4e7e6590a35f04b`. Manifeste technique `0e4663e337a9159957d3c99d3951ba3173ec847a26b12c1803477f5d8a624ce7`.

Prochain test de provenance : définir sur sources épinglées le contrat des événements Buildcage (opération, succès, processus, chemin, complétude) et tester un adaptateur sur des contrôles indépendants avant d’exposer une réserve externe. Prochain cycle alterné : mathématique.
