# P5 — Résultats exécutés : 24 sources, quatre domaines, falsification contrôlée

Date 2026-11-11. **Statut CALCUL EXACT / PILOTE ADVERSARIAL CONSTRUIT.**
Pré-enregistrement : `5e49b13ee268e99df66cc5e0bba1dea654f759b6`.
[CI 43018557073](https://github.com/Abrasax63/Omega-pub/actions/runs/43018557073) : **SUCCESS**, 119 tests du Prisme (dont quatre nouveaux), tests RCE/MCP et smoke-tests des index réussis.

## Protocole exécuté
- 24 questions publiques ; quatre groupes de 6 : états `merged` GitHub, prescriptions HTTP RFC 9110, références relatives RFC 3986, expressions Python 3.
- Six valeurs GitHub contrôlées dans `get_pr_info` puis `fetch_pr`, SHA de tête concordants ; URL et SHA archivés dans le JSON.
- Six références URI contrôlées par `urllib.parse.urljoin`; six assertions Python par expressions explicites dans un test indépendant du générateur. Les règles HTTP sont issues de §§13.1.3–13.1.4 de RFC 9110 et doivent être relues à la source ; aucun correcteur humain externe indépendant n'a signé de certificat.
- La note secondaire trompeuse est un texte **fabriqué**, jamais une déclaration réelle de la source. Sur huit cas gelés, l'observation qui se présente comme primaire est artificiellement inversée en condition USURPÉ.
- Omega exécute réellement `optimize_policy`, horizon 1, coût 5 millièmes, **plafond dur d'un contrôle** ; le plan fixe possède exactement le même contrôle et budget. Son modèle suppose que ce contrôle détermine parfaitement la vérité.

## Mesures

| Condition | Note secondaire A (0 contrôle) | Plan fixe B (1 contrôle) | Omega C (1 contrôle) | Erreurs confiantes C |
|---|---:|---:|---:|---:|
| Source intacte, 24 cas | 16/24 | 24/24 | 24/24 | 0 |
| Source usurpée, 24 cas appariés | 16/24 | 16/24 | 16/24 | **8** |

En condition usurpée, **deux erreurs confiantes par domaine**, huit au total. Les 24 cas sont rejoués deux fois, **pas 48 observations indépendantes**. Les huit échecs proviennent de huit falsifications choisies avant exécution, pas d'un taux spontané d'erreurs dans le monde.

Pour diagnostics seulement, un contrôleur disposant de la **clé de vérité** signalerait les huit incohérences et pourrait s'abstenir. Cette voie est privilégiée et ne constitue **pas un quatrième bras équitable** : elle dispose de la réponse de référence et d'une deuxième source supposée fiable. On ne doit pas la comparer causalement à B/C.

## Verdict
- **DÉMONTRÉ dans ce modèle** : une observation fausse maintenue sous l'étiquette « contrôle parfait » conduit le solveur à une décision finale fausse tout en considérant que son risque conditionnel est nul ; la politique ne possède pas de contrôle d'authenticité autonome.
- **CALCUL EXACT** : dans les 24 cas utilisés, Omega et B sont identiques à budget de 1 contrôle ; seuls les huit cas falsifiés engendrent les huit erreurs.
- **NON DÉMONTRÉ** : qualité réelle d'Omega sur tâches nouvelles, compétence d'extraction de preuves multi-domaines, résistance à des attaques réelles, capacités d'un LLM, gain de coûts ou de temps, validation humaine aveugle.
- **AMÉLIORATION PRIORITAIRE** : intégrer une *chaîne de provenance contrôlable par un canal distinct*, une détection des contradictions et l'abstention lorsque l'origine n'est pas établie. Tester cette mesure sur des documents inconnus, sous même coût et avec une baseline également adaptative.

Sources :
- RFC 9110 : https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.3 et https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.4
- RFC 3986 §5.4.1 : https://www.rfc-editor.org/rfc/rfc3986.html#section-5.4.1
- Python bool : https://docs.python.org/3/library/stdtypes.html#boolean-type-bool
- PR GitHub : références exactes dans `prism/p5_multidomain_public_cases_2026-11-11.json`.

## Reproduction
Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :
```sh
python p5_multidomain_adversarial.py
python -m unittest -v test_p5_multidomain_adversarial
```
Les résultats sont *une calibration publique*, pas une épreuve indépendante invisible aux modèles. Une future campagne A/B/C/D requiert des sorties de modèles isolés, traces d'outils, coûts fournisseurs, holdout non divulgué et double notation humaine aveugle. La PR est un brouillon, sans fusion ni écriture SQLite ni promotion CORE.
