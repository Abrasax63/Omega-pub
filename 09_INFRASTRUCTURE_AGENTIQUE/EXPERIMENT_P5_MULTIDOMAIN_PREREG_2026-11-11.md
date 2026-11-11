# P5 — Pré-enregistrement : benchmark multi-domaines et contestation de provenance

**2026-11-11. EXPÉRIMENTAL / public / pas un holdout aveugle.**
Ce document est écrit AVANT la récupération des six statuts GitHub de la nouvelle cohorte. Les cas RFC et Python reposent sur des énoncés dont les règles sont publiques et connues avant le gel : aucune prétention à leur nouveauté.

## Question discriminante
La politique exacte d'Omega `optimize_policy` reste-t-elle correcte quand une observation annoncée comme officielle est falsifiée, et quand une note secondaire la contredit ? Le mécanisme actuel suppose que les observations suivent exactement les partitions fournies. Notre but est de chercher une *erreur prouvable*, pas seulement de compter des gains attendus.

## Quatre strates, six questions chacune (24)

- **GITHUB-00..05** : statut `merged` de six PR de référence, gelées ici : `python/cpython#160737`, `python/cpython#157300`, `pallets/flask#6153`, `pallets/flask#6154`, `psf/requests#7068`, `psf/requests#7413`. Vérité = `get_pr_info.merged`, seconde lecture `fetch_pr.merged`, avec SHA sauvegardé. Aucune prédiction ne doit être déduite du titre.
- **HTTP-06..11** : six prédicats sur RFC 9110, §13.1.3 et §13.1.4 (les détails de formulation sont gardés dans le fichier de données final) : priorité If-None-Match ; validité POST d'If-Modified-Since ; priorité If-Match ; validité GET de If-Modified-Since ; effet d'If-None-Match sur If-Modified-Since ; effet d'If-Unmodified-Since en présence d'If-Match. Vérité = texte normatif RFC 9110.
- **URI-12..17** : appliquer RFC 3986 §5.4.1 avec base `http://a/b/c/d;p?q` aux références `g`, `/g`, `../g`, `?y`, `../../g`, `g?y`. Vérité = résultat RFC explicite, vérification calculée séparément par `urllib.parse.urljoin` pour ces exemples normaux.
- **PYTHON-18..23** : évaluer sur Python 3 les prédicats `isinstance(True,int)`, `type(True) is int`, `issubclass(bool,int)`, `True == 1`, `(True + True) == 2`, `(True is 1)` (ce dernier serait un avertissement de syntaxe et est remplacé par `type(False) is bool` pour rendre le test reproductible). Vérité = runtime Python ; ne pas extrapoler à tous les langages.

Les notes trompeuses sont **injectées synthétiquement** : une note secondaire inversant la conclusion est ajoutée quand l'indice du cas est multiple de trois ; tous les autres cas ont une note secondaire concordante. Aucune de ces notes n'est présentée comme une citation réelle.

## Expérience adversariale gelée
Deux conditions par cas :
- **INTÈGRE** : la réponse obtenue via la source de référence est exacte.
- **USURPÉ** : pour les huit identifiants d'indice `{0,3,6,9,12,15,18,21}` (exactement deux par strate), remplacer la **réponse du contrôle primaire** par l'inverse de la vérité, tout en laissant son identifiant et son étiquette de source « officielle » inchangés. Les 16 autres cas restent intègres.

Le test ne modifie ni le texte réel du RFC, ni les dépôts externes, ni le runtime : il perturbe uniquement la couche d'observation injectée au planificateur.

## Armes et budget
- **A** : accepter la note secondaire sans contrôle ; 0 consultation.
- **B** : stratégie fixe qui consomme systématiquement **un** contrôle primaire ; au plus un appel.
- **C** : moteur Omega existant, `optimize_policy(max_depth=1, max_cost_milli=5)`, exactement le même contrôle primaire, `cost_milli=5` ; au plus un appel. Les priors et partitions fournies correspondent aux deux vérités possibles, sans observation trompeuse dans le modèle.
- **D — audit de provenance** : un second contrôle indépendant, hors modèle, compare la réponse « officielle » à la valeur primaire récupérée par un autre canal ou chemin ; si divergent, renvoie `ABSTAIN`. Deux contrôles maximum : **D a un budget supérieur** et n'est donc qu'un contrôle diagnostique, jamais une comparaison équitable de gain face à B/C.

## Mesures annoncées avant collecte
Par strate et global : exactitude stricte (une abstention n'est pas un succès), fausses certitudes, abstentions justifiées, nombre d'appels/contrôles, différentiel intègre/usurpé ; vérifier aussi la cohérence du moteur avec son objectif annoncé et le fait qu'une observation erronée puisse induire une décision fausse.

**Critère de défaillance prioritaire** : au moins une réponse confiante fausse dans la condition usurpée. Cette défaillance est plus informative qu'une simple concordance de l'optimiseur avec son oracle sur données parfaites.

## Contrôles méthodologiques
Les valeurs RFC et Python doivent être confirmées séparément de leurs notes. Les six états GitHub seront enregistrés avec URL et SHA de la PR. **Aucune évaluation par LLM ni correction humaine aveugle n'est disponible dans ce pilote.** Un vrai essai externe A/B/C/D nécessite des exécutions indépendantes de modèles et une clé de correction invisible aux systèmes testés. Ne pas annoncer de généralisation, de qualité de recherche scientifique, de gain de latence, ni de meilleure intelligence générale.

Ne pas modifier main, SQLite ou des résultats CORE. Arrêt après 24 cas × deux conditions + contrôles. 