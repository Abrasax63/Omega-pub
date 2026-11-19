# DUAL25 — indépendance de formalisation, consensus prudent et revue humaine

Préenregistrement le **19 novembre 2026**, gelé **avant le développement du second formaliseur et les évaluations**. Branche expérimentale issue de TYPED24 #209 ; aucune fusion ni modification de `main`.

## Question falsifiable
Deux chemins **algorithmiquement distincts** peuvent-ils produire la même représentation de fonctions finies à partir du même document, avec une conservation explicite des désaccords et des ambiguïtés, sans favoriser l'apparence d'un consensus ?

## Architecture
- Formaliseur **A :** `typed24/adapter.py`, existant et immuable, basé sur motifs de phrases et parseur source, dont les représentations typées peuvent être multi-valuées.
- Formaliseur **B :** nouveau **lexeur / analyseur grammatical séquentiel autonome**, sans import d'A ni réutilisation de ses expressions régulières, sur les mêmes documents. Les deux réutilisent **seulement** le contrôleur d'identité de source Reader12 et le calcul exact SEM22 comme base de confiance partagée ; **ils ne sont pas indépendants par auteur ni par données**, donc le consensus n'est pas une validation humaine.
- Le rapprochement compare le domaine, codomaine, type de fonction, coefficients, quantificateur et type de prédicat — **pas uniquement** le booléen calculé pour un exemple.
- Toute divergence, toute pluralité de lectures, source altérée, phrase incomplète ou hors type => **WITHHELD / ABSTAIN**, jamais certification ni règle Horn. Conserver les lectures alternatives pour exploration et revue humaine.
- Détecter un **contre-témoin de non-équivalence** par exploration finie quand des interprétations ont les mêmes réponses sur le problème courant. La recherche peut établir une divergence par un exemple concret ; **aucun contre-exemple trouvé n'est jamais preuve d'équivalence générale**.
- **A et B identiques** sur un cas ne démontre pas qu'ils ont compris l'intention de l'auteur. Étiqueter les cas `AGREED_LOCAL_CONTRACT_AWAITING_HUMAN_REVIEW`, pas `SEMANTICALLY_CERTIFIED`.

## Cohortes (aucun nouveau score récupéré de l'ancien résultat)
- **24 cas TYPED24 préexistants**, gelés avant notre B, adaptés aux tests de contrat ; ils **ne sont pas un nouveau holdout**, et leur distribution a déjà servi à concevoir A.
- **6 courts extraits externes HU01–HU06** préexistants (TYPED24), ainsi que 12 anciens EXT23 ; contrôles négatifs de refus, jamais appelés nouveaux holdouts. Aucun verdict de fidélité humaine sur ces textes.
- **Revue humaine indépendante** : produire un paquet de textes **sans les verdicts attendus et sans les propositions de A/B**, contenant source, domaine/codomaine et questions ouvertes à renseigner. L'annotateur devra travailler sur des **textes complets nouveaux** et fournir une interprétation typée avec justifications et éventuelles ambiguïtés. Tant que ce jeu n'existe pas, statut `PENDING_INDEPENDENT_HUMAN_GOLD`, et aucune mesure de fidélité réelle n'est permise.
- Les expériences de revue ne pourront être incorporées à la métrique qu'après préenregistrement de l'annotation et preuve de provenance, sans modification des attentes a posteriori.

## Critères
- Contrôles : 24/24 documents retrouvés par empreinte Git ; 168/168 énoncés SEM22 inchangés ; 6/6+12/12 extérieurs non soutenus => abstention ; zéro promotion.
- Indicateurs publiés : accords structuraux A/B (avec dénominateur), conflits, abstentions, ambiguïtés, contre-exemples d'interprétation, latences, taux de couverture des **contrats normalisés uniquement**, et **annotation humaine : ABSENTE** tant que vraie revue.
- Un 100 % d'accord A/B ne saurait être appelé fidélité au langage naturel. Une divergence n'est pas preuve qu'un des formaliseurs a raison. Jamais de décision prise par vote seul.
- Tests adversariaux : modifications d'empreinte, proposition B inventée, lien vers autre ligne, paraphrases hors langage, quantificateurs contraires, consensus de vérité malgré AST différente, doublons, injection de consigne.

## Références publiques
- Li et al. (NeurIPS 2024), *Autoformalize Mathematical Statements by Symbolic Equivalence and Semantic Consistency* : https://proceedings.neurips.cc/paper_files/paper/2024/hash/6034a661584af6c28fd97a6f23e56c0a-Abstract-Conference.html
- Poiroux et al. (EMNLP 2025), *Reliable Evaluation and Benchmarks for Statement Autoformalization* : https://aclanthology.org/2025.emnlp-main.907/
- Zhang et al. (2026), *Beyond Compilation: Evaluating Faithful Natural-Language-to-Lean Statement Formalization* : https://arxiv.org/abs/2606.31002

Objectif scientifique à court terme : **coupler sûreté formelle et fidélité à la source** sans confondre les deux ; traiter les lectures minoritaires comme hypothèses testables. Aucune API payante et aucun entraînement de modèle.
