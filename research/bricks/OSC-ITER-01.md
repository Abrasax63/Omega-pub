# OSC-ITER-01 --- Itération oscillatoire à gain fixe

Statut : CERT-V composite. Version 1.0, 2026-10-15.

Interface : base/stress admissible + amplitudes primaires fixes +
inverse linéarisé signé + corrections moyennes/cinq équations → étape
suivante avec mêmes données structurelles et gain résiduel +1/10.

Dépendances : OpenAI Propositions 7.5, 7.6, 9.6 et mécanismes de §8.

Correction durable : B(W0,LΣ)=Σ est exact pour la covariance bilinéaire
linéarisée ; la covariance non linéaire complète conserve C(LΣ) dans le
résidu suivant.

Limites : ne fournit pas à elle seule l'objet limite.