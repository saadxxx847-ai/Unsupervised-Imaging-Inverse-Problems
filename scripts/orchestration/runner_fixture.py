"""Controlled native child. Never imports project training or restoration code."""
import json
import os
from pathlib import Path
import sys
import time
import traceback

root=Path(sys.argv[1])
case=sys.argv[2]
delay=int(sys.argv[3])
print('fixture child started pid='+str(os.getpid()),flush=True)
print('ordinary warning on stderr; not a failure',file=sys.stderr,flush=True)
for elapsed in range(delay):
    if elapsed % 5 == 0:
        print('fixture heartbeat elapsed_seconds='+str(elapsed),flush=True)
    time.sleep(1)
if case=='native-failure':
    try:
        raise RuntimeError('deliberate fixture failure')
    except RuntimeError:
        traceback.print_exc()
    sys.exit(7)
if case=='success':
    with (root/'output'/'fixture.ok').open('x',encoding='utf-8') as fh:
        json.dump({'kind':'validation fixture','pid':os.getpid(),'trained':False},fh)
    print('fixture success',flush=True)
else:
    print('fixture exits zero without required artifact',flush=True)
