import json,html
from pathlib import Path
root=Path(__file__).parent
source=json.loads((root/'source.json').read_text(encoding='utf-8'))
esc=html.escape
def box(x,y,w,h=None):
    return f'left:{x:g}px;top:{y:g}px;width:{w:g}px;'+(f'height:{h:g}px;' if h else '')
def at(text,x,y,w,cls='body',tag='div',h=None):
    return f'<{tag} class="positioned {cls}" style="{box(x,y,w,h)}">{text}</{tag}>'
def ul(items): return '<ul>'+''.join('<li>'+esc(i.lstrip('• ').strip())+'</li>' for i in items if i.strip())+'</ul>'
def groups(text):
    parts=text.strip().split('\n\n')
    result=f'<p class="intro">{esc(parts[0])}</p>'
    for part in parts[1:]:
        lines=part.splitlines()
        result+=f'<div class="group"><h2>{esc(lines[0])}</h2>{ul(lines[1:])}</div>'
    return result
titles={1:'DITE — Fundamentos digitais',10:'PowerPoint — exemplo',21:'Canva — exemplo',31:'Encerramento',32:'Bem-vindos!',33:'Referências DORFic',34:'Paleta de cores'}
for p in range(1,36):
    texts=[t for t in source['richtexts'] if t['page_index']==p and t['containerElement']['type']=='TEXT']
    if p not in titles and texts:
        titles[p]=''.join(min(texts,key=lambda x:x['containerElement']['position']['top'])['regions'][i]['text'] for i in range(len(min(texts,key=lambda x:x['containerElement']['position']['top'])['regions'])))
symbols='''<svg class="symbols" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#eff2f3"/><stop offset=".18" stop-color="#8a949c"/><stop offset=".43" stop-color="#d3d9dd"/><stop offset=".58" stop-color="#979fa5"/><stop offset=".8" stop-color="#f7f9fa"/><stop offset="1" stop-color="#bcc4c9"/></linearGradient>
<linearGradient id="bevel" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#6a737a"/><stop offset=".27" stop-color="#c1c8ce"/><stop offset=".48" stop-color="#fff"/><stop offset=".55" stop-color="#d2d7db"/><stop offset=".8" stop-color="#626d76"/><stop offset="1" stop-color="#eef0f1"/></linearGradient>
<linearGradient id="orange" x1="0" y1="1" x2=".8" y2="0"><stop stop-color="#ffd236"/><stop offset=".33" stop-color="#ff980c"/><stop offset=".7" stop-color="#ff6607"/><stop offset="1" stop-color="#ed3e08"/></linearGradient>
<linearGradient id="hexbevel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff8d9"/><stop offset=".35" stop-color="#ffbe68"/><stop offset=".6" stop-color="#ff5708"/><stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#fb7a23"/></linearGradient>
<symbol id="metal-corner" viewBox="0 0 470 470"><path d="M0 0 155 139 133 218 470 470H0Z" fill="url(#steel)"/><path d="M0 3 154 140 132 220 470 470 440 470 104 228 126 148 0 36Z" fill="url(#bevel)"/><path d="M0 11 146 143 124 222 464 470" fill="none" stroke="#fff" stroke-width="5"/><path d="M0 33 128 150 106 230 438 470" fill="none" stroke="#727d85" stroke-width="4"/><path d="M0 45 116 154 94 233 420 470" fill="none" stroke="#e8edf0" stroke-width="2"/><path d="M0 62 96 159 73 237 391 470" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="2"/></symbol>
<symbol id="hex-filled" viewBox="0 0 200 174"><path d="M50 3H150L197 87 150 171H50L3 87Z" fill="url(#hexbevel)" stroke="#f65707" stroke-width="3"/><path d="M53 12H147L188 87 147 162H53L12 87Z" fill="url(#orange)" stroke="#fff7d2" stroke-opacity=".65" stroke-width="3"/><path d="M53 13H147L185 82" fill="none" stroke="#fff" stroke-width="3" stroke-opacity=".65"/></symbol>
<symbol id="hex-outline" viewBox="0 0 200 174"><path d="M50 3H150L197 87 150 171H50L3 87Z" fill="none" stroke="#f86612" stroke-width="4"/></symbol></defs></svg>'''
media={'MAHV7rtp13c':('dite-logo.png','DITE — Fundamentos digitais','logo'), 'MAHazLOZU6c':('windows-desktop.png','Exemplo de área de trabalho do Windows','screen'), 'MAHazLh7J2Q':('task-manager.png','Exemplo do Gerenciador de Tarefas','screen'), 'MAHX0ukf9u8':('powerpoint-example.png','Exemplo de uma apresentação aberta no PowerPoint','screen'), 'MAHa0CoDg3A':('presentation-format.png','Formato de apresentação no Canva',''), 'MAHX0jTrL40':('canva-example.png','Exemplo de uma apresentação aberta no editor do Canva','screen'), 'MAHah7nBuUU':('abnt.png','Associação Brasileira de Normas Técnicas',''), 'MAF9graRFek':('xls-outline.png','Arquivo de planilha XLS',''), 'MAGEIn0PdAM':('xls.svg','Ícone de arquivo de planilha XLS',''), 'MAHahq_nAUY':('outlook.png','Microsoft Outlook',''), 'MAHNTYwkxBk':('phishing.png','Gancho e cadeado representando phishing',''), 'MAEEZN6Etvs':('closed.jpg','Placa: Sorry, we’re closed',''), 'MAHX0RI6na0':('powerpoint.png','PowerPoint','app-icon'), 'MAHX0r4kGDU':('canva.png','Canva','app-icon'), 'MAHV7tKSMrs':('dorf-wave.png','Referência de ondas e formas industriais laranjas',''), 'MAHV7rR77Zk':('dorf-spheres.png','Referência de esferas e superfícies laranjas',''), 'MAHV7ms4Vxk':('dorf-techwear.png','Referência de tecnologia e vestuário industrial',''), 'MAHV7mN-dOw':('dorf-office.png','Referência visual do Microsoft Office',''), 'MAHV7sxN0Yg':('dorf-eshop.png','Referência visual de interface Nintendo eShop','')}
def decorations(p):
    result=''
    seen=set()
    for f in source['fills']:
        if f['page_index']!=p: continue
        b=f['containerElement']; x=b['position']['left'];y=b['position']['top'];w=b['dimension']['width'];h=b['dimension']['height'];a=f['asset_id']
        if a=='MAG4TyUFZi4':
            if any(abs(x-sx)<5 and abs(y-sy)<5 for sx,sy in seen): continue
            seen.add((x,y))
            rotation='transform:rotate(180deg);' if x>960 else ''
            result+=f'<svg class="deco metal" aria-hidden="true" style="{box(x,y,w,h)}{rotation}"><use href="#metal-corner"/></svg>'
        elif a=='MAHWlzrgYo4':
            # Padrão vetorial com o mesmo ponto de ancoragem do asset original.
            corner_only=(x>960 and y<0) or (x<0 and y>0)
            result+=f'<svg class="deco hexfield" viewBox="0 0 996 567" aria-hidden="true" style="{box(x,y,w,h)}'+('transform:rotate(180deg);' if x>960 else '')+'">'
            for row in range(3):
                if corner_only and row==0: continue
                for col in range(min(3,5-row) if corner_only else 5-row):
                    sx=col*205+(102 if row%2 else 0);sy=row*177
                    typ='hex-outline' if (row+col)%3==1 else 'hex-filled'
                    result+=f'<use href="#{typ}" x="{sx}" y="{sy}" width="200" height="174"/>'
            result+='</svg>'
        elif a in media:
            name,alt,cls=media[a]
            result+=f'<img class="visual {cls}" src="assets/{name}" alt="{esc(alt)}" draggable="false" style="{box(x,y,w,h)}">'
    if p==6:
        result+=f'<img class="visual" src="assets/internet-search.png" alt="Exemplos de navegação e pesquisa na internet" draggable="false" style="{box(1070,364,780,393)}">'
    return result
def text(p):
    entries=[t for t in source['richtexts'] if t['page_index']==p and t['containerElement']['type']=='TEXT']
    entries.sort(key=lambda x:(x['containerElement']['position']['top'],x['containerElement']['position']['left']))
    result=''
    for t in entries:
        b=t['containerElement'];x=b['position']['left'];y=b['position']['top'];w=b['dimension']['width'];h=b['dimension']['height']
        plain=''.join(r['text'] for r in t['regions']).strip()
        if not plain: continue
        if p==33:
            result+=at(esc(plain),x,y,w,'heading reference-title','h1');continue
        if p in [8,9,*range(11,21),35] and y==235:
            result+=at(groups(plain),x,y,w,'body compact' if p in [19,35] else 'body');continue
        if p==2 and y>210:
            parts=plain.split('\n\n')
            markup=ul(parts[0].splitlines())
            for part in parts[1:]:
                lines=part.splitlines();markup+=f'<h2>{esc(lines[0])}</h2>'+ul(lines[1:])
            result+=at(markup,x,y,w,'body compact');continue
        is_title=(y<210 and h>70 and '\n' not in plain)
        if p==6 and y<200: is_title=True
        if is_title:
            result+=at(esc(plain),x,y,w,'heading','h1' if not result else 'h2');continue
        if 150<y<330 and h<75 and '\n' not in plain:
            result+=at(esc(plain),x,y,w,'subheading','h2');continue
        lines=plain.splitlines()
        if p==30:
            markup='<p><a href="https://megueutu.github.io/Horus/" target="_blank" rel="noopener noreferrer">https://megueutu.github.io/Horus/</a></p>'
        elif p==27:
            markup='<ol>'+''.join(f'<li>{esc(line.strip())}</li>' for line in lines)+'</ol>'
        elif p==26:
            markup=''.join('<p>'+esc(part).replace('\n','<br>')+'</p>' for part in plain.split('\n\n'))
        elif p==24:
            markup='<p>Título do trabalho</p><p>1. Introdução • 2. Desenvolvimento<br>2.1 Aplicações • 3. Conclusão</p><p>Use estilos para padronizar e gerar sumário.</p>'
        else:
            markup=ul(lines)
        cls='body compact' if p in [3,4,5,26,27] else 'body'
        if p==7: cls='body wide'
        if p==28: markup=markup.replace('Span,','Spam,')
        result+=at(markup,x,y,w,cls)
    if p in [3,4,5]: result+='<div class="divider" aria-hidden="true"></div>' if p!=5 else ''
    return result
slides=[]
for p in range(1,36):
    cls='cover' if p==1 else 'closing' if p==31 else 'collage' if p==32 else 'palette' if p==34 else 'example-slide' if p in [10,21] else ''
    inside=decorations(p)+text(p)
    if p==32:
        inside='<img class="visual full-image" src="assets/welcome-collage.png" alt="Bem-vindos! Colagem original com personagens e imagens de referência do curso." draggable="false">'
    if p==34:
        inside='<div class="orange-tile" aria-label="Amostra de superfície laranja"></div><svg class="hex-sample" aria-label="Amostra de hexágono laranja"><use href="#hex-filled"/></svg>'
        for x,c in [(771.915,'#ff990d'),(1165.915,'#e88300'),(1560.078,'#ff7800')]: inside+=f'<div class="palette-chip" style="left:{x}px;top:721.964px;background:{c}" aria-label="Cor {c}"></div>'
    slides.append(f'<!-- SLIDE {p:02d}: {esc(titles[p])}. Mova esta section inteira para reorganizar. -->\n<section class="slide {cls}'+(' is-active' if p==1 else '')+f'" id="slide-{p:02d}" data-source-page="{p}" data-title="{esc(titles[p],quote=True)}" role="group" aria-roledescription="slide" aria-label="{p} de 35 — {esc(titles[p],quote=True)}" aria-hidden="'+('false' if p==1 else 'true')+'">\n'+inside+'\n</section>')
css=(root/'style.css').read_text(encoding='utf-8')
js=(root/'navigation.js').read_text(encoding='utf-8')
result='''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="DITE — Fundamentos digitais. Apresentação do curso com navegação pelo teclado.">
<meta name="theme-color" content="#f5690b">
<title>DITE — Fundamentos digitais</title>
<style>'''+css+'''</style>
</head>
<body>
<!--
  APRESENTAÇÃO LOCAL | Fonte: Canva DAHV7g9oaXw | 35 páginas, 1920 × 1080 (16:9).
  Abra index.html diretamente no navegador, mantendo a pasta assets ao lado.
  Setas esquerda/direita: trocar página. F: tela cheia. Esc: sair da tela cheia.
  Conteúdo, CSS e navegação ficam neste arquivo. Não há dependências externas.
  Cada section é um slide editável. Reordene as sections para mudar a sequência.
  data-source-page registra a página de origem; o contador segue a ordem no HTML.
  Os IDs slide-XX preservam links existentes; a navegação os usa pela ordem atual.
  Cantos metálicos e hexágonos são vetores. As imagens ficam em assets/.
  Algumas capturas foram extraídas das prévias de 596 px disponibilizadas pelo Canva.
  A colagem da página 32 foi preservada como uma imagem, inclusive seus textos.
  Correção de digitação na página 28: "Span" para "Spam".
-->
'''+symbols+'''
<main id="stage" aria-label="Apresentação DITE">
<div id="frame" role="region" aria-label="Slides do curso">
'''+ '\n\n'.join(slides)+'''
</div>
</main>
<footer class="chrome" aria-label="Controles da apresentação">
<span class="chrome-label">DITE <span style="color:#86949e;font-weight:400">/ Fundamentos digitais</span></span>
<span class="chrome-hint">Use as setas esquerda e direita do teclado <span aria-hidden="true">·</span> <kbd>F</kbd> tela cheia</span>
<div class="chrome-actions"><span id="counter" aria-hidden="true">01 / 35</span>
<button id="fullscreen" type="button" title="Tela cheia (F)" aria-pressed="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M8 3H3v5M16 3h5v5M21 16v5h-5M8 21H3v-5"/></svg><span id="fullscreen-label">Tela cheia</span></button></div>
</footer>
<div id="progress" aria-hidden="true"><div id="progress-fill"></div></div>
<div id="live" class="sr-only" aria-live="polite" aria-atomic="true"></div>
<div id="status" role="status"></div>
<noscript><div style="position:fixed;inset:0 auto auto 0;background:#fff4e9;padding:16px;z-index:30">Ative o JavaScript para navegar pelos slides com as setas do teclado.</div></noscript>
<script>'''+js+'''</script>
</body>
</html>
'''
(root.parent/'presentation'/'index.html').write_text(result,encoding='utf-8')
print('Created 35 editable slide sections:',len(result),'characters')
