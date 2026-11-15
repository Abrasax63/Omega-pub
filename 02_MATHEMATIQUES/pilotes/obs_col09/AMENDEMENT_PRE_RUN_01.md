# Amendement PRE-RUN au protocole OBS-COL-09 (2026-11-15)

Cet amendement est ajouté **avant création du benchmark et avant exécution des modèles**. Il ne répond à aucun résultat mesuré.

Dans le pré-enregistrement initial, les mots de test étaient définis à longueur 5..12. Or `RandomWalkEqOracle` interroge parfois un mot dont les préfixes coïncident avec un mot de test. Pour éviter de confondre évaluation post hoc et **réserve réellement non vue**, on garde la graine de sélection mais adopte la longueur 12..18 (256 mots uniques par modèle). Un mécanisme générique conserve un journal de tous les préfixes physiquement observés pendant l'apprentissage : tout mot réservé apparu dans ce journal est marqué `overlap` et exclu du score `unseen_only`, sans remplacement après mesure. Les mots complets de test peuvent aussi servir à un score total séparé clairement identifié comme susceptible de recouvrement.

Le nombre de mots exclus et le nombre restant doivent figurer dans le JSON. Si aucun mot non vu ne reste, le score de généralisation est **INDÉTERMINÉ**, jamais « parfait ».

La sélection des mots n'utilise ni vérité terrain ni sortie de l'apprenant. Aucun coût de P1 ou de random walk n'est omis du compte de consultations.
