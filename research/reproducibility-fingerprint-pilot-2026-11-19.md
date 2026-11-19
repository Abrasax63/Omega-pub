# Reproducibility fingerprint pilot (2026-11-19)

Status: **experimental / not a scientific certificate**. This branch does not change `main`.

## Contract
The manifest contains schema_version=1, result_id, code_sha256, data_sha256,
parameters, dependencies, and execution. SHA-256 is computed over sorted-key
UTF-8 JSON with a domain prefix. Unknown/missing fields, floating point values,
and unsupported schema versions fail closed. Reuse is permitted only if both
the recorded manifest and the proposed current manifest match the recorded
fingerprint.

## Test
Run `python -m unittest discover -s tests -p 'test_repro_fingerprint.py' -v`.
Eleven tests cover unchanged manifests, field order, parameters, dependencies,
execution, code/data changes, malformed metadata and corrupt stored fingerprints.

## Limitations
This is an isolated proof of concept, not integrated with Omega's actual cache,
CI workflows, provenance graph or scientific status engine. The caller must
provide **complete** dependency closure (including environment, toolchain and
external inputs); omitted factors cannot be detected. SHA-256 attests identity,
not truth or independent verification. No migration to Lean 4.36.0 or evaluation
of Nextflow/AiiDA has been performed. No results should be promoted on this basis.

## Next falsification
Run an actual Omega computation twice with an unchanged complete manifest,
then change one dependency while preserving all other inputs. Verify the real
scheduler rejects reuse, keeps both historical records, and requires fresh
independent validation.
