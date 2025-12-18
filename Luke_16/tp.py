#!/usr/bin/env python3
import re
from pathlib import Path

data=Path('intresting').read_text(errors='ignore')
pts=[tuple(map(int,t)) for t in re.findall(r"\btp\s+(\d+)\s+(\d+)\s+(\d+)\b",data)]
pts=list(dict.fromkeys(pts))
pts.sort(key=lambda p:p[2])
print(''.join(chr(p[0]) for p in pts),end='')