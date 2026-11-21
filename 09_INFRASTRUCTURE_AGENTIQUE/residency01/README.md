# RESIDENCY-01 — un seul modèle local résident, RAM et provenance vérifiées

Prototype expérimental de chargement sélectif des **poids déjà disponibles localement**, conçu pour éviter de maintenir les modèles 0,5B et 3B simultanément en RAM. Cela **n'augmente pas** la taille du plus gros modèle qui rentre individuellement dans la mémoire.

## Contrat

`ModelProfile.from_scale_report(report,path)` exige un rapport **réel** `SCALE01` terminé, deux pics RSS du serveur observés sous cache OFF/ON, un modèle et moteur épinglés, des sorties Reader18 appariées et une taille de fichier non vide. Le rapport n'est pas signé cryptographiquement : son intégrité relève de la chaîne GitHub Actions et de l'approvisionnement des artefacts.

`SingleResidentGovernor(backend,budget_kib,reserve_kib)` : avant chaque chargement, la taille et le SHA256 du fichier local sont contrôlés, et `peak_RSS + marge` doivent rentrer dans le budget explicitement fixé. Le gestionnaire n'invente pas un modèle de secours de moindre qualité, refuse tout profil non mesuré, et arrête intégralement le modèle précédent avant de lancer le suivant.

`LocalLlamaBackend(server_binary)` : pilote une instance **localhost** de llama-server. Le processus est explicitement arrêté lors d'un changement. **Pas de transfert du KV cache entre modèles**. La chaîne de compilation du binaire llama.cpp doit être vérifiée indépendamment ; le simple SHA de commit déclaré dans un fichier ne prouve pas l'identité d'un exécutable local.

Ce module ne modifie pas le texte produit par les modèles et n'active **aucun cache LLM par défaut**. Les gardes de provenance et de vérité sont extérieurs et restent obligatoires.

## Exemple minimal (uniquement sur machine avec deux poids locaux vérifiés)

```python
import json
from pathlib import Path
from single_resident import ModelProfile, LocalLlamaBackend, SingleResidentGovernor

report=json.loads(Path("scale01-3b-report.json").read_text())
profile=ModelProfile.from_scale_report(report,Path("/modeles/qwen3b-pinned.gguf"))

governor=SingleResidentGovernor(
    LocalLlamaBackend(Path("/opt/pinned-llama-server"),port=8129),
    budget_kib=6*1024*1024,
    reserve_kib=512*1024,
)
try:
    governor.activate(profile)
    # Un seul modèle tourne sur 127.0.0.1:8129. Les requêtes scientifiques
    # et leurs vérifications restent au pipeline du lecteur, pas à ce module.
finally:
    governor.release()
```

Ceci ne garantit pas qu'un modèle va charger sur une machine différente des runners de mesure. L'absence de mémoire libre, un modèle déjà servi ailleurs ou des buffers additionnels peuvent provoquer l'échec du chargement. Éviter les usages concurrentiels non orchestrés.

## Validation et limites

[CI RESIDENCY01](https://github.com/Abrasax63/Omega-pub/actions/workflows/omega-residency01.yml) : tests d'empreinte de fichiers temporairement construits, faux rapports, mémoire insuffisante, refus de downgrade, processus simulé et échecs de transition. **Les tests ne chargent pas les modèles réels et ne mesurent pas les transitions sur matériel**.

Une exécution de basculement 0,5B↔3B sur le **même runner**, avec mesure RAM et régression sur les sorties, reste nécessaire avant activation dans Omega. Pas d'API payante, pas de téléchargement de 7B/14B, pas de changement de `main`.
