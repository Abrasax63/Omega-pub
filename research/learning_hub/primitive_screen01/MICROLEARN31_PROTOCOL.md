# MICROLEARN31 — Boucle courte sur la sélection élémentaire

Pilote exploratoire autorisé le 26 novembre 2026. Il part du modèle Qwen2.5-0.5B-Instruct initial et d'un adaptateur neuf, dans un unique runner CPU et un environnement journalisé. Il ne reconstruit pas PILOT14, n'utilise pas le checkpoint en quarantaine et ne promeut aucun poids.

Hypothèse falsifiable : quelques exemples supplémentaires, choisis dans les positions les moins bien réussies sur développement, produisent un gain de sélection vérifiable sans perdre de réponses précédemment correctes. Le témoin entraîné utilise un ordre équilibré des positions. Le modèle sans nouvelles mises à jour reste la référence initiale. Une égalité préfère le témoin fixe et ne démontre pas l'utilité du ciblage.

## Protocole gelé avant inférence

- Quatre itérations au maximum ; deux propositions par itération, quatre mises à jour chacune, depuis le même état paramètres/optimiseur/RNG.
- Cible unique : sélectionner un mot à une position donnée, parmi quatre mots.
- Développement : 8 questions cibles, une paire par position, et 12 questions de conservation (copie, appartenance, inversion). Ce lot est consommé par la sélection ; il ne sert pas d'examen final.
- Transfert final : 16 questions cibles, deux paires par position, et 12 de conservation ; vocabulaire distinct et consignes reformulées. Consulté seulement après gel du candidat. Générateur du même auteur : aucune qualification indépendante.
- Groupes entraînés : curriculum fixe [1,2,3,4] et ciblage des deux positions les moins bien réussies. Les exemples proviennent exclusivement de train.
- Même budget exact par paire : tokens d'entrée réels, cibles correctes et cibles alternatives ; mêmes séquences rembourrées à 128 positions.
- Acceptation de développement : au moins 2 réponses et 1 paire cibles de plus que l'état courant, aucune réponse de conservation précédemment correcte perdue.
- Sans candidat accepté : retour à l'état courant. Si une régression de conservation apparaît, réduire de moitié le taux d'apprentissage ; sinon changer seulement l'objectif CE / CE avec marge contrastive. Une modification par itération.
- Arrêt après deux itérations successives sans gain accepté, plafond de développement atteint, erreur technique ou budget dépassé.
- Signal final exploratoire : au moins 14/16 réponses et 7/8 paires, au moins 3/4 par position, gain d'au moins 2 réponses et 1 paire face à la référence initiale, aucune réponse de conservation initialement correcte perdue. Aucun seuil n'est modifié après observation.
- Plafonds : 32 mises à jour d'optimiseur au total, 240 générations maximum (236 dans le plan complet), 420 secondes pour le script et 10 minutes pour le job entier.
- La perte, le format, le score exact, les paires, les régressions individuelles, les décisions, les budgets et les erreurs sont séparés dans les traces.

## Reprise et confidentialité

Le module RESUME25 schéma 2 vérifie l'environnement numérique et refuse les anciens états non attestés. Les propositions non retenues sont restaurées exactement. L'état retenu, l'optimiseur, les RNG, le curseur, le contrôleur et les données sont chiffrés pour récupération privée ; seuls résultats et traces autorisées sont publiés. Le checkpoint final conserve un statut expérimental, même si un signal court passe.

La boucle ajuste les poids par gradient et sélectionne les essais selon un algorithme explicite. Elle ne démontre ni invention autonome de la méthode ni compétence mathématique générale. Le pilotage récurrent doit distinguer configuration, exécution observée, reprise privée disponible et gain scientifique vérifié. Sans chemin privé de reprise accessible au worker ou en cas d'environnement incompatible, il doit signaler le blocage, sans repartir silencieusement de zéro ni rejouer 128 mises à jour.

## Révision prospective après le premier pilote

Le run corrigé 45758787226 a exécuté deux itérations, 16 mises à jour et 100 générations. Aucun candidat n'a gagné une paire ; tous ont été rejetés. La référence stricte était 0/8 en sélection et 0/12 en conservation ; ses huit sorties de sélection étaient hors contrat. Ce résultat ne démontre pas l'absence de toute connaissance sémantique et ne rend pas le contrôle de conservation informatif.

Le commit a9f3bfa82c8a7f5200a5873cc6ecf50265c01467 ajoute, pour les futurs essais seulement, une détection explicite du format et un blocage avant entraînement si la référence de conservation est vide ou si aucune sortie de sélection ne respecte le contrat. Les traces partielles des étapes sont conservées avant la fin d'un bras. Contrôles hors modèle exécutés localement ; cette révision n'a pas encore eu de nouveau run Qwen. Les seuils et décisions du premier pilote restent inchangés.

Prochain test prioritaire : sur les questions de développement déjà consommées, comparer la consigne initiale, une consigne de sortie explicite et un conseil neutre, sans entraîner les poids et sans fournir la réponse. Geler conditions et budgets avant inférence, rapporter les tokens effectivement utilisés, score strict, paires et erreurs de sélection parmi les réponses au format valide. Ne pas ouvrir le lot final pour régler cette interface. La reprise inter-worker reste conditionnée à un état privé accessible et à l'environnement attesté ; aucune continuité cumulative n'est annoncée tant qu'elle n'est pas vérifiée.
