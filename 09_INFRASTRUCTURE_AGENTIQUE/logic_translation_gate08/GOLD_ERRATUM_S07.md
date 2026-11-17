# GOLD ERRATUM S07 — erreur de transcription du corrigé, pas retouche du moteur
2026-11-17. Run initial holdout : https://github.com/Abrasax63/Omega-pub/actions/runs/44153033017 — FAILED due to `ValueError: gold manual span absent in historical source`.

Le gold figé initial `GOLD_SKELETON09_FROZEN.json`, commit `8a10b001bdedfc7d85d6ba78362413b1da19d40f`, portait sur S07, ligne 25 de BR-ACC-STATE-COMMUTE-01, l'ancre incorrecte `si et seulement si`.
La source Git SHA `c4c89930f075983e085da5e38c956f12dc61186e` contient exactement `si et seulement s’ils`. La nouvelle pièce `GOLD_SKELETON09_ERRATUM1.json` ne corrige que cette ancre et documente la correction ; le premier gold reste immuable.

Le programme `skeleton09.py` demeure STRICTEMENT inchangé et figé à son Git blob `4462d120496f9c2743ab4168227d184b5d2e1305` ; sa grammaire ne reconnaît pas `s’ils`. Ne pas interpréter cette correction manuelle de source comme du surapprentissage de l'extracteur ni comme un succès sémantique : S07 reste un cas potentiellement manqué.

Le run ultérieur doit conserver l'historique négatif du premier CI et signaler explicitement le caractère **corrigé a posteriori du gold**.