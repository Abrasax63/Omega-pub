"""Optional v2 model-code reader, fail closed, with explicit format provenance.

Prepared for a NEW independent evaluation cohort. Does NOT change frozen
reader, original scores, or any run in PR #242. No LLM calls or gradients.
"""
from __future__ import annotations


def normalize_escaped_line_separators(source: str, max_chars: int) -> tuple[str | None, str]:
    """Recover literal backslash-n separators outside quoted strings only.

    Narrowly scoped to one-line escaped Python functions. Do not rewrite a real
    newline, triple quote, any backslash inside a string, or other escapes.
    Validation by an independent AST sandbox MUST follow before admission.
    """
    if (not isinstance(source, str) or len(source) > max_chars
            or "\n" in source or "\r" in source
            or not source.startswith("def transform(s):\\n")
            or source.count("\\n") > 100
            or "'''" in source or '"""' in source):
        return None, "NO_UNAMBIGUOUS_ESCAPED_LINE_FORMAT"
    result = []
    quote = None
    index = 0
    converted = 0
    while index < len(source):
        ch = source[index]
        if quote is not None:
            if ch == "\\" and index + 1 < len(source):
                result.extend((ch, source[index+1]))
                index += 2
                continue
            if ch == quote:
                quote = None
            result.append(ch)
            index += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            result.append(ch)
            index += 1
            continue
        if ch == "\\" and index+1 < len(source) and source[index+1] == "n":
            result.append("\n")
            converted += 1
            index += 2
            continue
        result.append(ch)
        index += 1
    if converted == 0 or quote is not None:
        return None, "AMBIGUOUS_ESCAPED_LINE_FORMAT"
    return "".join(result), "ESCAPED_LINES_NORMALIZED"


def inspect_candidate(raw: str, safe) -> tuple[str | None, str]:
    """Return (safe code or None, audit status).

    safe is the existing sandbox from PR #232: parse_code(),
    validate_program() and MAX_CODE_CHARS. The model cannot change these checks.
    A format-only recovery is not model learning or semantic correction.
    """
    code = safe.parse_code(raw)
    if not isinstance(code, str):
        return None, "INVALID_JSON_OR_CODE"
    try:
        safe.validate_program(code)
        return code, "SAFE_PYTHON_UNCHANGED"
    except ValueError as exc:
        if str(exc) != "INVALID_PYTHON_SYNTAX":
            return None, "UNSAFE_OR_INVALID_CODE:" + str(exc)
    candidate, status = normalize_escaped_line_separators(code, safe.MAX_CODE_CHARS)
    if candidate is None:
        return None, status
    try:
        safe.validate_program(candidate)
    except ValueError as exc:
        return None, "NORMALIZED_CODE_REJECTED:" + str(exc)
    return candidate, "SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING"
