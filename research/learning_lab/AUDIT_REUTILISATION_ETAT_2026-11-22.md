# OMEGA — audit anti-duplication et plan d'apprentissage réutilisable

**Date : 22 novembre 2026. Statut : AUDIT DOCUMENTAIRE + CONTRATS LOGICIELS VÉRIFIABLES ; pas de nouvel entraînement.**

**Périmètre effectivement contrôlé :** arbre Git du dépôt public \`Abrasax63/Omega-pub\`, PR et code sources de branches expérimentales, logs GitHub Actions de TRAIN26 et TRANSFER27, résultats réels des pilotes Python V1/V2/V3, sources universitaires ou documents officiels mentionnés ci-dessous. Une PR DRAFT techniquement verte ne prouve pas un gain scientifique.

## 1. Premier constat important — le noyau existe déjà

Sur \`main\`, l'arbre Git récursif expose **59 entrées (répertoires et fichiers)**, principalement gouvernance et mathématiques. Les expérimentations de langue, apprentissage, LoRA et mémoire durable sont sur **différentes branches de PR non fusionnées**. Cela explique une partie du sentiment « déjà construit, mais non exploité » : un code vivant dans une PR ne devient pas automatiquement une capacité du runtime Omega sur \`main\`.

**Correction explicite du discours précédent :** nous avions déjà entraîné de vrais paramètres, sur **un petit modèle SmolLM2 135M auxiliaire**, même si **les essais de Qwen3B V1–V3 ne modifiaient aucun poids**. Il serait faux de dire qu'Omega n'a jamais eu de LoRA.

| Brique préexistante | Évidence concrète | À conserver / limite |
|---|---|---|
| Génération de vérificateurs | PR [#79](https://github.com/Abrasax63/Omega-pub/pull/79), [#81](https://github.com/Abrasax63/Omega-pub/pull/81) | Adapter/réutiliser contrôles, pas revendiquer un apprentissage neuronal |
| Gate anti-régression | PR [#83](https://github.com/Abrasax63/Omega-pub/pull/83), [27 tests et run](https://github.com/Abrasax63/Omega-pub/actions/runs/43687842990) | Réutiliser contrôle coûts, groupes de provenance et non-perte, mais origine des groupes reste une affirmation du producteur |
| Mémoire scientifique durable | PR [#228](https://github.com/Abrasax63/Omega-pub/pull/228), [run](https://github.com/Abrasax63/Omega-pub/actions/runs/44878832829) | Registre chaîné, quarantaine des LLM. **Ne pas mélanger faits prouvés et corrections de code simplement utiles** |
| Modélisation actif Mealy | PR [#136](https://github.com/Abrasax63/Omega-pub/pull/136), [run](https://github.com/Abrasax63/Omega-pub/actions/runs/43964241311) | Vraie boîte noire / oracle après reconstruction ; domaine fini et sans LLM, pas équivalent à apprendre Python |
| Plasticité A→B→A′ | PR [#128](https://github.com/Abrasax63/Omega-pub/pull/128), [run](https://github.com/Abrasax63/Omega-pub/actions/runs/43918567785) | Paramètres de petite politique mis à jour ; signal descriptif, ne surpasse pas comparateurs FIXED/MEMORY |
| LoRA TRAIN25 | PR [#197](https://github.com/Abrasax63/Omega-pub/pull/197) | Poids SmolLM2 réellement changés, 24 pas ; **0 gain sur 24 épreuves utiles** selon TRAIN26 |
| LoRA TRAIN26 | PR [#198](https://github.com/Abrasax63/Omega-pub/pull/198), [run réel #44512647677](https://github.com/Abrasax63/Omega-pub/actions/runs/44512647677) | **640 mises à jour**, delta L2 **10,0499777148** ; **0/48 → 29/48** sur familles déjà enseignées. Logs font apparaître **12 → 3 faux verdicts** ; cela n'établit pas la généralisation hors domaine |
| TRANSFER27 | PR [#199](https://github.com/Abrasax63/Omega-pub/pull/199), [run #44518970468](https://github.com/Abrasax63/Omega-pub/actions/runs/44518970468) | Trois bras base / LoRA / LoRA+feedback : **0/12 représentations validées chacun sur deux nouvelles familles**, aucun bénéfice vérifié du feedback |
| Python black-box et cours | PR [#232](https://github.com/Abrasax63/Omega-pub/pull/232), [#233](https://github.com/Abrasax63/Omega-pub/pull/233), [#234](https://github.com/Abrasax63/Omega-pub/pull/234) | La version V3 conserve 16/40 réussites E malgré une correction mal formatée, mais transfert F **0/40 → 0/40** ; résultats insuffisants |
| Mathématiques Web / bibliothèque | PR [#230](https://github.com/Abrasax63/Omega-pub/pull/230), [#231](https://github.com/Abrasax63/Omega-pub/pull/231) | Recherche autonome et provenance, mais 0/3 citations littérales retenues dans le vrai essai d'abstraction ; mémoire certifiée jamais alimentée par ces sorties |

**Conséquence :** ne PAS coder un nouvel agent autonome, nouvel évaluateur de base, nouveau runner de modèle ou nouveau moteur LoRA. Réutiliser les briques déjà testées et écrire seulement une passerelle minimale vérifiable.

## 2. Ce qui existe dans la littérature et les outils publics

### A. Voyager — cursus adaptatif + bibliothèque de compétences exécutables

Wang et al., *Voyager: An Open-Ended Embodied Agent with LLMs*, TMLR 2024, [texte et synthèse académique](https://mlanthology.org/tmlr/2024/wang2024tmlr-voyager/).

Il assemble précisément **un curriculum automatique**, **une bibliothèque de code réutilisable** et **un mécanisme de correction depuis les erreurs d'exécution**. Il est démontré dans Minecraft, **pas** comme preuve d'un modèle de langage devenu auto-constructeur ou d'un entraînement de ses poids. Sur Omega, la première et la deuxième composante existent partiellement mais le transfert entre familles est précisément la faiblesse mesurée.

### B. Reflexion — apprendre en contexte des retours, sans modifier les poids

Shinn et al., NeurIPS 2023, [article](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html).

Réflexion sur feedback et mémoire d'épisodes pour les prochaines décisions. Éclaire nos essais V1–V3, **mais ne constitue pas du fine-tuning**. La dégradation 11/40→0/40 V2 montre qu'une note de mémoire peut aussi nuire ou ne pas être pertinente.

### C. SWE-agent / OpenHands — interface de programmation et sécurité

Yang et al., NeurIPS 2024, [SWE-agent](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf) : interface model-friendly pour lire, modifier, exécuter et recevoir du feedback. [OpenHands](https://www.openhands.dev/) : plateformes d'exécution agentique en environnement isolé, pas besoin de réinventer une plateforme complète.

[OpenHands benchmarks](https://github.com/OpenHands/benchmarks) contient **ProgramBench**, directement proche de notre projet : reconstruction d'un programme à partir d'un binaire compilé et de documentation. Une tâche externe de ce type est préférable aux seuls oracles synthétiques écrits par nos soins, mais il faut vérifier les licences, coûts de préparation et contamination possibles avant de l'utiliser.

### D. LoRA / PEFT — progrès paramétrique réel mais pas garantie de transfert

Documentation de référence [Hugging Face PEFT](https://huggingface.co/docs/transformers/peft), [LoRA](https://huggingface.co/docs/peft/main/en/package_reference/lora).

TRAIN25/26 utilisent déjà cette famille : **ne pas créer une deuxième implémentation générique**. Former un adapter SmolLM2 sur des étiquettes de formalisation mathématique ne lui apprend pas automatiquement le Python. Pour ce nouveau domaine, il faudra un corpus/programme d'entraînement **contractuellement différent** et évaluer les régressions d'anciennes compétences.

### E. Évaluation — attention aux tests devenus trop connus

[OpenAI, 23 février 2026](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) : annonce l'abandon de SWE-bench Verified pour ses lancements en raison de problèmes de contamination et de conception de tâches. Cette alerte confirme notre besoin de **nouveaux exercices**, de groupes non miroirs et de holdouts propres à chaque cycle. Un workflow vert ne suffit pas.

## 3. Déficits observables (priorité opérationnelle)

1. **Incorporation** : modules dispersés sur branches/PR ; aucun raccord complet « compétence Python validée → corpus SFT → LoRA Python → test externe inédit » vérifié.
2. **Qualité de l'enseignant et du parseur** : réponses JSON incorrectes et code invalide ; la langue Python standard était parfois refusée par la politique AST. Il faut distinguer format, syntaxe, politique et logique.
3. **Qualité/volume des données** : une poignée de corrections valides ne justifie pas 640 steps d'un nouvel entraînement. Le volume et la diversité sont insuffisants. Les exemples de maîtrise V3 déjà utilisés **ne doivent plus être traités comme des holdouts indépendants**.
4. **Conservation des acquis** : best-state V3 fonctionne sur un cas, mais reste local à un artefact temporaire ; le registre SCI-MEMORY persiste sur Git, pas encore les compétences de programmation.
5. **Signal de généralisation** : TRAIN26 29/48 en domaine voisin mais TRANSFER27 0/12 sur familles nouvelles. Éviter les affirmations d'AGI ou de transfert autonome.

## 4. Correctifs concrets apportés sans nouveau moteur

Sur la branche de la PR #234 :

- La liste d'opérations sûres du runner Python est harmonisée avec les exercices : \`str.isupper()\`, \`str.islower()\` et \`reversed()\` (dans l'AST ET le processus de calcul isolé). Les appels dangereux restent interdits. **Ces modifications NE changent pas a posteriori les scores V3 originaux.**
- \`verified_python_training_export.py\` lit un rapport V3 réel ou compatible, **contrôle les sorties brutes du modèle**, l'index de la meilleure version, l'intégrité des exemples publics, les résultats de maîtrise **déjà consommés**, et leur reproduction par le code exact.
- Les échecs et la syntaxe invalide restent **en quarantaine**. Un exemple candidat ne contient **aucune des entrées/corrigés cachés E/F**, aucune modification de poids ni résultat artificiellement promu.
- Le manifeste marque les familles et holdouts V3 déjà utilisés comme **interdits à un futur test indépendant**.
- **Garde minimal de diversité** : 12 familles distinctes exigées avant une décision d'ouvrir un nouveau protocole d'entraînement. **Ce seuil est un garde-fou d'ingénierie et ne constitue PAS une preuve qu'un dataset de 12 familles suffirait au fine-tuning.**
- Le format candidat \`TASK=PYTHON_REPAIR\` est **explicitement INCOMPATIBLE** avec les labels de TRAIN26 (\`TASK=FORMALIZE/REPAIR/CRITIQUE/ABSTAIN\`, sortie \`EXPR:\`). Ne pas injecter le code Python en silence dans \`train26/train_full.py\` ; réutiliser son architecture quand un nouveau protocole de programme est justifié.
- Workflow **offline seulement**, sans inférence modèle et sans gradients, pour tester ces contrats. Le vrai run V3 déjà consommé a son emploi de modèle gelé sur SHA précédent ; pas d'autre répétition à présenter comme indépendante.

## 5. Prochain test réellement nouveau

Avant toute formation paramétrique Python :
1. Constituer un corpus de **solutions de programmation produites par le modèle** et vérifiées par exercices publics *et* validation indépendante réservée, avec au moins plusieurs familles différentes et une séparation attestée par groupes de problèmes.
2. **Geler** un nouveau jeu de problèmes, mieux encore inclure une cohorte externe telle que ProgramBench pour tests après entraînement, sans l'inspecter ou l'ouvrir dans le formateur.
3. Réutiliser \`TRAIN26\` comme **modèle de pipeline CPU et de preuve de variation réelle des poids** et \`AutoResearch #83\` comme garde budget/anti-régression ; fournir un **contrat de données Python séparé**.
4. Mesurer base vs LoRA-Python, apprentissage en contexte et référence symbolique, avec temps/jetons, oublis sur tâches antérieures et comparaisons groupées.
5. Aucun merge, aucune promotion de compétence ni recrutement de modèle de production avant une amélioration reproductible sur **données réellement nouvelles**.

**Verdict :** notre capacité de fine-tuning n'est pas le point aveugle ; **le flux entre expériences, sélection d'exemples fiables, diversité du corpus et mesure de transfert** l'est. La bonne réponse n'est pas « ajouter encore un agent », mais **raccorder les composants déjà présents en gardant leurs frontières de preuve**.
