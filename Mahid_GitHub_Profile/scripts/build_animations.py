"""Generate script-free animated SVG artwork for a GitHub README."""
from pathlib import Path
from html import escape
A=Path(__file__).resolve().parents[1]/'assets'
A.mkdir(exist_ok=True)

def svg(name,w,h,body,css=''):
    (A/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><style>{css}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.role{{opacity:0}}.first{{opacity:1}}}}</style>{body}</svg>')

def text(x,y,value,size=16,color='#c4b5fd',extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" {extra}>{escape(value)}</text>'

body='''<title>Yeamin Rahman Mahid — Machine Learning, Computer Vision and Data Science</title><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0c1020"/><stop offset="1" stop-color="#26174c"/></linearGradient><linearGradient id="line"><stop stop-color="#6366f1"/><stop offset=".5" stop-color="#c084fc"/><stop offset="1" stop-color="#22d3ee"/></linearGradient><clipPath id="round"><rect width="1000" height="290" rx="18"/></clipPath></defs><g clip-path="url(#round)"><rect width="1000" height="290" fill="url(#bg)"/><circle class="halo" cx="860" cy="130" r="105" fill="#8b5cf6" opacity=".08"/>'''
nodes=[(735,65),(800,42),(870,70),(935,48),(766,125),(845,135),(924,121),(724,203),(815,220),(903,213)]
edges=[(0,1),(0,4),(1,2),(1,4),(2,3),(2,5),(3,6),(4,5),(4,7),(5,6),(5,8),(6,9),(7,8),(8,9),(2,6)]
for a,b in edges:
    x,y=nodes[a];u,v=nodes[b]
    body+=f'<path d="M{x} {y}L{u} {v}" stroke="#7c63ca" stroke-width="1" opacity=".3"/>'
for i,(x,y) in enumerate(nodes):
    body+=f'<circle class="node" cx="{x}" cy="{y}" r="4" fill="#c4b5fd" style="animation-delay:-{i*.37}s"/>'
body+='<rect x="40" y="41" width="32" height="3" rx="1.5" fill="#a78bfa"/>'
body+=text(84,47,'LEARNING IN PUBLIC',12,extra='font-weight="700" letter-spacing="2"')
body+=text(40,117,'Yeamin Rahman Mahid',46,'#fafaff','font-weight="700"')
body+=text(42,149,'CSE UNDERGRADUATE · EAST WEST UNIVERSITY',13,'#aab2cc','letter-spacing="1"')
roles=['Exploring Machine Learning & AI','Building with Computer Vision','Turning Data into Understanding']
for i,role in enumerate(roles):
    body+=f'<g class="role {"first" if i==0 else ""}" style="animation-delay:{i*4}s">'+text(42,207,role,25,'#e6ddff','font-weight="600"')+'</g>'
body+='<rect class="cursor" x="535" y="185" width="3" height="25" fill="#a78bfa"/>'
body+=text(42,252,'DHAKA, BANGLADESH   /   LEARN · BUILD · EXPERIMENT',11,'#939db8','letter-spacing="1.4"')
body+='<rect class="scan" x="-260" y="287" width="260" height="3" fill="url(#line)"/></g>'
css='''.node{animation:pulse 3.8s ease-in-out infinite}.halo{animation:breathe 7s ease-in-out infinite}.role{opacity:0;animation:roles 12s linear infinite}.cursor{animation:blink 1s step-end infinite}.scan{animation:scan 6s linear infinite}@keyframes pulse{0%,100%{opacity:.3}50%{opacity:1}}@keyframes breathe{50%{opacity:.17}}@keyframes roles{0%,2%{opacity:0}5%,28%{opacity:1}32%,100%{opacity:0}}@keyframes blink{50%{opacity:0}}@keyframes scan{to{transform:translateX(1260px)}}'''
svg('header.svg',1000,290,body,css)

body='<title>Animated violet section divider</title><defs><linearGradient id="s"><stop stop-color="#6366f1" stop-opacity="0"/><stop offset=".5" stop-color="#c084fc"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient></defs><path d="M0 12H1000" stroke="#8b5cf6" stroke-opacity=".18"/><rect class="s" x="-220" y="11" width="220" height="2" fill="url(#s)"/>'
svg('divider.svg',1000,24,body,'.s{animation:slide 7s linear infinite}@keyframes slide{to{transform:translateX(1220px)}}')

body='<title>Learn, build, experiment, improve</title><rect width="1000" height="120" rx="14" fill="#131629"/>'
for i,(x,word) in enumerate([(68,'LEARN'),(302,'BUILD'),(529,'EXPERIMENT'),(813,'IMPROVE')]):
    body+=f'<g class="step" style="animation-delay:-{(3-i)*2}s">'+text(x,65,word,19,'#d9ccff','font-weight="700" letter-spacing="2"')+f'<circle cx="{x+30}" cy="86" r="3" fill="#a78bfa"/></g>'
for x in (238,465,747):body+=text(x,64,'→',20,'#71618f')
svg('footer.svg',1000,120,body,'.step{animation:glow 8s ease-in-out infinite}@keyframes glow{0%,25%,100%{opacity:.45}12%{opacity:1}}')

# Retain the generated toolkit content and add a subtle moving accent.
for name in ['languages.svg','ml.svg','tools.svg']:
    p=A/name
    if p.exists():
        import re
        s=p.read_text()
        s=re.sub(r'<g id="animated-accent">.*?</g>','',s,flags=re.S)
        accent='<g id="animated-accent"><style>.accent{animation:accent 8s linear infinite}@keyframes accent{from{transform:translateX(-180px)}to{transform:translateX(1000px)}}@media(prefers-reduced-motion:reduce){.accent{animation:none}}</style><rect class="accent" x="0" y="94" width="180" height="2" fill="#8b5cf6" opacity=".7"/></g>'
        p.write_text(s.replace('</svg>',accent+'</svg>'))
print('Generated animated header, dividers, toolkit accents and footer.')
