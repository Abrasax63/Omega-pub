# SEM22 — vérification mathématique indépendante et filtrage des propositions d'Omega

**Préenregistrement avant constitution du corpus, implémentation et inférence (2026-11-19).**

## Problème
Les expériences BENCH19/20/21 ont amélioré la présentation des réponses et éprouvé le décodage contraint, sans établir un meilleur raisonnement mathématique. Examiner une autre architecture : un *interpréteur mathématique spécialisé* relit la définition et les propositions directement dans le document d'origine, calcule une preuve exhaustive sur un ensemble fini et sépare VRAI, FAUX et INDÉTERMINÉ. Le modèle reste un proposeur non fiable et n'a pas accès aux réponses de l'oracle.

## Hypothèse et mesure
- Produire **24 nouvelles fiches mathématiques**, différentes des BF, CF et GF antérieures : 12 fonctions affines et 12 quadratiques de Z/nZ vers lui-même, sept prédicats par fiche.
- Prédicats supportés par le vérificateur : injectivité, surjectivité, existence d'un point fixe, involution, cardinal de l'image, nombre de points fixes, valeur f(f(0)). Écriture française standardisée. **168 propositions**.
- Les 24 définitions et 168 énoncés, leurs paramètres, leur ordre et leur masque de vérité sont figés avant les réponses des LLM. Une énumération arithmétique **hors du vérificateur** produit le corrigé préalablement enregistré (sans LLM). Aucun label de vérité n'est transmis aux modèles.
- L'évaluateur **parse uniquement le document brut**, pas le manifeste de vérités. Parseur strict avec ancrage complet, sans interprétation spéculative ni réparation silencieuse ; seules les sept formulations acceptées reçoivent VRAI ou FAUX. Toute formule, proposition ou notation inconnue produit INDÉTERMINÉ, sans statut de preuve ou publication.
- Pour VRAI ou FAUX, joindre une trace vérifiable d'énumération des éléments de Z/nZ (et si FAUX, un contre-exemple quand possible) ; les témoins et la table doivent permettre de **recalculer** les verdicts.
- Liaison au blob Git exact, puis Reader12 gate pour tout résultat source sélectionné. Ne jamais convertir une citation conforme en certification, règle Horn ou preuve formelle externe.

## Expérience à trois étages
1. **Modèle seul** : Qwen2.5-0.5B-Instruct ou 3B-Instruct sélectionne au plus 3 indices 1..7 ; traduire en lignes sources 9..15 ; parseur strict sans réparation.
2. **Modèle + vérificateur** : mêmes indices, mais toute proposition classée FAUSSE ou INDÉTERMINÉE est écartée. L'information manquante n'est pas ajoutée : mesurer TP, FP, FN, F1, nombre de propositions fausses écartées et fraction non vérifiable.
3. **Vérificateur en lecture complète** : examiner les sept propositions, signaler toutes celles vérifiées VRAIES, les FAUSSES et les INDÉTERMINÉES, **sans modèle**. Mesurer séparément la précision et le rappel de ce domaine *fermément délimité*, sans attribuer les bonnes réponses au LLM.
- Références : `first3`, `NONE`; `all7` couverture seulement. Comparer coût CPU inférence et coût du vérificateur.
- Succès intégration local : 168/168 verdicts sur les expressions supportées concordent avec l'oracle gelé, absence de faux `TRUE` sur contrôles contradictoires, aucune promotion automatique, et au moins un faux positif réellement supprimé des réponses de modèles. Si modèle n'en produit aucun, critère FP supprimé = non établi.
- Exiger 24/24 cas complets, 48 générations réelles au maximum (24 par modèle), un seul appel par fiche et modèle, et aucune API payante ; ne pas modifier a posteriori les cas.
- **20+ contrôles adversariaux** hors du holdout (chaînes non supportées, extra texte, injections, source modifiée, mapping hors plage, collisions, limites) : aucun ne doit provoquer de VRAI inventé. Le nombre exact et les énoncés sont pré-enregistrés dans la suite de tests avant le premier run.
- 11 tests plus contrôle adversarial à augmenter si nécessaire. Test CI CPU réel, mêmes Qwen2.5 Instruct Q4_K_M épinglés, même commit llama.cpp que BENCH21, température 0 et max 64 tokens.

## Limites
Ce n'est pas un solveur mathématique universel ni de l'apprentissage du modèle. On intègre une capacité symbolique **exacte dans un langage délimité** et un refus honnête hors langage. Concordance avec un oracle algorithmique ne fournit pas d'annotation humaine indépendante ni une preuve de compréhension de publications scientifiques réelles. Ne pas appeler « autonomie », « AGI », « modèle frontière » ou « intelligence générale ». L'effet causal peut se mesurer sur le même corpus à réponses du modèle identiques (filtrage seulement). Ne pas comparer directement des scores inter-BENCH.

## Sûreté
Aucun secret, aucun service payant, pas d'accès web dans le composant. Branches expérimentales et PR DRAFT empilées, aucune fusion ni modification de main, des PR #203/#204/#206 et des travaux historiques.
