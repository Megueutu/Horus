import json,urllib.request
from pathlib import Path
from PIL import Image
root=Path(__file__).parent
for p in json.loads((root/'highres.json').read_text()):
    path=root/'slides'/f"{p['page']:02d}-large.png"
    request=urllib.request.Request(p['url'],headers={'x-amz-expected-bucket-owner':'078831785109'})
    try:
        with urllib.request.urlopen(p['url'],timeout=40) as r: path.write_bytes(r.read())
        print(path.name,Image.open(path).size)
    except Exception as e: print(path.name,str(e))
