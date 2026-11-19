#!/usr/bin/env python3
"""Omega Reader21 web access: bounded, read-only, allowlisted research requests.

An explicit capability, *not* an unrestricted browser or arbitrary fetch(url).
Data returned by outside pages is untrusted and may NEVER execute instructions,
promote scientific statuses, or modify repository files.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

MAX_BODY_BYTES = 262144
MAX_QUERY_CHARS = 120
TIMEOUT_SECONDS = 10
MAX_RESULTS = 3
ALLOWED_HOSTS = frozenset(("api.crossref.org", "raw.githubusercontent.com"))
MARKDOWN_PATH = "02_MATHEMATIQUES/observabilite_temporelle/OBS-V8-FACT-INF.md"
REPO_OWNER = "Abrasax63"
REPO_NAME = "Omega-pub"
CROSSREF_TERM = "finite dynamical systems observability"


class NetworkPolicyError(ValueError):
    pass


class NetworkFetchFailed(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise NetworkPolicyError("REDIRECT_REJECTED")


def validate_fixed_url(url: str, *, source_kind: str) -> None:
    """Strict validation of *constructed* URLs, never arbitrary URL input."""
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.username or parsed.password or
        parsed.hostname not in ALLOWED_HOSTS or parsed.port not in (None, 443) or
        parsed.fragment or parsed.netloc != parsed.hostname):
        raise NetworkPolicyError("BLOCKED_URL_SCHEME_HOST_OR_AUTHORITY")
    if source_kind == "crossref":
        if parsed.hostname != "api.crossref.org" or parsed.path != "/works":
            raise NetworkPolicyError("ONLY_CROSSREF_WORKS_ALLOWED")
        values = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
        if set(values) != {"query.bibliographic", "rows", "select"}:
            raise NetworkPolicyError("INVALID_CROSSREF_QUERY")
        if len(values["query.bibliographic"]) != 1 or not validate_query(values["query.bibliographic"][0]):
            raise NetworkPolicyError("INVALID_CROSSREF_QUERY_TERM")
        if values["rows"] != [str(MAX_RESULTS)] or values["select"] != ["DOI,title,issued,URL,type"]:
            raise NetworkPolicyError("CROSSREF_EXTRA_PARAMETERS_BLOCKED")
    elif source_kind == "repo_markdown":
        expected = f"/{REPO_OWNER}/{REPO_NAME}/main/{MARKDOWN_PATH}"
        if parsed.hostname != "raw.githubusercontent.com" or parsed.path != expected or parsed.query:
            raise NetworkPolicyError("REPO_PATH_NOT_IN_ALLOWLIST")
    else:
        raise NetworkPolicyError("UNKNOWN_SOURCE_KIND")


def validate_query(q: str) -> bool:
    return (
        isinstance(q, str) and 3 <= len(q) <= MAX_QUERY_CHARS
        and q.isascii()
        and bool(re.fullmatch(r"[A-Za-z0-9 .,'()+\-/]+", q))
    )


def crossref_url(query: str) -> str:
    if not validate_query(query):
        raise NetworkPolicyError("UNSAFE_BIBLIOGRAPHIC_QUERY")
    params = urllib.parse.urlencode({
        "query.bibliographic": query,
        "rows": str(MAX_RESULTS),
        "select": "DOI,title,issued,URL,type",
    })
    url = "https://api.crossref.org/works?" + params
    validate_fixed_url(url, source_kind="crossref")
    return url


def repository_url() -> str:
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{MARKDOWN_PATH}"
    validate_fixed_url(url, source_kind="repo_markdown")
    return url


def opener():
    """Ignore environment proxy; do not permit HTTP redirects or cookies."""
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NoRedirect(),
    )


def fetch_bounded(url: str, *, source_kind: str, transport=None) -> tuple[bytes, str]:
    validate_fixed_url(url, source_kind=source_kind)
    transport = opener() if transport is None else transport
    request = urllib.request.Request(url, headers={
        "User-Agent": "OmegaReader21/0.1 (noncommercial research; github.com/Abrasax63/Omega-pub)",
        "Accept": "application/json" if source_kind == "crossref" else "text/plain",
        "Accept-Encoding": "identity",
        "Connection": "close",
    }, method="GET")
    with transport.open(request, timeout=TIMEOUT_SECONDS) as response:
        if response.geturl() != url:
            raise NetworkPolicyError("UNEXPECTED_FINAL_URL_REDIRECT")
        if response.status != 200:
            raise NetworkFetchFailed("REMOTE_STATUS_" + str(response.status))
        typ = response.headers.get("Content-Type", "").lower().split(";")[0].strip()
        if source_kind == "crossref":
            if typ not in ("application/json", "application/vnd.crossref-api-message+json"):
                raise NetworkPolicyError("UNEXPECTED_CROSSREF_CONTENT_TYPE")
        elif typ not in ("text/plain", "text/markdown", "application/octet-stream"):
            raise NetworkPolicyError("UNEXPECTED_MARKDOWN_CONTENT_TYPE")
        length_header = response.headers.get("Content-Length")
        if length_header:
            try:
                if int(length_header) > MAX_BODY_BYTES:
                    raise NetworkPolicyError("REMOTE_CONTENT_TOO_LARGE")
            except ValueError:
                raise NetworkPolicyError("INVALID_CONTENT_LENGTH")
        body = response.read(MAX_BODY_BYTES + 1)
        if len(body) > MAX_BODY_BYTES:
            raise NetworkPolicyError("REMOTE_BODY_EXCEEDED_LIMIT")
        return body, typ


def _now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def entry(url: str, kind: str, body: bytes, typ: str) -> dict:
    """Untrusted result; never a truth certificate, only a reproducible body hash."""
    out = {
        "status": "WEB_FETCHED_UNTRUSTED",
        "url": url, "kind": kind,
        "retrieved_utc": _now_utc(),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body), "content_type": typ,
        "untrusted_content": True, "automatic_scientific_promotion": False,
        "model_instructions_allowed": False, "paid_api": False,
    }
    if kind == "crossref":
        j = json.loads(body)
        if not isinstance(j, dict) or j.get("status") != "ok":
            raise NetworkFetchFailed("INVALID_CROSSREF_RESPONSE")
        items = j.get("message", {}).get("items", [])
        if not isinstance(items, list):
            raise NetworkFetchFailed("INVALID_CROSSREF_ITEMS")
        works = []
        for item in items[:MAX_RESULTS]:
            if not isinstance(item, dict):
                continue
            doi = item.get("DOI")
            if not isinstance(doi, str) or not re.fullmatch(r"10\.\d{4,9}/[^\s]{1,200}", doi, flags=re.I):
                continue
            title = item.get("title", [""])
            if not isinstance(title, list) or not title:
                continue
            name = title[0]
            if not isinstance(name, str):
                continue
            works.append({
                "doi": doi, "title": name[:400],
                "type": str(item.get("type",""))[:80],
                "issued": item.get("issued"),
                "metadata_only": True,
                "mathematical_validity": "NOT_VERIFIED",
            })
        out["works"] = works
    else:
        document = body.decode("utf-8", errors="strict")
        if not document.lstrip().startswith("#"):
            raise NetworkFetchFailed("REPO_RESPONSE_NOT_MARKDOWN")
        out["line_count"] = len(document.splitlines())
        out["title"] = document.splitlines()[0][:250]
        out["snippet"] = document[:500]
        out["source_truth_automatically_certified"] = False
    return out


def run_once(transport=None, *, query: str = CROSSREF_TERM,
             mode: str = "both") -> dict:
    """Agent-callable read-only search/fetch with fixed provider and request budget."""
    if mode not in ("both", "search", "source"):
        raise NetworkPolicyError("UNSUPPORTED_WEB_MODE")
    targets = []
    if mode in ("both", "search"):
        targets.append(("crossref", crossref_url(query)))
    if mode in ("both", "source"):
        targets.append(("repo_markdown", repository_url()))
    results = []
    for kind, url in targets:
        try:
            body, typ = fetch_bounded(url, source_kind=kind, transport=transport)
            results.append(entry(url, kind, body, typ))
        except Exception as exc:
            results.append({
                "status": "REMOTE_FETCH_FAILED",
                "url": url, "kind": kind, "error_type": type(exc).__name__,
                "error": str(exc)[:400], "untrusted_content": True,
                "automatic_scientific_promotion": False,
                "model_instructions_allowed": False,
            })
    return {
        "experiment": "OMEGA_READER21_ALLOWLISTED_WEB_CAPABILITY",
        "uses_paid_api": False, "http_requests_max": len(targets),
        "mode": mode, "bibliographic_query": query if mode != "source" else None,
        "arbitrary_url_fetch_enabled": False, "browser_or_search_engine": False,
        "sources_are_untrusted": True, "automatic_scientific_promotions": 0,
        "results": results,
        "real_fetch_success_count": sum(x["status"] == "WEB_FETCHED_UNTRUSTED" for x in results),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("both", "search", "source"), default="both")
    parser.add_argument("--query", default=CROSSREF_TERM,
                        help="Constrained public Crossref bibliographic query, never a URL")
    a = parser.parse_args()
    data = run_once(query=a.query, mode=a.mode)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("WEB_FETCHES", data["real_fetch_success_count"], "of", data["http_requests_max"])
    for v in data["results"]:
        print(v["kind"], v["status"], v.get("bytes"), v.get("error", ""))
    if data["real_fetch_success_count"] != data["http_requests_max"]:
        raise SystemExit("REMOTE_WEB_NOT_FULLY_CONFIRMED")


if __name__ == "__main__":
    main()
