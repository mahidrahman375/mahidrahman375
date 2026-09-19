"""Build the profile's SVG artwork with Python 3. No packages required."""
from pathlib import Path
from html import escape
import json
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

def svg(name, width, height, content):
    (ASSETS / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{content}</svg>', encoding='utf-8')

def label(x, y, value, size=16, color='#c4c7d9', weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(str(value))}</text>'

hero = '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101321"/><stop offset="1" stop-color="#211744"/></linearGradient></defs><rect width="1000" height="240" rx="16" fill="url(#bg)"/>'
for x in range(720, 981, 26):
    for y in range(32, 219, 26):
        hero += f'<circle cx="{x}" cy="{y}" r="1.5" fill="#a78bfa" opacity="0.25"/>'
hero += '<rect x="40" y="39" width="36" height="3" rx="1.5" fill="#a78bfa"/>'
hero += label(88,46,'LEARNING IN PUBLIC',12,'#b9a4f6',700)
hero += label(40,111,'Yeamin Rahman Mahid',46,'#fafaff',700)
hero += label(42,151,'MACHINE LEARNING  /  COMPUTER VISION  /  DATA SCIENCE',15,'#c4b5fd',700)
hero += label(42,204,'East West University',15) + label(248,204,'•',15,'#8b5cf6') + label(270,204,'Dhaka, Bangladesh',15)
svg('header.svg',1000,240,hero)

for name,title,w,color in [('linkedin','LINKEDIN',116,'#7053cf'),('github','GITHUB',108,'#23283a'),('codeforces','CODEFORCES',142,'#23283a'),('leetcode','LEETCODE',124,'#23283a')]:
    svg(name+'.svg',w,34,f'<rect width="{w}" height="34" rx="7" fill="{color}"/>'+f'<text x="{w/2}" y="22" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="11" font-weight="700" letter-spacing="1" fill="#ffffff">{title}</text>')

categories = [('languages','LANGUAGES',['Python','C','C++','Java','JavaScript']),('ml','ML & DATA',['PyTorch','TensorFlow','scikit-learn','OpenCV','pandas','NumPy']),('tools','TOOLS & WORKSPACE',['Git','GitHub','Jupyter','Colab','Kaggle','Streamlit','VS Code','IntelliJ IDEA'])]
for filename,title,items in categories:
    content = '<rect width="1000" height="96" rx="10" fill="#151827"/>'+label(22,28,title,12,'#b7a0f4',700)
    x=22
    for item in items:
        w=len(item)*8+26
        content += f'<rect x="{x}" y="44" width="{w}" height="30" rx="6" fill="#24283b"/>'+label(x+13,64,item,14,'#ecebff')
        x += w+10
    svg(filename+'.svg',1000,96,content)

def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'mahid-profile-assets','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

# Statistics are a dated public snapshot, never invented or labelled live.
# All responses must succeed before the existing statistics asset is replaced.
user=get_json('https://api.github.com/users/mahidrahman375')
repos=[]
page=1
while True:
    batch=get_json(f'https://api.github.com/users/mahidrahman375/repos?per_page=100&page={page}')
    repos.extend(batch)
    if len(batch)<100:
        break
    page+=1
owned=[r for r in repos if not r['fork']]
values=[('PUBLIC REPOSITORIES',user['public_repos']),('FOLLOWERS',user['followers']),('STARS · NON-FORK REPOS',sum(r['stargazers_count'] for r in owned))]
content='<rect width="1000" height="148" rx="12" fill="#151827"/>'
for i,(title,value) in enumerate(values):
    x=28+i*330
    content+=label(x,38,title,11,'#b7a0f4',700)+label(x,92,value,40,'#fafaff',700)
    if i<2: content+=f'<path d="M {x+300} 24 v 78" stroke="#333149"/>'
content+=label(28,128,'Public GitHub snapshot · '+datetime.now(timezone.utc).strftime('%Y-%m-%d UTC')+' · Refresh: python3 scripts/build_assets.py',11,'#9ba2b8')
svg('github-stats.svg',1000,148,content)
print('Built all SVG assets; fetched real public GitHub statistics.')
