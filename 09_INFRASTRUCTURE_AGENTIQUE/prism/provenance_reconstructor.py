"""Conservative native tool for Omega's existing planner (no new orchestrator).

Evidence items may contain observed relationships from an external parser.
Only explicitly supported relationships are returned; never promote to proof.
"""
from collections import defaultdict


def reconstruct_provenance(dossier):
    items = dossier.get("evidence", [])
    if not isinstance(items, list):
        return {"status": "indéterminé", "relations": [], "errors": ["invalid_evidence"]}
    by_id = {}
    errors = []
    for item in items:
        if not isinstance(item, dict) or not item.get("id") or item["id"] in by_id:
            errors.append("missing_or_duplicate_id")
            continue
        by_id[item["id"]] = item
    relations = []
    for item_id, item in by_id.items():
        for parent in item.get("derived_from", []):
            if parent not in by_id:
                errors.append("unresolved_parent:" + str(parent))
                continue
            if parent == item_id:
                errors.append("self_dependency:" + item_id)
                continue
            relations.append({
                "from": parent, "to": item_id,
                "kind": "declared_dependency",
                "status": "observé_non_certifié",
                "evidence": [item_id],
            })
    # Do not equate same content hash with same execution or causal origin.
    by_hash = defaultdict(list)
    for item_id, item in by_id.items():
        if item.get("sha256"):
            by_hash[item["sha256"]].append(item_id)
    for ids in by_hash.values():
        if len(ids) > 1:
            relations.append({
                "members": sorted(ids), "kind": "same_content_digest",
                "status": "observé_non_certifié",
                "evidence": sorted(ids),
            })
    return {
        "status": "indéterminé" if errors else "observations_sans_certification",
        "relations": relations, "errors": sorted(set(errors)),
        "scientific_certification": False,
        "next_check": "Validate origins and causal execution traces independently.",
    }
