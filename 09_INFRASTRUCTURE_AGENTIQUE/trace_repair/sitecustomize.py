"""Read-only call profiler loaded with PYTHONPATH=/probe:/tmp/work.

Designed for Python 3.6/3.8 historical project containers. Uses sys.setprofile
rather than sys.settrace to avoid competing with pytest-cov's coverage tracer.
Output is an atexit JSON line in the *existing pytest stderr*; this does not
modify the tested files or replace upstream assertions.
"""
import atexit
import json
import os
import sys

PREFIX = os.environ.get("OMEGA_TRACE_ROOT","")
MAGIC = "OMEGA_CALL_TRACE_V1="
FILE_LIMIT = 100
FUNCTION_LIMIT = 250
calls = {}
if PREFIX:
    PREFIX = os.path.realpath(PREFIX) + os.sep

def _profile(frame, event, arg):
    if event != "call":
        return
    code=frame.f_code
    location=os.path.realpath(code.co_filename)
    if not PREFIX or not location.startswith(PREFIX):
        return
    relative=os.path.relpath(location, PREFIX)
    if relative.startswith(".."):
        return
    if relative not in calls:
        if len(calls)>=FILE_LIMIT:
            return
        calls[relative]={}
    name=code.co_name
    key=name+"@"+str(code.co_firstlineno)
    dest=calls[relative]
    if key not in dest and len(dest)>=FUNCTION_LIMIT:
        return
    dest[key]=dest.get(key,0)+1

def _emit():
    if not PREFIX:
        return
    output={"schema":"omega-calltrace-v1","root":PREFIX,
            "files":[{"path":file,
                      "functions":[{"label":name,"calls":count}
                                   for name,count in sorted(values.items())],
                      "total_calls":sum(values.values())}
                     for file,values in sorted(calls.items())]}
    try:
        sys.stderr.write("\n"+MAGIC+json.dumps(output,sort_keys=True,separators=(",",":"))+"\n")
        sys.stderr.flush()
    except Exception:
        pass

if PREFIX:
    atexit.register(_emit)
    sys.setprofile(_profile)
