"""Experimental, source-anchored verifier for bounded Delta_h emptiness claims."""

import argparse
from dataclasses import asdict, dataclass
from itertools import product
import json
from pathlib import Path
import re
import sys

READER = Path(__file__).resolve().parents[3] / "09_INFRASTRUCTURE_AGENTIQUE" / "reader_bridge12"
if READER.is_dir():
    sys.path.insert(0, str(READER))

from gate import gate
from read import MAX_BYTES, packetize

MAX_SYSTEMS = 3984
MAX_JSON_BYTES = 32_768

# Each recognized line has one explicit role. An unrecognized nonblank line
# could qualify the claim, so the pilot abstains instead of ignoring it.
FORMS = {
    "max_states": (
        r"On considère au plus ([1-4]) états et une dynamique déterministe totale\.",
        r"La dynamique est totale et déterministe, sur ([1-4]) états au maximum\.",
    ),
    "horizon": (
        r"On fixe l’horizon à ([1-5])\.",
        r"Le nombre de pas est ([1-5])\.",
    ),
    "observation": (
        r"L’observation est (injective|arbitraire) sur son image\.",
        r"Sur son image, l’observation est (injective|arbitraire)\.",
    ),
    "conclusion": (
        r"Alors Δ_h est toujours vide\.",
        r"Pour tous ces systèmes, Δ_h = ∅\.",
    ),
}


@dataclass(frozen=True)
class Contract:
    max_states: int
    horizon: int
    observation: str


def recognize(line):
    for field, patterns in FORMS.items():
        for pattern in patterns:
            match = re.fullmatch(pattern, line)
            if match:
                value = match[1] if match.lastindex else "empty_delta"
                return field, int(value) if value.isdecimal() else value
    return None


def propose(raw, path):
    inventory = packetize(raw, path)
    packets_by_line = {
        line: packet["packet_id"]
        for packet in inventory["packets"]
        for line in range(packet["start_line"], packet["end_line"] + 1)
    }
    fields, evidence = {}, []
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip() or (number == 1 and line == "# Énoncé"):
            continue
        recognized = recognize(line)
        if recognized is None:
            return None
        field, value = recognized
        if field in fields:
            return None
        fields[field] = value
        evidence.append({
            "role": "conclusion" if field == "conclusion" else "premise",
            "packet_id": packets_by_line[number],
            "line": number,
            "literal": line,
        })
    if fields.keys() != FORMS.keys():
        return None
    fields.pop("conclusion")
    conclusion_packet = next(item["packet_id"] for item in evidence if item["role"] == "conclusion")
    return {
        "source_blob": inventory["source_blob"],
        "contract": asdict(Contract(**fields)),
        "claims": [{"claim_id": "Cdelta", "packet_id": conclusion_packet, "evidence": evidence}],
    }


def canonical_observations(size, prefix=()):
    if len(prefix) == size:
        yield prefix
        return
    for label in range(max(prefix, default=-1) + 2):
        yield from canonical_observations(size, (*prefix, label))


def counterexample(transition, observation, horizon):
    edges = {(observation[x], observation[target]) for x, target in enumerate(transition)}
    walks = {edge: edge for edge in sorted(edges)}
    for _ in range(1, horizon):
        walks = {
            (start, target): (*path, target)
            for (start, end), path in walks.items()
            for source, target in sorted(edges) if end == source
        }

    realized = set()
    for state, start in enumerate(observation):
        end = state
        for _ in range(horizon):
            end = transition[end]
        realized.add((start, observation[end]))

    gap = sorted(walks.keys() - realized)
    if gap:
        pair = gap[0]
        return {
            "T": list(transition), "pi": list(observation), "endpoints": list(pair),
            "observed_path": list(walks[pair]),
        }
    return None


def verify(contract, budget):
    checked = 0
    for size in range(1, contract.max_states + 1):
        if contract.observation == "injective":
            observations = [tuple(range(size))]
        else:
            observations = list(canonical_observations(size))
        for transition in product(range(size), repeat=size):
            for observation in observations:
                if checked == budget:
                    return {"status": "ABSTAIN_BUDGET", "systems_checked": checked}
                checked += 1
                witness = counterexample(transition, observation, contract.horizon)
                if witness:
                    return {"status": "REFUTED", "systems_checked": checked, "witness": witness}
    return {"status": "CONFIRMED_WITHIN_BOUND", "systems_checked": checked}


def evaluate(raw, path, *, arm="exact", proposal=None, budget=MAX_SYSTEMS):
    if arm not in ("direct", "exact") or type(budget) is not int or not 0 <= budget <= MAX_SYSTEMS:
        raise ValueError("Unsupported arm or system budget.")
    recognized = propose(raw, path)
    if recognized is None:
        return {"status": "ABSTAIN_UNSUPPORTED_OR_AMBIGUOUS_SOURCE", "systems_checked": 0}
    if proposal is not None and json.dumps(proposal, sort_keys=True) != json.dumps(recognized, sort_keys=True):
        return {"status": "ABSTAIN_CONTRACT_CITATION_MISMATCH", "systems_checked": 0}
    cited = gate(raw, path, {
        "source_blob": recognized["source_blob"], "claims": recognized["claims"],
    }, provider="delta-bridge")
    if cited["accepted_count"] != 1:
        return {"status": "ABSTAIN_REJECTED_CITATION", "systems_checked": 0}

    contract = Contract(**recognized["contract"])
    verdict = (
        {"status": "ASSERTED_WITHOUT_CHECK", "systems_checked": 0}
        if arm == "direct" else verify(contract, budget)
    )
    return {**verdict, "contract": asdict(contract), "source_blob": recognized["source_blob"],
            "evidence": cited["accepted"][0]["evidence"], "promotable": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--arm", choices=("exact", "direct"), default="exact")
    parser.add_argument("--proposal", type=Path, help="Optional JSON proposal to check against the source.")
    parser.add_argument("--emit-proposal", action="store_true")
    parser.add_argument("--budget", default=MAX_SYSTEMS, type=int)
    args = parser.parse_args()

    with args.source.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if args.emit_proposal:
        result = propose(raw, args.source.as_posix())
    else:
        proposal = None
        if args.proposal:
            with args.proposal.open("rb") as draft:
                data = draft.read(MAX_JSON_BYTES + 1)
            if len(data) > MAX_JSON_BYTES:
                parser.error("JSON proposal too large.")
            proposal = json.loads(data)
            if not isinstance(proposal, dict):
                parser.error("The proposal must be a JSON object.")
        result = evaluate(raw, args.source.as_posix(), arm=args.arm, proposal=proposal, budget=args.budget)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
