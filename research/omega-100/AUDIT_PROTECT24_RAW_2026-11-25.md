# Omega100 — PROTECT24, recalcul à partir des sorties brutes

25 novembre 2026, 23 h 02 CET. Branche `experiment/omega-100-2026-11-18`, départ `27a14286adfbfba67b557e9acb41e5f2751ba9d9`. Programme, 068 et journal précédent relus : 68 fiches, 069 libre. L'exécuteur local est de nouveau accessible. Question du complément : le rescorage exact des 960 réponses du [run PROTECT24](https://github.com/Abrasax63/Omega-pub/actions/runs/45685909054) confirme-t-il les mesures lues dans le journal précédent ?

**VÉRIFIÉ, audit d'un run existant.** Les empreintes des 320 questions uniques, les libellés calculés par oracle direct et les 960 sorties concordent. La trace ne fournit au modèle que les identifiants et les prompts selon le fichier questions. Insertion d'une sortie dupliquée rejetée. Par bras, 256 cas d'acquis et 64 de nouvelle tâche. Le recalcul confirme tous les totaux par compétence et le nombre de paires entièrement exactes. Chaque candidat a bien 32 enregistrements de pas et 128 calculs de gradient auxiliaire. Coûts par bras et tokénisation non recomptés.

| Mesure | Contrôle | Ordinaire | Protégé |
|---|---:|---:|---:|
| Copie, réponses exactes /64 | 64 | 62 | 64 |
| Copie, paires entières /32 | 32 | 30 | 32 |
| Nouvelle tâche, réponses exactes /64 | 2 | 18 | 18 |
| Nouvelle tâche, paires entières /32 | 0 | 5 | 5 |

Le bras protégé satisfait la partie sans régression sur cette cohorte, tandis que l'ordinaire perd deux réponses et deux paires en copie. Les deux échouent au seuil de nouvelle compétence (61/64 et 29/32). Cette confirmation rescore les mêmes sorties, sans réplication ni nouvelle expérience. Ni examen indépendant, ni rétention durable, ni supériorité stable établis. Référence conservée. Le test décisif reste une réplication indépendante de la préservation de copie, à pas appariés et avec un seuil distinct pour la nouvelle tâche.

`timeout 15s python3 audit_protect24_raw.py` avec l'artefact Actions 15059388537 renommé protect24.zip. SHA-256 de l'archive `6b7180c7933fe35e908e2236bed046b1bd6ce9f01a53eb98e3f957cb75ffa7a9`, égal au digest GitHub. Code `260acc4413374d078f2aebf8cf394b72c4d655179d4a57f63b35c480258fd5d6`, agrégats `13d73342d60b8a1f38daa6d8fb28a3470f160b0ed048cbeb7738e9d953ab19e2`. Recalcul local 0,0082 s. Le run archivé rapporte 3 381,529 s. Aucun nouvel entraînement ni corrigé publié.

**069 NON EXÉCUTÉE — cycle sans expérience nouvelle.** L'exécuteur fonctionne à nouveau. Aucun moteur ni poids local utilisable pour une inférence sur cas frais. A/P/B, rétention, transfert et régressions de 069 non mesurés. Référence conservée. Test suivant : croiser ordre et étiquettes pour l'appartenance, à moteur disponible. Aucun nouveau verdict COPY-SFT01 ni modification du rythme.

Registre lu et SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`. `existing_omega100` considéré, pertinent, exécuté pour l'audit des prédictions, utile pour confirmer les totaux et le verdict. Aucun composant ajouté ni coût payant.
