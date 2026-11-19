"""Public same-byte symlink interleaving, separate from the reserved corpus."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
from read import blob, safe_read

with TemporaryDirectory() as directory:
    source=Path(directory)/"source.md"
    target=Path(directory)/"target.md"
    raw=b"Public source for the opening control.\n"
    source.write_bytes(raw)
    target.write_bytes(raw)
    path_open=Path.open
    descriptor_open=os.open
    mutated=False
    def replace():
        global mutated
        if not mutated:
            mutated=True
            source.unlink()
            source.symlink_to(target)
    def through_path(path,*args,**kwargs):
        if path==source:
            replace()
        return path_open(path,*args,**kwargs)
    def through_descriptor(path,*args,**kwargs):
        if Path(path)==source:
            replace()
        return descriptor_open(path,*args,**kwargs)
    with patch.object(Path,"open",through_path),patch.object(os,"open",through_descriptor):
        try:
            safe_read(source,blob(raw))
        except ValueError:
            print("SYMLINK_REJECTED")
        else:
            print("SYMLINK_ACCEPTED")
    assert mutated
