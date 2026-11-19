# TRANSFER27 — préenregistrement, avant données, générateur et score

Date 2026-11-19. **Version 0, gelée avant code et corpus.** Branche expérimentale **empilée sur TRAIN26 PR #198** ; aucune modification ni fusion de `main`, aucun appel d'API payante. Recherche d'un **transfert de représentation**, non d'un théorème nouveau.

## Question principale

Le modèle `HuggingFaceTB/SmolLM2-135M-Instruct` entraîné sur les **320 exemples de TRAIN26** (640 pas, adaptateur LoRA sauvegardé dans l'artefact historique de run #44512647677) peut-il proposer une **formule universelle correcte** pour des domaines de mathématiques **absents des textes d'entraînement**, avec ou sans retour d'un vérificateur fini indépendant ?

**Trois bras prédéfinis**, pour **exactement les mêmes 16 énoncés et deux appels de génération par énoncé** (même modèle de base, même politique greedy, même maximum 96 nouveaux tokens par appel, 32 appels / bras) :
- **A : BASE+contrôle neutre** = SmolLM2-135M original ; au deuxième appel, seule consigne neutre de révision, sans oracle.
- **B : LORA+contrôle neutre** = mêmes poids initiaux plus l'adaptateur TRAIN26, deuxième appel sans oracle.
- **C : LORA+vérificateur** = même adaptateur TRAIN26 ; le deuxième appel reçoit un rapport **calculé à partir d'une cohorte de calibration** (un contre-exemple avec attendu et observé, ou une confirmation bornée, ou un refus syntaxique). Pas de troisième appel et **aucun ajustement des poids** pendant cette expérience.

Comparer le **premier jet A/B** (effet de LoRA) et le **dernier jet B/C** (effet possible de la rétroaction). Le budget en *appels* et en *plafond de jetons générés* est identique ; **les jetons d'entrée et le coût CPU des vérificateurs ne sont pas forcément égaux**, ils doivent être comptés. Ne pas affirmer une comparaison à coût total exactement égal. A/B reçoivent un texte témoin explicite sans indication de vérité, C reçoit un retour factuel de l'oracle; il s'agit du mécanisme testé.

## Problèmes de transfert

**Famille M (6 paraphrases distinctes)** : sur les résidus modulo `modulus`, application itérable de `state = (state + step) % modulus` ; décider s'il existe un nombre `k >= 0` d'applications pour passer de `start` à `target`. Une bonne représentation peut utiliser `gcd` et la divisibilité ; **elle n'est pas donnée au modèle** dans les prompts.

**Famille I (6 paraphrases)** : deux intervalles fermés sur les entiers `[a,b]`, `[c,d]`, avec `a<=b`, `c<=d`; décider si leur intersection est non vide. Une bonne représentation peut utiliser `min` et `max` ; **pas de critère de chevauchement dans le prompt**.

**Famille OOD (4 énoncés)** : demandes de théorie ouverte, contraintes non précisées, suites d'actions non décrites ; réponse attendue `ABSTAIN`, ne pas forcer un résultat.

**Absence dans le corpus TRAIN26** : rechercher explicitement les termes « gcd / modular / modulo / interval / overlap / intervalle » dans ses 320 prompts et cibles. Les familles **n'ont pas été utilisées comme exemples dans TRAIN26**. Cela ne signifie pas qu'elles étaient absentes du préentraînement de SmolLM2, ni que leur traitement constitue une invention nouvelle. Les *fonctions disponibles* `gcd`, `min`, `max` fournissent une amorce architecturale évidente : la nouvelle combinaison est le seul comportement testé.

## Séparation stricte avant évaluation

Après ce préenregistrement et **avant code de modèle**, geler dans Git :
- `PROMPTS_FROZEN.json` : les **16** énoncés et leurs domaines, sans réponses.
- `CALIBRATION_FROZEN.json` : **24 cas M + 24 cas I**, 12 vrais/12 faux par famille ; les seuls exemples que le vérificateur peut révéler au bras C, un seul témoin au maximum par énoncé.
- `HOLDOUT_FROZEN.json` : **96 cas M + 96 cas I**, 48 vrais/48 faux par famille, sans valeurs identiques à la calibration et plages de nombres distinctes. Il reste non lu par le programme générateur et celui du feedback.
- `ANSWER_KEY_EVAL_ONLY.json` : cibles de domaine `M/I` (le critère de référence pour débogage humain) séparées ; **jamais** injectées dans les prompts ni utilisées par le code qui génère les réponses.

Pour la famille M, l'oracle *indépendant* calcule par exploration cyclique directe et un second oracle de divisibilité par `gcd`; en cas de désaccord **FAIL CLOSED**. Pour I, l'oracle direct énumère les entiers et un second oracle de bornes compare les intersections ; désaccord **FAIL CLOSED**. Le modèle ne reçoit ni critère explicite, ni fonction nommée « reachability » ou « overlap ».

## Expression et sécurité

Une génération valide est **une seule ligne** `EXPR: expression_booléenne` ou exactement `ABSTAIN`. Langage fermé : noms des entrées du domaine, fonctions `gcd(x,y)`, `min(x,y)`, `max(x,y)`, comparaisons, `+,-,%`, entiers 0..64, `and/or/not`, parenthèses. Pas de `eval`, `exec`, import, attribut, subscripting, boucles, multiplication ni division. Limites AST/taille strictes et trace des refus. Un modèle hors scope doit s'abstenir; une expression hors grammaire est rejetée, jamais réparée automatiquement.

Les deux premiers jets sont sauvegardés **avant** les retours du vérificateur. Le bras C peut voir un seul contre-exemple de calibration dans le second prompt. **Le holdout n'est ouvert que dans le job d'évaluation séparé** après archivage des sorties brutes. Le premier jet et le deuxième jet de chaque bras sont évalués **tels quels**, sans nettoyage ni extraction de code.

## Évaluation et statistiques

**Par énoncé de M/I** : compter valide si la formule passe **96/96 exemples réservés** (un statut `EMPIRICAL_FINITE_EQUIVALENCE`, jamais « démontré universellement ») ; si formule fausse, enregistrer **premier contre-exemple exact**. Un rejet syntaxique ou `ABSTAIN` ne rapporte pas de faux succès. **OOD** : réussite seulement si sortie exactement `ABSTAIN`.

Rapporter séparément :
- formulations valides M/I sur 12, abstentions OOD sur 4, erreurs de type faux verdicts, refus syntaxiques, faux positifs sur calibration, réponses premières/finales ;
- nombre réel d'appels, tokens prompt + complétion, temps CPU de génération, temps du vérificateur et nombre d'exemples testés;
- exactitude du témoin fort D **192/192** sur le holdout de M/I et sa complexité (intervalles et congruences courtes) ; ne pas prétendre que LLM bat D en efficacité;
- `C` comparé à `B` sur **les mêmes prédictions finales**, un gain seul C>B ne prouve pas la nouveauté de l'idée ni l'amélioration des poids;
- classes `TRANSFER_OBSERVED_BOUNDED` si B > A sur les **formules vérifiées sur 12**, `VERIFIER_FEEDBACK_GAIN_BOUNDED` si C > B, `NO_TRANSFER_GAIN` sinon. Statuts **constats sur la cohorte uniquement**, sans significativité statistique.

**Ne pas relancer le modèle après avoir vu le corrigé.** Si l'adaptateur historique est indisponible ou corrompu, classer `INDETERMINATE_ADAPTER` et arrêter. Enregistrer le hash SHA256 `4d378c42f491550251d8973fc1344351865d1d41bc6e24fd2d94d6a0d6a3b446` de `adapter_model.safetensors`, modèle et révision, arrêt si divergent. Adapter entraîné et évalué dans TRAIN26 sans retouche. Le fait que l'artifact GitHub expire (30 jours) ne doit pas être masqué : conserver un bilan scientifique et les empreintes.

## Critère de conclusion

**Un succès ne signifierait que la capacité d'un modèle ayant reçu une liste de primitives à trouver une combinaison correcte sur deux domaines classiques non vus dans son petit fine-tuning**. Pas de créativité générale, pas de nouvelle théorie, pas de modification du Qwen3B, pas de boucle autonome réellement apprenante. En cas d'échec : conserver précisément syntaxe, hypothèse fausse, manque de transfert, ou effet négatif de l'adaptateur.

Pas de nouvelle architecture ou de changement de seuil après inspection des résultats. Tout correctif d'infrastructure doit être daté et séparé dans un erratum, sans réécrire ce préenregistrement.
