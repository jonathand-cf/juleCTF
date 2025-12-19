# Luke 13 Nisselandslaget (Bonus)

**Author**: vealending

**Descripotion**:
> Ånei, jeg glemte å trykke lagre på det vakre bildet jeg redigerte 🙁 alt jeg har nå er en memdump og et skjermbilde av at jeg holder på. Mener å huske at jeg gjemte flagget bak skjegget til hver enkelt, men aner ikke hva det var

## Writeup

Goal: recover an unsaved Paint.NET project from a Windows minidump (`rxdlqj/paintdotnet.dmp`) and find the flag that was “hidden behind the beards”.

### 1) Recon (dump + hints from `info_dmp.txt`)

First, i confirmed what the dump actually is:

```sh
file rxdlqj/paintdotnet.dmp
```

This shows it’s a Windows **Mini DuMP crash report, 18 streams**.

Then i used [Minidump Parser](https://marketplace.visualstudio.com/items?itemName=CuiLiAn.minidump-parser) and extracted the dump info into `info_dmp.txt`, i used it as a “map” to confirm the process is Paint.NET and that it loaded relevant modules:

```sh
rg -n "(?i)paintdotnet|PaintDotNet" info_dmp.txt | head
```

`info_dmp.txt` have the module list (PaintDotNet.*.dll), which confirms this is the right process/dump.

You can also find traces of which image file was opened (not required for the flag, but useful for validation):

```sh
strings -a -n 8 rxdlqj/paintdotnet.dmp | rg -i "C:\\\\Users\\\\.*\\.(jpg|png|pdn)" | head
```

### 2) Why this is not “a PNG in the dump”

When i used `binwalk` and extracted the PNG's, i got like over 1000 images.

Because the project wasn’t saved as `.pdn`, the content often lives as **raw pixel buffers in RAM** (typically 4 bytes per pixel, BGRA), not as a finished PNG/JPEG.

The screenshot (`rxdlqj/skjermbilde.png`) shows the canvas size is `4500 x 3001`. That lets us search for memory regions of approximately:

`4500 * 3001 * 4 = 54,018,000` bytes.

### 3) Finding layer buffers in `Memory64List`

MiniDump has a stream called `Memory64List` which contains the raw contents of many memory regions (a range list + a big memory blob).
I parsed the dump header to locate the stream directory and then `Memory64List`, and searched for ranges with size ≈ `54018000`.

The script below prints the stream overview (including `Memory64List`):

```python
import struct
from pathlib import Path
p=Path('rxdlqj/paintdotnet.dmp')
with p.open('rb') as f:
    sig,ver,num_streams,dir_rva,checksum,timestamp,flags=struct.unpack('<IIIIIIQ',f.read(32))
    f.seek(dir_rva)
    dirs=f.read(num_streams*12)
for i in range(num_streams):
    stype,size,rva=struct.unpack_from('<III',dirs,i*12)
    print(f'{i:02d}: type={stype} size={size} rva={rva}')
```

Then `Memory64List` was used to find large buffers. In this dump there were **4** ranges of size `54018048` (48 bytes more than a “perfect” BGRA buffer). These were extracted to `recovered_layers/` and “trimmed” in two ways:

- `trim0`: første `4500*3001*4` bytes
- `trim48`: hopp over 48 bytes header og ta neste `4500*3001*4` bytes

- `trim0`: first `4500*3001*4` bytes
- `trim48`: skip a 48-byte header and take the next `4500*3001*4` bytes

Extraction:

```sh
mkdir -p recovered_layers
```

```python
import struct
from pathlib import Path
p=Path('rxdlqj/paintdotnet.dmp')
w,h=4500,3001
TARGET=w*h*4

with p.open('rb') as f:
    sig,ver,num_streams,dir_rva,checksum,timestamp,flags=struct.unpack('<IIIIIIQ',f.read(32))
    f.seek(dir_rva)
    dirs=f.read(num_streams*12)

mem64_rva=None
for i in range(num_streams):
    stype,size,rva=struct.unpack_from('<III',dirs,i*12)
    if stype==9:
        mem64_rva=rva
        break
assert mem64_rva is not None

with p.open('rb') as f:
    f.seek(mem64_rva)
    n_ranges, base_rva = struct.unpack('<QQ', f.read(16))
    ranges=[struct.unpack('<QQ', f.read(16)) for _ in range(n_ranges)]

offset=base_rva
candidates=[]
for idx,(start,size) in enumerate(ranges):
    if size==TARGET+48:
        candidates.append((idx,start,size,offset))
    offset += size

print('candidates',len(candidates))
with p.open('rb') as f:
    for j,(idx,start,size,off) in enumerate(candidates):
        f.seek(off)
        blob=f.read(size)
        Path(f'recovered_layers/layerbuf_{j}_addr_{start:x}_full.bin').write_bytes(blob)
        Path(f'recovered_layers/layerbuf_{j}_trim0.raw').write_bytes(blob[:TARGET])
        Path(f'recovered_layers/layerbuf_{j}_trim48.raw').write_bytes(blob[48:48+TARGET])
```

`(AI alert, needed different and whole memory range as stored in the dump)`

### 4) Converting raw BGRA to PNG (viewing layers)

Once the raw data is extracted, ImageMagick can read it as “raw BGRA”:

```sh
magick -size 4500x3001 -depth 8 bgra:recovered_layers/layerbuf_0_trim48.raw recovered_layers/layer0_trim48.png
magick -size 4500x3001 -depth 8 bgra:recovered_layers/layerbuf_1_trim48.raw recovered_layers/layer1_trim48.png
magick -size 4500x3001 -depth 8 bgra:recovered_layers/layerbuf_2_trim48.raw recovered_layers/layer2_trim48.png
magick -size 4500x3001 -depth 8 bgra:recovered_layers/layerbuf_3_trim48.raw recovered_layers/layer3_trim48.png
```

In this challenge, the different buffers corresponded to:

- `recovered_layers/layer0_trim48.png`: background image (the photo)
- `recovered_layers/layer1_trim48.png`: the flag
- `recovered_layers/layer2_trim48.png`: beards/hats (overlay layer)
- `recovered_layers/layer3_trim48.png`: logo layer

### 5) Flag

The text is found in `layer1_trim48.png` and is split across fragments (`JUL{`,`fo`, `to`, `ge`, `ni`, `sk`, `e_`, `al`, `ve`, `r}`), which combine into the flag:

`JUL{fotogeniske_alver}`
