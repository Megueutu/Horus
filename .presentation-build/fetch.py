import json, urllib.request, urllib.parse, concurrent.futures
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).parent
pages=json.loads((root/'pages.json').read_text())
assets=json.loads((root/'assets.json').read_text())
(root/'slides').mkdir(exist_ok=True)
(root/'media').mkdir(exist_ok=True)
jobs=[(p['thumbnail']['url'],root/'slides'/f"{p['index']:02d}.png") for p in pages]
jobs += [(a['result']['asset']['thumbnail']['url'],root/'media'/f"{a['assetId']}.png") for a in assets if a.get('result')]
def fetch(job):
    url,path=job
    if path.exists(): return
    try:
        try:
            response=urllib.request.urlopen(url,timeout=45)
        except Exception:
            fallback=urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('fallback')
            if not fallback: raise
            response=urllib.request.urlopen(fallback[0],timeout=45)
        with response: path.write_bytes(response.read())
    except Exception as e: print(path.name,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(fetch,jobs))
for kind,files,cols,w,h in [('slides',sorted((root/'slides').glob('*.png')),4,596,365),('media',sorted((root/'media').glob('*.png')),6,210,240)]:
    sheet=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),'#d9dddf')
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGBA'); im.thumbnail((w-12,h-30))
        x,y=(i%cols)*w,(i//cols)*h
        sheet.paste(im,(x+6,y+24),im)
        draw.text((x+8,y+6),p.stem,fill='black')
    sheet.save(root/f'{kind}-contact.png')
print('Downloaded',len(jobs),'source previews')
