# OMEGA-READER13 — préenregistrement (figé avant consultation des textes réservés)
Date: 2026-11-18. Branche: `experiment/omega-reader13-real-small-model-2026-11-18`, empilée sur #179. Aucun changement de main, aucune API payante ni secret.
## Question
Un vrai petit modèle extracteur apporte-t-il une meilleure fidélité sémantique qu'une extraction déterministe, à textes et filtres identiques ? Aucune preuve mathématique ne sera certifiée.
## Cohorte choisie à l'aveugle par les noms de fichiers et la taille (avant ouverture)
Source Git immuable: commit main `0ca3c5f63998cf16cc84478c7735c03445a08669` (arbre inspecté pour noms et hachages seulement).
A: `02_MATHEMATIQUES/temps_regle90/BR-R90-01_NOYAUX_PERIODES.md`, blob `478ca7c518ed1368a0bf35deb5f9be160bba581d`, 2400 octets.
B: `02_MATHEMATIQUES/temps_regle90/BR-R90-02_MAJORITY_WALSH.md`, blob `0a9f6bab0b91a93f8fcc831c39a988171c169eb5`, 2475 octets.
Ni A ni B n'appartiennent aux holdouts V8/DELTA déjà exposés de #177/#179. *Absence totale d'exposition dans tout le projet non garantie.*
## Modèle et témoin
Un seul petit modèle ouvert: `Qwen/Qwen2.5-0.5B-Instruct` (Transformers, CPU GitHub Actions, poids téléchargés sans clé; fichier de révision exacte et versions dans le rapport). Température 0, un appel par source avec 10 paquets maximum, sortie JSON; 700 nouveaux jetons max pour chaque source. Aucun fallback déguisé en vraie génération. Témoin sans modèle: extraction mécanique de citations suivant motif de phrase; mêmes sources, même limite de 10 paquets, même gate de #179. Zéro auto-certification.
## Tests et critères
- Tests de non-régression existants et nouveaux; blobs Git et citations exactes; rien hors QUARANTINE; aucun effet main/RCE/Horn.
- Enregistrement brut des deux sorties modèle et des deux sorties du témoin; acceptées/rejetées, motifs, temps CPU, versions, SHA du modèle, longueurs d'entrée et sortie.
- La seule vérification automatisable de fidélité est *littérale* (citations). Une annotation de référence écrite et gelée AVANT de voir les sorties du modèle pourra comparer l'identification de conclusions et hypothèses, mais reste provisoire sans évaluateur réellement indépendant.
- Distinction entre erreur JSON, absence de proposition, hallucination de citation, dégradation du filtre, sortie correcte et vraie découverte.
- Aucun critère de compréhension revendiqué sans comparaison sémantique indépendante; un run CI vert ne suffit pas.
## Verrous et abstention
Un runner sans réseau HF ou sans ressources signale INDETERMINATE_INFRA au lieu de feindre un succès. Les deux textes réservés pourront être relus pour annoter leur référence uniquement APRÈS ce commit de préenregistrement. Échantillon de deux seulement: exploration, pas conclusion statistique.
