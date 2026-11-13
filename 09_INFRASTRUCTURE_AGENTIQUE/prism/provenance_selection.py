"""Select a discriminating provenance observation under a read budget."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Piece:
    name: str
    kind: str
    job: str
    output: str


def select_verdict(pieces, read, *, job, output, budget=2):
    """Return a verdict and its read trace for a single job/output pair.

    The inventory is metadata visible before reads. Only a complete execution
    record can distinguish a write by a calculation from a write by a copy.
    """
    if budget < 0:
        raise ValueError("Le budget doit être positif ou nul.")
    candidates = [
        piece for piece in pieces
        if piece.job == job and piece.output == output and piece.kind == "execution"
    ]
    trace = []
    observed = set()
    for piece in candidates[:budget]:
        trace.append(piece.name)
        record = read(piece.name)
        if not isinstance(record, dict):
            continue
        if (
            record.get("job") != job or record.get("output") != output
            or record.get("complete") is not True or record.get("success") is not True
        ):
            continue
        operation = record.get("operation")
        if operation in ("recalcul", "copie"):
            observed.add(operation)
    # If the budget leaves applicable records unread, a conflict is still possible.
    verdict = observed.pop() if len(candidates) <= budget and len(observed) == 1 else "indéterminé"
    return {"verdict": verdict, "pieces_lues": trace}
