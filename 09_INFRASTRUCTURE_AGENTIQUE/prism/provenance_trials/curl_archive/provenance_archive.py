"""Correlate the known curl archive recipe with its GitHub execution trace."""

from hashlib import sha256
import re

UNKNOWN = "indéterminé"
RECIPE = "tests/cmake/test.sh"
RECIPE_HASHES = {
    "1cfd324c184754414096997c541c6ba0973e1c37":
        "15bd0498374856547ac50d9324c8e85f30c7a335a3af1db237ff09e27a3a7513",
}
TIMESTAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")


def archive_verdict(log, output, read_recipe):
    """Read the pinned recipe only when a successful verification is visible."""
    if not output.startswith("/") or not output.endswith("/tests/cmake/source.tar.gz"):
        return UNKNOWN
    lines = [TIMESTAMP.sub("", line) for line in log.splitlines()]
    transcript = "\n".join(lines)
    checkouts = list(re.finditer(
        r"^\[command\]/usr/bin/git log -1 --format=%H\n([0-9a-f]{40})$",
        transcript, re.MULTILINE,
    ))
    if len(checkouts) != 1 or checkouts[0][1] not in RECIPE_HASHES:
        return UNKNOWN

    target = re.escape(output)
    event = (
        r"^\+ cd -- \./tests/cmake\n\+ mode=ExternalProject\n"
        r"(?:\+ [^\n]*\n){0,16}"
        r"(?:\+ git archive --format=tar HEAD\n\+ gzip|"
        r"\+ gzip\n\+ git archive --format=tar HEAD)\n"
        r"\+ pwd\n\+ src=" + target + r"\n\+ sha256sum " + target
        + r"\n\+ grep [^\n]*\n\+ sha=([0-9a-f]{64})$"
    )
    matches = list(re.finditer(event, transcript, re.MULTILINE))
    if len(matches) != 1:
        return UNKNOWN
    if checkouts[0].end() >= matches[0].start():
        return UNKNOWN
    after = transcript[matches[0].end():]
    digest = matches[0][1]
    invocation = rf"^\+ .* -DFROM_ARCHIVE={target} -DFROM_HASH={digest}$"
    verify = rf"^-- verifying file\.\.\.\n +file='{target}'\n-- verifying file\.\.\. done$"
    command = re.search(invocation, after, re.MULTILINE)
    if command is None or not re.search(verify, after[command.end():], re.MULTILINE):
        return UNKNOWN

    commit = checkouts[0][1]
    recipe = read_recipe(commit, RECIPE)
    if recipe is None or sha256(recipe).hexdigest() != RECIPE_HASHES[commit]:
        return UNKNOWN
    return "recalcul"
