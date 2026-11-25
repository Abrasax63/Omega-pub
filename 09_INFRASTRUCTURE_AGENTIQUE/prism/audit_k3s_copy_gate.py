"""Narrow K3s development diagnostic; workflow receipts must be independently checked."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from provenance_xtrace import extract, fixed_verdict

SOURCE = "scripts/airgap/image-list.txt"
OUTPUT = "dist/artifacts/k3s-images.txt"
COMMAND = f"cp {SOURCE} {OUTPUT}"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
TIMESTAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")


def qualifies(log, source, workflow, receipt):
    lines = [ANSI.sub("", TIMESTAMP.sub("", line)).strip() for line in log.splitlines()]
    publication = workflow.find("run: gh release create ")
    return (
        publication >= 0
        and len(lines) >= 4
        and lines[0] == "##[group]Run " + COMMAND
        and lines[1] == COMMAND
        and lines[-1] == "##[endgroup]"
        and lines.count("shell: /usr/bin/bash -e {0}") == 1
        and re.findall(r"^\s*([^\n]*\bk3s-images\.txt[^\n]*)$", workflow[:publication], re.M) == [COMMAND]
        and receipt["copy_ok"] is True
        and receipt["publish_ok"] is True
        and len(source) == receipt["asset_size"]
        and sha256(source).hexdigest() == receipt["asset_sha"]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stem")
    args = parser.parse_args()
    stem = args.stem
    receipt = json.loads(Path(f"{stem}.json").read_text())
    log = Path(f"{stem}-step.log").read_text()
    source = Path(f"{stem}-source.txt").read_bytes()
    workflow = Path(f"{stem}-workflow.yml").read_text()
    accepted = qualifies(log, source, workflow, receipt)
    adverse = (
        qualifies(log.replace(SOURCE, SOURCE + ".missing", 2), source, workflow, receipt),
        qualifies(log, bytes([source[0] ^ 1]) + source[1:], workflow, receipt),
        qualifies(log, source, workflow.replace(COMMAND, COMMAND + "\n        touch " + OUTPUT), receipt),
    )
    assert accepted and not any(adverse)
    normalized = Path(f"{stem}-normalized.log")
    normalized.write_text("+ " + COMMAND + "\n" + f"# receipt {receipt['commit']}\n")
    manifest = [dict(journal=normalized.name, output=OUTPUT, expected="copie",
                     source=receipt["source"], truth_source=receipt["truth_source"],
                     sha256=sha256(normalized.read_bytes()).hexdigest(),
                     format="bash-step", successful_errexit_step=True)]
    Path(f"{stem}-manifest.json").write_text(json.dumps(manifest) + "\n")
    print(json.dumps(dict(raw_fixed=fixed_verdict(extract(log, OUTPUT)),
                          normalized_fixed=fixed_verdict(extract(normalized.read_text(), OUTPUT)),
                          rejected_controls=sum(not value for value in adverse),
                          input_sha256=sha256(source).hexdigest()), ensure_ascii=False))


if __name__ == "__main__":
    main()
