"""Python 3.6-compatible instrumented ORIGINAL buggy pytest run.

No fixed commit, patch, network, or model access. Writes one JSON marker to stdout.
"""
from __future__ import print_function
import json
import os
import sys
import time
import traceback

MARKER="OMEGA_TRACE_JSON="
MAX_EVENTS=250000

def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: trace_runner.py /tmp/work tqdm/tests/tests_tqdm.py::test_bool")
    root=os.path.realpath(sys.argv[1])
    package=os.path.join(root,"tqdm")+os.sep
    test=sys.argv[2]
    import pytest

    records={}
    events=[0]
    truncated=[False]
    start=time.monotonic()

    def tracer(frame,event,arg):
        path=os.path.realpath(frame.f_code.co_filename)
        if not path.startswith(package) or os.sep+"tests"+os.sep in path:
            return None
        def package_tracer(frame,event,arg):
            if event=="line":
                events[0]+=1
                if events[0]>MAX_EVENTS:
                    truncated[0]=True
                    return None
                key=(os.path.relpath(path,root).replace(os.sep,"/"),frame.f_lineno)
                old=records.get(key)
                if old is None:
                    records[key]={"path":key[0],"line":key[1],"count":1,"last":events[0]}
                else:
                    old["count"]+=1
                    old["last"]=events[0]
            return package_tracer
        return package_tracer

    sys.settrace(tracer)
    try:
        status=int(pytest.main(["-q","-p","no:cacheprovider","--tb=short",
                               "--maxfail=1",test]))
    except Exception:
        traceback.print_exc()
        status=90
    finally:
        sys.settrace(None)

    elapsed=time.monotonic()-start
    evidence={
        "event_count":events[0],
        "truncated":truncated[0],
        "elapsed_seconds":round(elapsed,6),
        "test_exit":status,
        "lines":sorted(records.values(),key=lambda x:(x["path"],x["line"])),
    }
    print(MARKER+json.dumps(evidence,sort_keys=True,separators=(",",":")))
    sys.stdout.flush()
    return status

if __name__=="__main__":
    sys.exit(main())
