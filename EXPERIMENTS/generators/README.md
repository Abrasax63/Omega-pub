# T1/T3 Python generators v0.1

- t1_t3_generators.py: task generators and separated public/private payloads.
- test_t1_t3_generators.py: standard-library unit tests.

Run from this directory:

    python -m unittest -v

Send only task.public_payload() to the evaluated model. Keep
task.evaluation_payload() private for scoring.

These tests validate the generators only. They do not compare the three
experimental configurations (single model, fixed-role Omega, adaptive Omega).
