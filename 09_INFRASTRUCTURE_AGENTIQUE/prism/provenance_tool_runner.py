"""Explicit, read-only execution of a tool selected by Omega's P1 planner.

This does not execute perspectives or spawn autonomous agents.
"""
from provenance_reconstructor import reconstruct_provenance


def run_selected_provenance_tool(plan, dossier):
    selected = [item for item in plan.get("tools", [])
                if item.get("name") == "reconstruct_provenance"]
    if not selected:
        return {"status": "not_selected", "tool_executed": False, "relations": []}
    if len(selected) != 1 or plan.get("planner") != "omega-adaptive-prism":
        raise ValueError("Invalid provenance tool selection")
    result = reconstruct_provenance(dossier)
    return {"status": "executed_read_only", "tool_executed": True,
            "tool": "reconstruct_provenance", "result": result,
            "scientific_certification": False}
