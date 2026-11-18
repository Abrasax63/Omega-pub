"""Falsify recognition of literal dollars in a bounded Markdown fragment."""
import json
from time import perf_counter
from read import packetize, verify_packets

CASES = {
    "escaped": (r"Prix écrit \$\$ dans le texte.", False),
    "literal_code": ("Le code `$$` est affiché tel quel.", False),
    "plain_control": ("Prix écrit dans le texte.", False),
    "display_control": ("$$\nx=y\n$$", True),
}

def measure():
    results = {}
    for name, (intro, math) in CASES.items():
        raw = (intro + "\n## Suite\nTexte ordinaire.\n").encode()
        document = packetize(raw, name + ".md")
        expected = [(intro, [], math), ("Texte ordinaire.", ["Suite"], False)]
        actual = [(p["source_quote"], p["section_path"], p["contains_display_math"])
                  for p in document["packets"]]
        results[name] = (actual == expected, not verify_packets(raw, document))
    return results

if __name__ == "__main__":
    print(json.dumps(measure(), sort_keys=True))
    start = perf_counter()
    for _ in range(1000):
        measure()
    print(f"{perf_counter() - start:.6f} s / 1000 replays")
