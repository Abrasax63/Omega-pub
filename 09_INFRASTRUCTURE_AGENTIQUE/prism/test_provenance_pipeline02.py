"""Offline, adversarial coverage of the new experimental grammar."""
import unittest

from provenance_pipeline02 import UNKNOWN, fingerprints, learn, verify, fixed, score

SCRIPT = '''#!/usr/bin/env bash
(cd "./source"; git archive --format=tar HEAD) | gzip > source.tar.gz
'''
LOG = '''2026-11-15T05:01:53.241Z + git archive --format=tar HEAD
2026-11-15T05:01:53.242Z + gzip
2026-11-15T05:01:53.567Z + sha256sum /tmp/run/source.tar.gz
2026-11-15T05:01:53.570Z + cmake -DFROM_ARCHIVE=/tmp/run/source.tar.gz -DFROM_HASH=xyz
'''
CMAKE = 'add_executable(curl main.c)\n'
LINK = '[12/12] : && /usr/bin/cc -Wl,-z,relro -o src/curl lib/libcurl.a && :'


class SemanticProvenanceTests(unittest.TestCase):
    def test_archive_complete(self):
        self.assertTrue(fingerprints(LOG, SCRIPT, "source.tar.gz")["archive"])
        self.assertEqual(
            verify(LOG, SCRIPT, "source.tar.gz",
                   {"archive-pipeline": "recalcul"})["verdict"], "recalcul",
        )

    def test_missing_script_rejects(self):
        self.assertFalse(fingerprints(LOG, "", "source.tar.gz")["archive"])

    def test_wrong_target_rejects(self):
        self.assertFalse(fingerprints(LOG, SCRIPT, "other.tar.gz")["archive"])

    def test_missing_hash_rejects(self):
        self.assertFalse(fingerprints(
            LOG.replace("+ sha256sum", "+ echo"), SCRIPT, "source.tar.gz",
        )["archive"])

    def test_missing_use_rejects(self):
        self.assertFalse(fingerprints(
            LOG.replace("-DFROM_ARCHIVE", "-DOTHER_ARCHIVE"),
            SCRIPT, "source.tar.gz",
        )["archive"])

    def test_conflicting_second_writer_blocks_archive(self):
        log = LOG + "+ cp evil.tar source.tar.gz\n"
        self.assertFalse(fingerprints(log, SCRIPT, "source.tar.gz")["archive"])

    def test_simple_link(self):
        self.assertTrue(fingerprints(LINK, CMAKE, "src/curl")["link"])
        self.assertEqual(fixed(LINK, CMAKE, "src/curl"), "recalcul")

    def test_link_missing_source(self):
        self.assertFalse(fingerprints(LINK, "", "src/curl")["link"])

    def test_link_other_output(self):
        self.assertFalse(fingerprints(
            LINK.replace("-o src/curl", "-o src/notcurl"),
            CMAKE, "src/curl",
        )["link"])

    def test_unknown_docker(self):
        self.assertEqual(
            fixed("[command]/usr/bin/docker buildx build --output type=image",
                  "", "src/curl"), UNKNOWN,
        )

    def test_learns_only_unambiguous(self):
        corpus = [
            {"log": LOG, "script": SCRIPT, "output": "source.tar.gz",
             "expected": "recalcul"},
            {"log": LINK, "script": CMAKE, "output": "src/curl",
             "expected": "recalcul"},
        ]
        self.assertEqual(learn(corpus), {
            "archive-pipeline": "recalcul", "ninja-link": "recalcul",
        })
        corpus.append({
            "log": LOG, "script": SCRIPT, "output": "source.tar.gz",
            "expected": "copie",
        })
        self.assertNotIn("archive-pipeline", learn(corpus))

    def test_fixed_parity(self):
        corpus = [
            {"log": LOG, "script": SCRIPT, "output": "source.tar.gz",
             "expected": "recalcul"},
            {"log": LINK, "script": CMAKE, "output": "src/curl",
             "expected": "recalcul"},
        ]
        result = score(
            [dict(row, id=str(i)) for i, row in enumerate(corpus)],
            learn(corpus),
        )
        self.assertFalse(result["recommend_for_review"])
        self.assertEqual(result["candidate"], result["fixed"])


if __name__ == "__main__":
    unittest.main()
