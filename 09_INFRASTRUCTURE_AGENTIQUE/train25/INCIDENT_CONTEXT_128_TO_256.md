# TRAIN25 — incident de longueur de contexte, réparation causale

19 novembre 2026. [Run initial #44506808403](https://github.com/Abrasax63/Omega-pub/actions/runs/44506808403).

**État** : vérification des données/contrôles offline = SUCCESS ; installation des bibliothèques CPU et téléchargement du modèle public = SUCCESS ; job d'entraînement = FAILED. Message exact : `ValueError: TRAIN_SAMPLE_TOKEN_LENGTH_EXCEEDS_PREREG_128` dans `train_lora.py`. Les pas d'entraînement n'ont pas été achevés et aucun adaptateur entraîné utilisable n'a été publié ; le job d'évaluation n'a pas démarré.

**Cause : dimensionnement insuffisant** de la limite de séquence prévue (128 tokens) pour l'association du système, de l'énoncé en français et de sa sortie mathématique. Ce n'est ni une réfutation scientifique, ni un manque de généralisation du modèle.

**Réparation minimale décidée AVANT toute évaluation ou lecture du holdout** : autoriser une longueur de séquence jusqu'à 256 tokens, sans troncature ni changement des exemples, des cibles, de l'ordre des données, du nombre de pas (24), du taux d'apprentissage, de la graine, du modèle, des paramètres LoRA ou des critères de validation. Ne pas modifier le `PREREG.md` initial : conserver l'hypothèse erronée « max 128 » et cette note d'erratum. La seule conséquence est l'augmentation possible du calcul par séquence, à mesurer.

**Interprétation :** les résultats du relancement respecteront une version corrigée `TRAIN25_CONTEXT_256_ERRATUM`, et pas l'ensemble strict des contraintes matérielles du préenregistrement initial. Toute évaluation ultérieure doit déclarer cet écart. Aucune API payante, `main` inchangée.
