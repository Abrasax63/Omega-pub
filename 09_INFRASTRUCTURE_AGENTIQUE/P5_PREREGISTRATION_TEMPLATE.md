# P5 — fiche de pré-enregistrement (à remplir avant génération)

**Règle :** aucune case ne peut rester implicitement supposée. Écrire une valeur vérifiable ou `NON DISPONIBLE`. Si une valeur critique est non disponible, suspendre le lancement.

## Identification et gel
- ID de campagne :
- Version du protocole :
- Version du jeu de cas :
- Branche et commit du code testé :
- Date/heure UTC du gel :
- Responsable du jeu :
- Responsable de la génération :
- Responsable de la notation :
- Empreinte SHA-256 du fichier des cas :
- Empreinte SHA-256 du corrigé privé (ne pas coller le corrigé ici) :
- Emplacement privé du corrigé et responsable d'accès :

## Modèles et paramètres
| Bras | Fournisseur | Nom exact du modèle | Snapshot/version | Paramètres (température, top-p, etc.) | Limite de sortie |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | | | | | |

- Même modèle/version pour les trois bras ? Si non, décrire et justifier :
- Identifiant de l'environnement d'exécution :
- Date de vérification des versions :

## Prompts et configuration
- Prompt système A (copie exacte ou empreinte) :
- Prompt système B (copie exacte ou empreinte) :
- Prompt système C (copie exacte ou empreinte) :
- Configuration exacte des rôles fixes B :
- Commit/configuration exacte du planificateur C :
- Contexte initial fourni à chaque bras :
- Politique de mémoire/historique :
- Sources externes autorisées :
- Outils autorisés et versions :
- Outils interdits :

## Budgets et exécution
- Budget maximal par cas et par bras (tokens/appels/coût) :
- Nombre maximal d'appels :
- Durée maximale :
- Règle en cas de dépassement :
- Règle en cas d'erreur technique :
- Données opérationnelles effectivement disponibles (tokens, coût, latence) :
- Écarts inévitables entre bras et traitement analytique :

## Randomisation et aveuglement
- Méthode de randomisation de l'ordre A/B/C :
- Graine aléatoire (conserver hors des évaluateurs) :
- Procédure de création des identifiants opaques :
- Emplacement privé de la table identifiant opaque ↔ bras :
- Confirmation qu'aucune sortie n'est visible d'un autre bras :
- Confirmation que le corrigé n'est fourni à aucun système :
- Confirmation que les évaluateurs n'ont pas accès aux bras pendant la notation :

## Évaluateurs et barème
- Évaluateur 1 (identifiant pseudonymisé) :
- Évaluateur 2 (identifiant pseudonymisé) :
- Déclaration d'indépendance / conflits d'intérêts :
- Confirmation que chaque évaluateur notera les trois sorties de chaque cas :
- Version du barème :
- Échelle 0–4 et ancrages comportementaux :
- Définition d'une erreur matérielle :
- Définition d'une affirmation non étayée :
- Définition d'un contre-exemple manqué :
- Règle d'arbitrage pré-enregistrée :

## Analyse
- Critère principal :
- Critères secondaires :
- Analyse appariée prévue :
- Gestion des données manquantes :
- Présentation des désaccords :
- Méthode d'incertitude prévue :
- Limites reconnues du nombre de cas :
- Formulations de conclusion autorisées :

## Validation avant lancement
- [ ] Cas nouveaux et non exposés dans un dépôt public.
- [ ] Corrigé conservé dans un espace privé.
- [ ] Empreintes calculées et enregistrées.
- [ ] Modèles, versions, prompts et budgets renseignés.
- [ ] Conditions de génération comparables ou écarts justifiés.
- [ ] Ordre randomisé et table d'aveuglement protégée.
- [ ] Deux évaluateurs indépendants disponibles.
- [ ] Barème et arbitrage gelés.
- [ ] Validateur v0.2 testé sur le jeu complet de notes.
- [ ] Aucune génération A/B/C n'a commencé avant le gel.

**Décision de lancement :** EN ATTENTE / AUTORISÉ / BLOQUÉ  
**Justification :**
