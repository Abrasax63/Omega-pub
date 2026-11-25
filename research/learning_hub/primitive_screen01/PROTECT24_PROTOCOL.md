# PROTECT24 — comparaison neuronale bornée de la protection et du pas ordinaire

## Hypothèse et décision prospective

Demande du 25 novembre 2026 : continuer l'entraînement. Aucun changement de main, aucune API payante, aucun déploiement.

PROTECT22 (run 45679902900, artefact 15055353368) rapporte dix hausses de perte sur seize ancres pour le pas ordinaire, quatre pour le pas protégé ; sur les seize paires distinctes d'audit train, huit contre sept. Les quatre sondes protégées diminuent la perte nouvelle, sans fallback. Ce sont des diagnostics sur entraînement, pas des résultats de rétention indépendante.

La règle ROUTE23, fixée avant les résultats, appliquée au rapport complet donne PROTECTED_VS_ORDINARY_BLOCK. Le gain cumulé de perte nouvelle est 0,7607473749667406 ordinaire et 0,7548045255243778 protégé. Cette règle sélectionne une hypothèse ; l'autorisation de cet essai vient de la nouvelle demande utilisateur, pas du champ training_authorized du diagnostic.

Hypothèse falsifiable : sur un bloc court, la projection d'un déplacement AdamW contre quatre gradients de compétences anciennes réduit l'oubli observé tout en apprenant l'extraction adjacente. La faisabilité linéaire ne garantit ni la baisse réelle de toutes les pertes ni le maintien de l'exactitude.

## Préconditions et groupes

Avant chargement du modèle : tests du noyau, absence de recouvrement des prompts avec train et les fixtures antérieures recensées, contrôle des labels, détection de traces altérées, rejet d'une régression synthétique. Un petit réseau exerce ensuite les deux vrais chemins de mise à jour, un cas sans conflit et la restauration exacte.

Qwen2.5-0.5B-Instruct et tokenizer à la révision c89bee90d9f811437d9735454613c35b4a3c4dc8 ; pile CPU identique à PROTECT22. Reproduction de 128 étapes adaptatives PILOT14 : hashes de l'initialisation et du modèle gelé, sorties dev avant/après, hash des tenseurs et du fichier safetensors strictement identiques avant le nouveau bloc. Arrêt si un contrôle échoue.

Trois états comparés : checkpoint reproduit sans nouveau bloc ; 32 étapes AdamW ordinaires ; 32 étapes avec déplacement projeté. Mêmes paires d'exercices, ordre, initialisation, état optimiseur et RNG au fork. Chaque étape de chaque bras calcule les mêmes quatre gradients d'ancres anciennes choisies uniquement dans train, la même étape nouvelle et la même projection avec contrôle d'arrondi. Le contrôle ordinaire réapplique sa proposition originale exacte. Les moments AdamW suivent les propositions ordinaires dans les deux bras ; ils ne sont pas corrigés pour la projection. Les trajectoires diffèrent après la première intervention.

## Mesures et décisions

Une nouvelle cohorte publique de développement du même auteur : 256 anciennes tâches et 64 tâches d'extraction adjacente, 160 paires au total. Graine 2026112524 pour les anciennes, 2026112525 pour les nouvelles. Les gabarits et vocabulaires proviennent des générateurs existants : ce n'est pas une validation indépendante ni une absence de recouvrement sémantique garantie. Aucun examen final privé consommé. Les résultats d'évaluation ne pilotent ni le plan ni l'arrêt des branches.

Évaluer les trois états : 960 générations, plus 256 générations dev nécessaires à la reproduction, soit 1216 générations prévues. Compter les réponses strictes, les paires complètes, classes, positions, longueurs et gabarits avec les scoreurs existants. Conserver les traces question/réponse et les labels séparément. Invalides et troncatures échouent au score strict ; aucun parseur post-hoc.

Critère exploratoire historique RETENTION15 inchangé : extraction nouvelle au moins 61/64 réponses et 29/32 paires, sans régression sur aucune ancienne compétence ni nombre de paires. Rapporter aussi les deltas protégé moins ordinaire sans revendiquer de significativité sur cette unique graine. Un bras qui préserve les anciennes tâches mais n'apprend pas la nouvelle ne réussit pas. Un succès ne constitue pas une qualification indépendante ou une promotion.

128 mises à jour de reproduction et 64 nouvelles mises à jour exploratoires, pas de boucle illimitée. Restaurer exactement le checkpoint initial après chaque comparaison et en fin d'essai ; aucun poids candidat non qualifié publié. Les rapports, plans et prédictions sont conservés. L'essai ne produit pas à lui seul un nouvel état de production durable.

## Budget et arrêt

PROTECT22 rapporte environ 1584 secondes pour la reproduction et quatre sondes, sur son runner. Cet essai ajoute des gradients et évaluations ; sa durée exacte n'est pas connue. Plafond strict du job d'entraînement : 90 minutes, une tentative, pas de relance automatique. Compiler et tester hors ligne avant lancement, puis exécuter les tests neuronaux jouets avant téléchargement du checkpoint préentraîné.

Arrêt technique sur NaN, hash divergent, échec de restauration, révision incorrecte, déplacement protégé irréalisable après fallback ou traces incomplètes. Si les deux bras échouent au critère scientifique, ne pas les promouvoir ni multiplier les variantes superficielles ; conserver les résultats et réorienter vers une spécialisation par adaptateur séparé ou une nouvelle hypothèse d'objectif/données. Les autres pistes restent ouvertes. Le résultat du pilote doit être lu avant toute campagne plus longue.
