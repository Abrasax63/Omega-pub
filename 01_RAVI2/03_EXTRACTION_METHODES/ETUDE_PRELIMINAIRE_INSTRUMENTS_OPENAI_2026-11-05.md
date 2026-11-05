# Étude préliminaire — instruments mathématiques OpenAI (38 familles)

**Date : 2026-11-05**  
**Statut : EXTRACTION DOCUMENTAIRE PRÉLIMINAIRE — NON CERTIFIÉE**  
**Branche : `pilot/ravi2-extraction-c4-20261104`**  
**Périmètre : familles 112, 268, 293 et 221 de l'inventaire de Ying Xie**

## 1. Objet et règles de lecture

Cette note poursuit le pilote du module `01_RAVI2/03_EXTRACTION_METHODES`. Elle ne réévalue pas les théorèmes phares des manuscrits OpenAI et ne crée aucune brique scientifique certifiée.

On sépare quatre niveaux :
1. **Extraction rapportée** : instrument décrit dans la revue de Ying Xie.
2. **Source primaire repérée** : manuscrit ou formalisation OpenAI localisé.
3. **Vérification mathématique indépendante** : non réalisée par cette note, sauf reformulation élémentaire explicitement indiquée.
4. **Transfert vers nos travaux** : simple analogie, correspondance formelle, hypothèse testable ou résultat démontré. Aucun transfert n'est déclaré démontré ici.

La revue de Ying Xie examine 38 familles sur les 372 familles initiales. Elle précise que ses évaluations de nouveauté sont provisoires, que toutes les recherches bibliographiques ne sont pas exhaustives et qu'aucun projet Lean n'a été compilé ou vérifié par le noyau pour cette étude. Source : https://arxiv.org/abs/2610.17090.

## 2. Fiches de triage

### OPENAI-INST-112 — restriction signée indépendante du nombre de clauses

**Source secondaire précise :** Ying Xie, §9.3.2, famille 112, notamment Lemma 3.1 et Lemma 4.1.  
**Source primaire repérée :** *Beyond the Square-Root Exponent for Depth-Three Boolean Circuits* — https://github.com/openai/math/blob/main/preprints/Beyond-the-Square-Root-Exponent-for-Depth-Three-Boolean-Circuits-September-23-2026/main.pdf.  
**Formalisation annoncée :** https://github.com/openai/math/blob/main/lean/docs/112.md

**Instrument extrait.** Une expansion signée d'une CNF sous restriction aléatoire est réécrite comme mélange de termes pondérés positivement, chacun associé à l'espérance d'une CNF de largeur bornée. Une identité de mélange marqueur/ordre aléatoire normalise les indices de clauses violées et élimine la dépendance explicite au nombre de clauses dans la borne de corrélation rapportée.

La revue donne la borne sous la forme :
`|E[G · H|ρ]| ≤ W · corr_b(G)`, avec `E[W] ≤ 1/(1−θ)`, où la queue de type Poisson vérifie `θ < 1` dans le régime indiqué par la source.

**Intérêt possible pour notre axe #SAT / complexité.** C'est le candidat le plus directement pertinent pour les travaux de complexité : le mécanisme porte sur les corrélations entre une fonction et des CNF après restriction, et sur la manière de neutraliser la dépendance au nombre de clauses. Il ne faut cependant pas confondre cette borne de corrélation avec une borne #SAT, ni l'extrapoler à des formules ou profondeurs non couvertes.

**Contre-tests prioritaires avant tout transfert :**
- vérifier les conditions exactes sur largeur, paramètre de restriction et seuil `b ≫ pk` ;
- reconstruire l'identité marqueur-mélange à partir du manuscrit primaire ;
- tester les CNF dégénérées (clauses répétées, clauses tautologiques, clauses déjà satisfaites, largeur effective inférieure à b) ;
- vérifier si la borne est uniforme sur la fonction test G dans le périmètre exact ;
- comparer à la fois avec le switching lemma de Håstad et les variantes L1 de Tal, sans prétendre qu'elles donnent la même conclusion.

**Verdict RAVI-2 :** EXTRACTION DOCUMENTAIRE ; pertinence potentielle élevée pour #SAT ; validité et nouveauté de l'instrument non auditées indépendamment ; transfert non démontré.

### OPENAI-INST-268 — bootstrap couplé des puretés

**Source secondaire précise :** Ying Xie, §9.2.4, famille 268, Proposition 4.4.  
**Source primaire repérée :** *The periodic spin-one Haldane gap*, dépôt OpenAI Math : https://github.com/openai/math/tree/main/preprints/The-periodic-spin-one-Haldane-gap-September-24-2026.

**Instrument extrait.** Une même fonction de partition `Z_n(b)` admet deux expressions de pureté :
- pureté de Gibbs `T(n,b)=Z_n(2b)/Z_n(b)^2` ;
- pureté spatiale `S(n,b)=Z_{2n}(b)/Z_n(b)^2`, issue des valeurs propres de l'opérateur de transfert spatial.

Le carré des poids de Gibbs double l'inverse température ; le carré des poids spatiaux double la longueur. Les identités exactes entre ces deux descriptions couplent les deux opérations et permettent, sous des hypothèses quantitatives précises, un bootstrap dyadique du défaut de pureté.

**Ce qui est établi par la revue, et ce qui ne l'est pas ici.** Xie indique que l'amélioration quadratique concerne un régime de haute pureté et ne force pas une convergence vers la pureté 1 à partir de données arbitraires (le vecteur uniforme est invariant). Le critère final de gap exige davantage que `T(L,b)>1/2` : il dépend aussi des hypothèses quantitatives de décroissance et de température.

**Intérêt possible pour nos travaux.** Piste abstraite sur les systèmes possédant deux représentations exactes d'une même quantité et deux opérations de raffinement/doublement couplées. Cela ne fournit actuellement aucune correspondance avec `W_L`, `μ_L`, `Δ_h` ou les dynamiques finies déterministes. Toute analogie avec nos profils d'observation serait prématurée.

**Contre-tests prioritaires :**
- vérifier les identités exactes et les hypothèses de la Proposition 4.4 dans le manuscrit primaire ;
- examiner le cas uniforme et les cas de pureté faible ;
- séparer le lemme élémentaire sur la pureté d'un vecteur de la partie propre à l'opérateur de transfert quantique ;
- chercher un modèle fini classique où les deux doubles transformations sont réellement définies et couplées, sans fabriquer cette structure.

**Verdict RAVI-2 :** EXTRACTION DOCUMENTAIRE ; transfert vers systèmes dynamiques finis NON ÉTABLI ; priorité basse tant qu'un modèle commun exact n'est pas identifié.

### OPENAI-INST-293 — obstruction par décroissance stricte sur une base ergodique

**Source secondaire précise :** Ying Xie, §9.4.3, famille 293, construction « backward intertwiner over an ergodic base ».  
**Source primaire/formalisation repérée :** https://github.com/openai/math/blob/main/lean/docs/293.md

**Instrument extrait.** La construction utilise l'odometer 2-adique préservant la mesure de Haar. Une structure de sous-espaces est codée par un indice entier mesurable `s(x)`. L'intertwiner impose une décroissance stricte le long de l'action, de la forme `s(x+1) ≤ s(x)−1`. Une telle fonction entière mesurable ne peut exister sur une base préservant une mesure de probabilité ; cette contradiction exclut le sous-espace hyperinvariant supposé dans la construction.

**Lien limité avec nos systèmes finis.** Sur un cycle fini, une fonction entière ne peut pas décroître strictement à chaque étape et revenir à sa valeur initiale. C'est une obstruction élémentaire de rang/ordre sur les orbites périodiques. Elle peut servir de contrôle de cohérence lorsqu'une construction prétend fournir un rang strictement décroissant sur une composante récurrente.

Mais ce fait fini est élémentaire et ne constitue ni une nouvelle brique, ni une traduction du théorème ergodique, ni une conséquence concernant `Δ_h`. Pour les systèmes non injectifs, les parties transitoires et les cycles doivent être traités séparément.

**Contre-tests prioritaires :**
- distinguer orbites périodiques, arbres transitoires et composantes récurrentes ;
- vérifier les hypothèses de mesurabilité et de préservation de mesure dans la preuve source ;
- ne pas remplacer l'odometer ergodique par une fonction finie sans démontrer la correspondance.

**Verdict RAVI-2 :** REFORMULATION ÉLÉMENTAIRE pour l'obstruction sur un cycle fini ; instrument source extrait mais non audité ; aucune nouvelle brique proposée.

### OPENAI-INST-221 — perturbations hiérarchiques à profondeurs marquées

**Source secondaire précise :** Ying Xie, §9.4.1, famille 221, Théorème 7.6 et Lemme 4.5 / Théorème 8.2.  
**Sources primaires repérées :**
- https://github.com/openai/math/tree/main/preprints/The-Mezard-Parisi-formula-for-diluted-spin-glasses-September-23-2026
- https://github.com/openai/math/blob/main/lean/docs/221.md

**Instrument extrait.** Des perturbations de Poisson marquées à des profondeurs prescrites d'une hiérarchie auxiliaire produisent des identités sur les arbres prescrits. Les marques partagées servent d'indicateurs de partage ; une polarisation sélectionne des motifs de branchement avec coefficients signés exacts. Un mécanisme de décalage de profondeur impose qu'une séparation ciblée soit créée par une nouvelle scission unaire, ce qui contrôle la somme des coefficients dans une limite où une division naïve donnerait une erreur d'ordre 1.

**Intérêt possible.** La gestion de dépendances hiérarchiques et le contrôle d'erreurs par déplacement d'un niveau pourraient être examinés comme méthode générale. Mais la construction est probabiliste, liée aux modèles d'Ising dilués et aux recouvrements multiples. Elle ne se transpose pas directement aux trajectoires déterministes finies.

**Contre-tests prioritaires :**
- reconstruire l'identité de Poisson add-one et les coefficients signés ;
- vérifier l'ordre des limites `N → ∞`, puis `L → ∞`, puis `η → 0` ;
- tester explicitement le coût d'un décalage de profondeur sur des arbres finis ;
- distinguer l'identité combinatoire sur les arbres de l'argument probabiliste de concentration.

**Verdict RAVI-2 :** EXTRACTION DOCUMENTAIRE ; transfert non établi ; candidat secondaire pour une étude méthodologique des hiérarchies.

## 3. Priorisation

1. **Famille 112 — priorité haute** : seule piste ayant un raccord direct et explicite avec l'axe #SAT / complexité. Prochaine étape : lecture primaire de Lemma 3.1 et reproduction indépendante de l'identité marqueur-mélange.
2. **Famille 293 — priorité moyenne/faible** : contrôle élémentaire sur les cycles finis à formaliser proprement, mais aucune nouveauté mathématique revendiquée.
3. **Famille 268 — priorité exploratoire** : attendre d'avoir identifié un modèle fini où le couplage des deux purités est exact.
4. **Famille 221 — priorité exploratoire** : examiner d'abord le mécanisme de décalage de profondeur sur des arbres finis, sans prétendre reproduire le théorème de spin glasses.

## 4. Limites et décisions

- Aucun de ces instruments n'est promu dans le noyau scientifique certifié.
- Aucun calcul, compilation Lean ou reproduction des manuscrits primaires n'est revendiqué dans cette note.
- Les étiquettes de nouveauté de Ying Xie restent des évaluations provisoires.
- Les statuts de formalisation indiqués par les dépôts ne garantissent pas que le contenu formalisé corresponde exactement au résumé du manuscrit ; il faut lire les fichiers de portée et les énoncés Comparator.
- Les pistes de transfert sont conservées séparément des faits établis.

**Prochaine expérience décisive recommandée :** reconstruire l'identité de restriction signée de la famille 112 à partir du texte primaire, puis la confronter à des CNF de petite taille énumérées exactement. Si l'identité échoue dans un cas limite ou si ses hypothèses ne couvrent pas la forme #SAT étudiée, fermer ce transfert comme non pertinent plutôt que l'étendre artificiellement.
