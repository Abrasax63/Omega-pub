# SEMANTIC-IR01 — results and decision
Frozen parser/guard and protocol: b46c377ed2a23766b331f9e7dfd68acc614e59c4.
Fresh benchmark: 74ac80459c3934838abbc014f7ebbd639565c3df.
CI https://github.com/Abrasax63/Omega-pub/actions/runs/45432415564
completed successfully; scientific primary criterion failed.
Artifact 14938533758, GitHub-reported ZIP SHA256
4cfed21482753dc1ad9f5da2bed8c85b4a519c87fc09fafc7d3fe675e50524af.
Results from verified CI logs, not independent local artifact replay.

60 new templates, 12 per class, two payloads per template. Same author
as parser, after freeze, not external or blind. Same template induces
same route for both payloads: 60 distinct routing decisions per arm.
Exact route + independently checked mathematical result:
| arm | projection | closure | inverse | compose | unsupported | total |
|---|---:|---:|---:|---:|---:|---:|
| IR |14/24|16/24|16/24|18/24|24/24|88/120|
| frozen NB |16/24|14/24|20/24|16/24|2/24|68/120|
| keyword |8/24|14/24|12/24|8/24|10/24|52/120|
| oracle |24/24|24/24|24/24|24/24|24/24|120/120|

IR: 0/24 unsupported dispatch, 28/96 supported abstentions,
4/96 supported wrong dispatch (composition incorrectly routed to inverse),
64/68 dispatched supported tasks correct. 8/8 malformed plan mutations
rejected. +20/120 versus frozen NB on same test. Primary threshold
108/120 and composition >=22/24 both failed. No promotion.
Example missed paraphrase: "Quelle est la composante du vecteur dans
l'espace nul de la matrice ?" abstains. Negation clause extraction
incorrectly abstains on "Ne pas calculer de primitive, mais projeter les
coordonnées sur le noyau." Worse, "Donner les écarts les plus proches de
somme zéro puis leur antécédent circulaire" and "Rendre les différences
intégrables sur le cercle, puis restituer les niveaux" both route to
inverse without required projection. A well-typed plan is not proof of
semantic fidelity to the original request.

Decision: retain typed guard and exact instruments as experimental
infrastructure; do not activate lexical parser autonomously. Next
prospective experiment should measure actual model-generated structured
plans (free local/open-weight model if feasible), using fresh externally
or independently authored tasks, semantic contract verification and
clarification/abstention when goal ambiguous. Compare against frozen IR
and oracle, no tuning on these 60 templates as fresh evidence.
No LLM was called in this experiment, no learned model weights changed,
no autonomous skill acquisition or runtime integration demonstrated.
No main change, no paid API.
