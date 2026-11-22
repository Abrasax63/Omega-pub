# OMEGA-LIBRARY-01 — bibliothèque mathématique incrémentale, expérimentale

**Statut : code proposé, branche isolée, aucune automatisation active, aucun changement de main.**

## Objectif

Faire évoluer la recherche documentaire autonome de la PR #230 vers une
**bibliothèque cumulative à écriture contrôlée**. Le modèle choisit le premier
concept depuis un texte de recherche *non annoté*, consulte les sources via
le même récupérateur Wikipédia de la PR #230, propose une fiche, puis choisit
une lacune suivante. Rien n'est fourni sous forme de graphe de théorèmes
prémâché ou de réponse attendue.

Chaque itération peut produire un **brouillon éducatif en quarantaine**,
pas un fait mathématique établi. C'est une première étape d'indexation autonome
et non une amélioration démontrée du raisonnement.

## Chaîne de travail

1. Texte initial brut (non annoté), choix de recherche par le même modèle
   local que la PR #230, avec le même validateur de requêtes.
2. Recherche par l'API MediaWiki à endpoint fixe (pas de navigation libre
   vers des adresses fournies par des documents), au plus deux sources par
   concept dans ce récupérateur.
3. Proposition JSON avec définition, hypothèses, relations, exemple à tester,
   falsificateur, citation verbatim, source identifiée et éventuelle prochaine
   lacune choisie **par le modèle**.
4. Contrôles *syntaxiques* (JSON, source identifiée, citation exactement dans
   l'extrait retourné), **pas de certification de sens**.
5. Enregistrement append-only d'une fiche avec URL, identifiant de page,
   révision, empreinte du texte consulté, sortie brute, statut explicite,
   chaînage SHA-256. Une recherche de même concept sur une **révision
   différente** crée un nouvel enregistrement plutôt que d'écraser le précédent.
6. Deux à trois itérations maximum par appel, sans lancement d'un serveur,
   sans coût API imposé, sans boucle infinie. La fonction est appelable plus
   tard par un orchestrateur déjà existant **après** revue.

Le fichier JSONL est une mémoire de **candidats**, pas une extension de
`scientific_memory01/verified_ledger.jsonl`. On évite ainsi toute promotion
implicite dans l'archive validée de la PR #228.

## Exécution manuelle (sur une machine qui héberge déjà le modèle local)

Depuis le dossier du module :

```bash
python incremental_math_library.py \
  --seed-file page_de_recherche_brute.txt \
  --ledger memoire_educative_candidates.jsonl \
  --server http://127.0.0.1:8080 \
  --max-hops 2
```

Le modèle local et le réseau sont nécessaires **pour une vraie recherche**.
Aucun serveur de modèle ni accès réseau n'est mis en place par ce module.
Les tests hors ligne utilisent des réponses fictives uniquement pour tester
le logiciel ; ils ne constituent pas une expérience de compréhension.

```bash
python -m unittest -v test_math_web_learning_pilot test_incremental_math_library
```

## Garde-fous et limites

- **Aucune suppression/fusion de concepts par similarité automatique.** Seuls
  les doublons exacts de concept + versions de sources sont ignorés.
- Une citation verbatim prouve uniquement une **correspondance textuelle**,
  pas une définition correcte, une conséquence logique ni une preuve.
- La vérification de SHA détecte les modifications accidentelles du registre ;
  sans signature externe ou historique Git conservé, elle ne prouve pas
  une authenticité forte face à un auteur capable de réécrire toute la chaîne.
- Aucun poids de modèle n'est modifié ; mémoire documentaire ≠ entraînement.
- Les extraits Wikipédia sont traités comme contenu non fiable. Le registre
  conserve leurs métadonnées et empreintes, pas leurs passages entiers.
  Toute republication de texte doit respecter la licence applicable et
  l'attribution Wikimedia, y compris l'historique de la révision.
- La source actuellement prise en charge est Wikipédia (contexte
  pédagogique), **pas un moteur de littérature scientifique complet**.
  Le fetch initial n'épingle pas encore l'ancien contenu lors d'un audit :
  un vérificateur de relecture des anciennes révisions reste à construire.
- Concurrence : verrou POSIX mono-fichier, pas de publication Git automatique.
  Une perte de la machine ou du fichier sans sauvegarde Git ferait perdre la
  mémoire ; persistance inter-runs à déployer séparément.

## Vérification réellement décisive avant extension

1. Exécuter **une** recherche réelle sur un nouvel extrait non utilisé dans
   les essais RAW-01/02 ou WEB-01, en conservant requêtes, sorties brutes,
   références et dépenses de jetons.
2. Vérifier que deux générations successives produisent un chaînage et que
   les deux références sont retrouvables par leurs révisions.
3. Sur de nouveaux problèmes aveugles : comparer direct / Web / Web +
   bibliothèque à budget de calcul comparable et avec corrigé tenu à part.
   Mesurer citations valides, erreurs mathématiques, abstentions, coût
   et stabilité des réponses. Un verdict négatif reste admissible.

**Critère de succès scientifique :** gain mesuré sur des problèmes nouveaux
sans hausse inacceptable des erreurs non détectées. Un registre qui grossit
sans ce gain n'est pas une amélioration du modèle.

## Réemploi de l'existant

- PR #230 : `math_web_learning_pilot.py` (choix de recherche et récupérateur).
- PR #228 : stockage de faits indépendamment vérifiés, **séparé**.
- PR #81 : laboratoire de provenance, à connecter par une revue distincte.
- PR #82 : calcul et contre-exemples finis, à connecter comme vérificateur
  d'énoncés compatibles (ne pas appliquer à toute formule arbitraire).
