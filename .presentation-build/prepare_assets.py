import json,shutil,math
from pathlib import Path
from PIL import Image
root=Path(__file__).parent
out=root.parent/'presentation'/'assets'
out.mkdir(parents=True,exist_ok=True)
temp=Path('C:/Users/EDUARD~1/AppData/Local/Temp')
for source,name in [('codex-clipboard-9ee0d4d2-94ab-4c0a-b975-fdd5048477e8.png','powerpoint.png'),('codex-clipboard-ff700542-318d-4caa-99cf-0b09c3d1e41a.png','canva.png')]:
    shutil.copyfile(temp/source,out/name)
def crop(page,box,name):
    im=Image.open(root/'slides'/f'{page:02d}.png')
    x,y,w,h=box
    s=im.width/1920;sy=im.height/1080
    im.crop((round(x*s),round(y*sy),round((x+w)*s),round((y+h)*sy))).save(out/name)
crop(1,(363,354,1194,372),'dite-logo.png')
crop(2,(983,380,689,516),'windows-desktop.png')
crop(5,(835,540,775,460),'task-manager.png')
crop(6,(1070,364,780,393),'internet-search.png')
crop(10,(116,91,1688,898),'powerpoint-example.png')
crop(11,(1249,349,410,318),'presentation-format.png')
crop(21,(83,141,1754,798),'canva-example.png')
crop(24,(1049,501,763,471),'abnt.png')
crop(28,(1157,367,643,599),'outlook.png')
crop(31,(100,87,902,478),'closed.jpg')
shutil.copyfile(root/'slides'/'32.png',out/'welcome-collage.png')
for page,box,name in [(33,(108,320,210,315),'dorf-wave.png'),(33,(668,320,510,287),'dorf-spheres.png'),(33,(1228,320,510,290),'dorf-techwear.png'),(33,(108,665,510,254),'dorf-office.png'),(33,(668,665,250,315),'dorf-eshop.png')]: crop(page,box,name)
for source,name in [('MAF9graRFek','xls-outline.png'),('MAGEIn0PdAM','xls.png'),('MAHNTYwkxBk','phishing.png')]: shutil.copyfile(root/'media'/f'{source}.png',out/name)
print('Prepared',len(list(out.iterdir())),'local assets')
