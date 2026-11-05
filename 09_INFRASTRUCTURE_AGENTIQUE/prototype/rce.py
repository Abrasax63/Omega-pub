#!/usr/bin/env python3
"""Read-only Research Context Engine prototype for Omega-pub.

Standard-library only. Reads a local repository checkout and emits a
provenance-preserving JSON context bundle. It never edits repository files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
INDEX_PATH = "00_GOUVERNANCE/INDEX_GLOBAL.md"
REGISTER_PATH = "00_GOUVERNANCE/REGISTRE_TRANSVERSAL.md"
SKIP_DIRS = {".git", ".github", ".venv", "venv", "__pycache__", "node_modules",
             "dist", "build", ".pytest_cache"}
SKIP_PARTS = {"private", "prive", "secret", "secrets"}
ALLOWED_SUFFIXES = {".md", ".py", ".lean", ".json", ".yaml", ".yml", ".toml", ".csv"}
STOPWORDS = {
    "avec", "dans", "pour", "sans", "chez", "cela", "cette", "comme", "comment",
    "quel", "quelle", "quels", "quelles", "nous", "vous", "leur", "leurs", "des",
    "les", "une", "uns", "sur", "sous", "entre", "depuis", "vers", "mais", "donc",
    "alors", "plus", "moins", "être", "avoir", "faire", "est", "sont", "qui", "que",
    "quoi", "dont", "par", "pas", "non", "oui", "the", "and", "for", "with", "from",
    "this", "that", "into", "are", "was", "were", "can", "how", "what"
}
ROLE_TERMS = {
    "researcher": ["lacune", "piste", "résultat", "conjecture", "littérature", "hypothèse"],
    "refuter": ["réfut", "contre-exemple", "objection", "limite", "échec", "contradiction"],
    "formalist": ["définition", "hypothèse", "preuve", "énoncé", "lemme", "théorème", "lean"],
    "computational": ["code", "script", "calcul", "donnée", "sortie", "reproductibilité", "simulation"],
    "bibliographer": ["source", "référence", "bibliographie", "doi", "publication", "littérature"],
}
ROLE_GUIDANCE = {
    "researcher": "Cartographier l'état des connaissances et les lacunes. Distinguer acquis, pistes et inconnues.",
    "refuter": "Chercher d'abord les hypothèses fragiles, objections, contre-exemples, corrections et résultats négatifs.",
    "formalist": "Préserver les définitions et hypothèses exactes. Ne pas renforcer un énoncé ni combler une lacune par intuition.",
    "computational": "Repérer code, données, commandes et sorties. Ne jamais prétendre qu'un calcul a été exécuté s'il ne l'a pas été.",
    "bibliographer": "Identifier les sources primaires et les références à vérifier. Ne pas inférer la nouveauté à partir d'une recherche incomplète.",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(c for c in value if not unicodedata.combining(c))


def terms(value: str) -> list[str]:
    found = re.findall(r"[a-zA-ZÀ-ÿ0-9_./-]+", normalize(value))
    return [t for t in found if len(t) > 1 and t not in STOPWORDS]


def safe_repo_path(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if any(part.casefold() in SKIP_PARTS for part in candidate.parts):
        return None
    return candidate


def markdown_tables(text: str):
    """Yield (header, rows) for simple pipe tables."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        line = lines[i].strip()
        if not (line.startswith("|") and line.endswith("|")):
            i += 1
            continue
        header = [c.strip() for c in line.strip("|").split("|")]
        sep = lines[i + 1].strip()
        if not (sep.startswith("|") and re.fullmatch(r"[\s|:-]+", sep)):
            i += 1
            continue
        rows = []
        j = i + 2
        while j < len(lines):
            rowline = lines[j].strip()
            if not (rowline.startswith("|") and rowline.endswith("|")):
                break
            cells = [c.strip() for c in rowline.strip("|").split("|")]
            if len(cells) == len(header):
                rows.append(dict(zip(header, cells)))
            j += 1
        yield header, rows
        i = max(j, i + 1)


def clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value)).strip()


def local_markdown_link(cell: str, source_file: Path, root: Path) -> str | None:
    match = re.search(r"\[[^\]]*\]\(([^)]+)\)", cell)
    if not match:
        return None
    target = match.group(1).split("#", 1)[0]
    if not target or re.match(r"^[a-z]+://", target, re.I):
        return None
    try:
        return (source_file.parent / target).resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


def load_registered_results(root: Path) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for rel in (INDEX_PATH, REGISTER_PATH):
        path = safe_repo_path(root, rel)
        if not path or not path.is_file():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for _, rows in markdown_tables(content):
            for row in rows:
                identifier = clean_cell(row.get("ID", ""))
                if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,80}", identifier):
                    continue
                record = records.setdefault(identifier, {
                    "id": identifier,
                    "epistemic_space": "experimental_internal",
                    "classification_basis": "Conservatively classified as experimental until an explicit certification record is parsed.",
                    "source_refs": [],
                })
                aliases = {
                    "domain": ("Domaine",),
                    "title": ("Énoncé / titre", "Énoncé court", "Résultat / dossier"),
                    "scientific_status_source": ("Statut scientifique source",),
                    "publication_status": ("Statut de publication", "Publication"),
                    "version": ("Version",),
                    "evidence": ("Preuve / audit",),
                    "dependencies": ("Dépendances",),
                    "keywords": ("Mots-clés",),
                }
                for dest, keys in aliases.items():
                    for key in keys:
                        if row.get(key):
                            value = clean_cell(row[key])
                            if value and value != "—":
                                record.setdefault(dest, value)
                            break
                source_ref = {"path": rel, "kind": "governance_index"}
                if source_ref not in record["source_refs"]:
                    record["source_refs"].append(source_ref)
                link_cell = row.get("Fiche") or row.get("Fiche / source") or ""
                target = local_markdown_link(link_cell, path, root)
                if target:
                    record["source_file"] = target
    return sorted(records.values(), key=lambda item: item["id"])


def load_pending_items(root: Path) -> list[dict[str, Any]]:
    path = safe_repo_path(root, REGISTER_PATH)
    if not path or not path.is_file():
        return []
    content = path.read_text(encoding="utf-8", errors="replace")
    pending = []
    # Select by the table's explicit schema rather than relying on heading
    # boundaries; this remains stable if explanatory headings are inserted.
    for header, rows in markdown_tables(content):
        if "Identifiants / dossier" not in header:
            continue
        for row in rows:
            identifier = clean_cell(row.get("Identifiants / dossier", ""))
            if identifier:
                pending.append({
                    "id": identifier,
                    "domain": clean_cell(row.get("Domaine", "")),
                    "documentary_state": clean_cell(row.get("État documentaire", "")),
                    "required_before_registration": clean_cell(row.get("Condition avant inscription comme fiche", "")),
                    "epistemic_space": "experimental_internal",
                    "scientific_status_source": "NON ÉTABLI — élément en attente de migration",
                    "source_refs": [{"path": REGISTER_PATH, "kind": "pending_migration_register"}],
                })
    return pending


def iter_documents(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS or part.casefold() in SKIP_PARTS for part in rel.parts):
            continue
        if path.name.casefold() in {".env", ".env.local", "secrets.json"}:
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError):
            continue
        yield rel.as_posix(), content


def score_document(query_terms: list[str], content: str, rel: str, role: str) -> tuple[float, list[str]]:
    haystack = normalize(content)
    path_text = normalize(rel)
    hits = [term for term in query_terms if term in haystack]
    path_hits = [term for term in query_terms if term in path_text]
    score = len(set(hits)) + 2.0 * len(set(path_hits))
    if role in ROLE_TERMS:
        role_hits = sum(1 for term in ROLE_TERMS[role] if normalize(term) in haystack)
        score += min(role_hits, 5) * 0.35
    if "08_ARCHIVES/" in rel:
        score *= 0.55
    return score, sorted(set(hits + path_hits))


def excerpts(content: str, query_terms: list[str], limit: int = 3, radius: int = 2):
    lines = content.splitlines()
    selected = []
    matched = [i for i, line in enumerate(lines)
               if any(term in normalize(line) for term in query_terms)]
    if not matched and lines:
        matched = [0]
    for idx in matched:
        lo, hi = max(0, idx - radius), min(len(lines), idx + radius + 1)
        if selected and lo <= selected[-1][1]:
            selected[-1] = (selected[-1][0], max(selected[-1][1], hi))
        else:
            selected.append((lo, hi))
        if len(selected) >= limit:
            break
    return [{"line_start": lo + 1, "line_end": hi, "text": "\n".join(lines[lo:hi])}
            for lo, hi in selected]


def build_context(root: Path, question: str, role: str, max_documents: int = 12) -> dict[str, Any]:
    query_terms = terms(question)
    if not query_terms:
        raise ValueError("La question ne contient aucun terme de recherche exploitable.")
    results = load_registered_results(root)
    pending = load_pending_items(root)
    documents = []
    for rel, content in iter_documents(root):
        score, matched = score_document(query_terms, content, rel, role)
        if score <= 0:
            continue
        documents.append({
            "path": rel,
            "score": round(score, 3),
            "matched_terms": matched,
            "excerpts": excerpts(content, query_terms),
            "epistemic_space": "experimental_internal" if rel.startswith("08_ARCHIVES/") else "internal_document",
            "source_kind": "repository_document",
        })
    documents.sort(key=lambda item: (-item["score"], item["path"]))
    documents = documents[:max_documents]

    normalized_question = normalize(question)
    relevant_results = []
    for record in results:
        searchable = normalize(" ".join(str(v) for k, v in record.items()
                                        if k not in {"source_refs"}))
        matched = [term for term in query_terms if term in searchable]
        if matched or any(term in normalized_question for term in terms(record["id"])):
            relevant_results.append({**record, "matched_terms": matched})
    relevant_pending = []
    for item in pending:
        searchable = normalize(" ".join(str(v) for v in item.values()))
        matched = [term for term in query_terms if term in searchable]
        if matched:
            relevant_pending.append({**item, "matched_terms": matched})

    payload = {
        "manifest": {
            "engine": "Omega-pub Research Context Engine prototype",
            "engine_version": VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "repository_root_name": root.name,
            "mode": "read_only_local_checkout",
            "query_terms": query_terms,
            "role": role,
            "content_hash": None,
        },
        "mission": {"question": question, "role": role, "role_guidance": ROLE_GUIDANCE[role]},
        "coverage": {
            "registered_results_loaded": len(results),
            "registered_results_returned": len(relevant_results),
            "pending_migration_items_loaded": len(pending),
            "pending_migration_items_returned": len(relevant_pending),
            "repository_documents_scanned": sum(1 for _ in iter_documents(root)),
            "repository_documents_returned": len(documents),
            "external_sources_queried": 0,
            "limitations": [
                "Recherche lexicale locale uniquement ; aucune recherche sémantique ni connexion web.",
                "Les résultats de l'index sont classés prudemment en mémoire expérimentale tant qu'une certification explicite n'est pas interprétée.",
                "Les documents trouvés ne sont pas automatiquement des résultats scientifiques.",
                "Les fichiers non présents dans ce checkout ne sont pas consultés.",
            ],
        },
        "registered_results": relevant_results,
        "pending_migration_items": relevant_pending,
        "candidate_documents": documents,
        "external_sources": [],
        "independence_warning": "La répétition d'une affirmation dans plusieurs documents ou par plusieurs agents ne constitue pas une vérification indépendante.",
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["manifest"]["content_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Racine du checkout Omega-pub")
    parser.add_argument("--question", required=True, help="Question ou mission de recherche")
    parser.add_argument("--role", choices=sorted(ROLE_GUIDANCE), default="researcher")
    parser.add_argument("--max-documents", type=int, default=12)
    parser.add_argument("--output", type=Path, help="Fichier JSON de sortie ; stdout par défaut")
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    if not root.is_dir():
        parser.error(f"Le dépôt indiqué n'est pas un dossier : {root}")
    try:
        payload = build_context(root, args.question, args.role, max(1, args.max_documents))
    except (OSError, ValueError) as exc:
        print(f"RCE error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        destination = args.output.resolve()
        try:
            destination.relative_to(root)
        except ValueError:
            pass
        else:
            parser.error("Le fichier de sortie doit être situé hors du dépôt : le prototype reste strictement en lecture seule.")
        destination.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
