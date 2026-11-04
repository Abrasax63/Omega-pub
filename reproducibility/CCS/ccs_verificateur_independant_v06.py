"""CCS v0.6 : vérificateur indépendant pour certificats finis.
Ne fait confiance ni au verdict ni aux obligations fournies.
"""
import json, sys

def verify(cert):
    try:
        a=cert["source"]; b=cert["target"]; pairs=cert["pairs"]
        assert a["quantifier"] == b["quantifier"] and a["quantifier"] in ("forall","exists")
        da=a["domain"]; db=b["domain"]
        assert len(da)==len(set(da)) and len(db)==len(set(db))
        assert len(pairs)==len(da)==len(db)
        assert set(x for x,y in pairs)==set(da)
        assert set(y for x,y in pairs)==set(db)
        assert len(set(tuple(p) for p in pairs))==len(pairs)
        for x,y in pairs:
            ax=a["values"][str(x)]; by=b["values"][str(y)]
            assert type(ax["hypothesis"]) is bool and type(by["hypothesis"]) is bool
            assert ax["hypothesis"] == by["hypothesis"]
            if ax["hypothesis"]:
                assert type(ax["conclusion"]) is bool and type(by["conclusion"]) is bool
                assert ax["conclusion"] == by["conclusion"]
        assert set(a["values"])==set(map(str,da))
        assert set(b["values"])==set(map(str,db))
        return True
    except (AssertionError, KeyError, TypeError, ValueError):
        return False

if __name__=="__main__":
    c=json.load(open(sys.argv[1],encoding="utf8"))
    ok=verify(c)
    print("CERTIFICAT FINI VALIDE" if ok else "CERTIFICAT REJETE")
    sys.exit(0 if ok else 1)