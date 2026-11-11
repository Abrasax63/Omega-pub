"""Offline data-quality and methodological regression tests for ASlib external CV."""
import math
import unittest

from aslib_external_benchmark import (
    read_arff,git_blob_sha,train_normalizer,normalize,
    _best_algo,select_knn,score_measurement,
    BLOBS,UPSTREAM_COMMIT,METHODS,
)


class AslibExternalHarnessTests(unittest.TestCase):
    def make_data(self):
        ids=["aa","ab","cc","zz"]
        a={
            "ids":ids,"algorithms":("A","B"),
            "features":{i:tuple([v]*37) for i,v in zip(ids,(0.,1.,2.,500.))},
            "runs":{
                "aa":{"A":(1., "ok"),"B":(9., "ok")},
                "ab":{"A":(2., "ok"),"B":(8., "ok")},
                "cc":{"A":(9., "ok"),"B":(1., "ok")},
                "zz":{"A":(18000., "timeout"),"B":(3., "ok")},
            },
            "folds":{"aa":1,"ab":1,"cc":1,"zz":2},
            "costs":{i:0.25 for i in ids},
        }
        return a

    def test_parser_rejects_width_and_accepts_full_arff(self):
        head=("""@RELATION sample
@ATTRIBUTE instance_id STRING
@ATTRIBUTE repetition NUMERIC
@ATTRIBUTE v NUMERIC
@DATA
'alpha',1,1.25
beta,1,?
""")
        attrs,rows=read_arff(head)
        self.assertEqual(attrs,["instance_id","repetition","v"])
        self.assertEqual(rows[0]["instance_id"],"alpha")
        self.assertEqual(rows[1]["v"],"?")
        with self.assertRaises(ValueError):
            read_arff(head+"broken,1\n")

    def test_normalization_train_only_and_outlier_robust_to_test_label_changes(self):
        data=self.make_data()
        norm=train_normalizer(["aa","ab","cc"],data)
        self.assertEqual(norm[0][0],1)
        self.assertAlmostEqual(norm[1][0],1)
        x=normalize(data["features"]["zz"],norm)
        self.assertEqual(x[0],10.0)
        self.assertEqual(len(x),37)
        self.assertEqual(normalize(data["features"]["aa"],norm),normalize(
            data["features"]["aa"],train_normalizer(["aa","ab","cc"],data)))
        altered=self.make_data()
        altered["runs"]["zz"]={"A":(1.,"ok"),"B":(18000.,"timeout")}
        self.assertEqual(_best_algo(["aa","ab","cc"],data),
                         _best_algo(["aa","ab","cc"],altered))
        norm2=train_normalizer(["aa","ab","cc"],altered)
        self.assertEqual(norm,norm2)

    def test_knn_does_not_read_test_performance_when_choosing(self):
        a=self.make_data()
        b=self.make_data()
        b["runs"]["zz"]["A"]=(0.5,"ok")
        b["runs"]["zz"]["B"]=(18000.,"timeout")
        norm=train_normalizer(["aa","ab","cc"],a)
        va={i:normalize(a["features"][i],norm) for i in a["ids"]}
        vb={i:normalize(b["features"][i],norm) for i in b["ids"]}
        self.assertEqual(select_knn(["aa","ab","cc"],"zz",a,va,1),
                         select_knn(["aa","ab","cc"],"zz",b,vb,1))
        self.assertEqual(select_knn(["aa","ab","cc"],"zz",a,va,3),
                         select_knn(["aa","ab","cc"],"zz",b,vb,3))

    def test_par10_and_feature_cost_not_double_counted_for_sbs(self):
        data=self.make_data()
        total,ok,raw,feature=score_measurement("zz","A",data,True)
        self.assertEqual((total,ok,raw,feature),(18000.25,False,18000.,0.25))
        total,ok,raw,feature=score_measurement("zz","A",data,False)
        self.assertEqual((total,ok,raw,feature),(18000.,False,18000.,0.))

    def test_sources_are_immutably_pinned_and_methods_prespecified(self):
        self.assertEqual(len(UPSTREAM_COMMIT),40)
        self.assertEqual(len(BLOBS),5)
        self.assertTrue(all(len(sha)==40 for sha in BLOBS.values()))
        self.assertIn("OMEGA_finite_v0",METHODS)
        self.assertIn("VBS_oracle",METHODS)
        self.assertEqual(git_blob_sha(b"hello"),
                         "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")


if __name__=="__main__":
    unittest.main()
