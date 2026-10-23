#!/usr/bin/env python3
"""Public-only GitHub profile. Standard library; no persistent credentials."""
import xml.etree.ElementTree as ET
import argparse, hashlib, collections, datetime as dt, html, json, os, re, sys, tempfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'jichuo1'
FEATURED = {
 'Bilibili_Innocent_Lab': 'Modular Android runtime exploration.',
 'LumenCoacervationEngine': 'Materials and motion for Android View.',
 'SplashScreenAdvanced': 'A considered start to every app.',
 'GlobalTokenTracker': 'Native visibility into AI coding usage.',
}

def get(url, token=None):
    headers = {'User-Agent': 'personal-profile-statistics', 'Accept': 'application/vnd.github+json'}
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request(url, headers=headers), timeout=30) as r:
        return r.read().decode('utf-8')

def pages(path, token=None, fetch=get):
    result=[]
    for page in range(1, 101):
        rows=json.loads(fetch(f'https://api.github.com{path}{"&" if "?" in path else "?"}per_page=100&page={page}', token))
        if not isinstance(rows,list): raise ValueError('Unexpected collection response')
        result.extend(rows)
        if len(rows)<100: return result
    raise ValueError('Pagination limit reached; refusing partial data')

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days={}
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'data-date' not in a or 'data-level' not in a: return
        date=dt.date.fromisoformat(a['data-date']); level=int(a['data-level'])
        if level not in range(5): raise ValueError('Invalid contribution level')
        key=date.isoformat()
        if key in self.days: raise ValueError('Duplicate contribution date')
        self.days[key]=level

def calendar(text):
    p=Calendar(); p.feed(text)
    days=sorted(p.days.items())
    if not 350<=len(days)<=380: raise ValueError('Incomplete contribution calendar')
    dates=[dt.date.fromisoformat(d) for d,_ in days]
    if any(b-a!=dt.timedelta(days=1) for a,b in zip(dates,dates[1:])):
        raise ValueError('Noncontiguous calendar')
    if dates[-1] > dt.datetime.now(dt.timezone.utc).date()+dt.timedelta(days=1):
        raise ValueError('Future calendar')
    return days

def number(v):
    if type(v) is not int or v<0: raise ValueError('Invalid count')
    return v

def summarize(source, days):
    repos=source['repos']
    if not repos: raise ValueError('No repositories')
    public=[]
    for r in repos:
        if r.get('private') is not False: continue
        if r['full_name']!=OWNER+'/'+r['name']: raise ValueError('Unexpected repository owner')
        number(r['stargazers_count']);number(r['forks_count'])
        public.append(r)
    if len({r['name'] for r in public})!=len(public): raise ValueError('Duplicate repository')
    byname={r['name']:r for r in public}
    projects=[]
    for name,description in FEATURED.items():
        r=byname[name]; releases=source['releases'][name]
        if len({x['id'] for x in releases})!=len(releases): raise ValueError('Duplicate release')
        releases=[x for x in releases if not x['draft']]
        stable=[x for x in releases if not x['prerelease']]
        stable.sort(key=lambda x:x['published_at'] or '',reverse=True)
        projects.append({'name':name,'description':description,'stars':r['stargazers_count'],
            'version':stable[0]['tag_name'] if stable else 'No stable release',
            'downloads':sum(number(a['download_count']) for x in releases for a in x['assets'])})
    return {'checked_at':source['checked_at'],'stars':sum(r['stargazers_count'] for r in public),
        'repos':len(public),'forks':sum(r['forks_count'] for r in public),
        'downloads':sum(p['downloads'] for p in projects),'projects':projects,
        'languages':dict(collections.Counter(r.get('language') or 'Other' for r in public)),
        'calendar':days,'calendar_source':f'https://github.com/users/{OWNER}/contributions'}

def esc(x): return html.escape(str(x), quote=True)

def paper_layer(height,dark,title):
    paper='#191c24' if dark else '#fbf6e9';edge='#090c12' if dark else '#c4ad83';fold='#343641' if dark else '#e7d7b5'
    grain=''.join(f'<circle cx="{(i*137+31)%900}" cy="{(i*43+7)%height}" r=".55" fill="{edge}" opacity=".16"/>' for i in range(max(12,height//3)))
    base=f'<rect width="900" height="{height}" fill="{paper}"/>{grain}<path d="M1 0V{height}M899 0V{height}" stroke="{edge}" opacity=".24"/>'
    return base

def svg(height, body, dark=False, title='Profile statistics'):
    bg,ink,muted,line=('#191c24','#f0eee8','#a8b4c4','#383945') if dark else ('#fbf6e9','#293040','#686d78','#e4daca')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title><style>text{{fill:{ink};font-family:Georgia,'Times New Roman',serif}}.pixel-type{{fill:{ink}}}.muted{{fill:{muted};font-family:monospace}}.label{{font:12px monospace;letter-spacing:1.2px;fill:{muted}}}.rule{{stroke:{line}}}</style>{paper_layer(height,dark,title)}{body}</svg>'''


PIXEL_GLYPHS = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._/', [
'01110/10001/10001/11111/10001/10001/10001','11110/10001/10001/11110/10001/10001/11110','01111/10000/10000/10000/10000/10000/01111','11110/10001/10001/10001/10001/10001/11110','11111/10000/10000/11110/10000/10000/11111','11111/10000/10000/11110/10000/10000/10000','01111/10000/10000/10111/10001/10001/01111','10001/10001/10001/11111/10001/10001/10001','11111/00100/00100/00100/00100/00100/11111','00111/00010/00010/00010/10010/10010/01100','10001/10010/10100/11000/10100/10010/10001','10000/10000/10000/10000/10000/10000/11111','10001/11011/10101/10101/10001/10001/10001','10001/11001/10101/10011/10001/10001/10001','01110/10001/10001/10001/10001/10001/01110','11110/10001/10001/11110/10000/10000/10000','01110/10001/10001/10001/10101/10010/01101','11110/10001/10001/11110/10100/10010/10001','01111/10000/10000/01110/00001/00001/11110','11111/00100/00100/00100/00100/00100/00100','10001/10001/10001/10001/10001/10001/01110','10001/10001/10001/10001/10001/01010/00100','10001/10001/10001/10101/10101/10101/01010','10001/10001/01010/00100/01010/10001/10001','10001/10001/01010/00100/00100/00100/00100','11111/00001/00010/00100/01000/10000/11111',
'01110/10001/10011/10101/11001/10001/01110','00100/01100/00100/00100/00100/00100/01110','01110/10001/00001/00010/00100/01000/11111','11110/00001/00001/01110/00001/00001/11110','00010/00110/01010/10010/11111/00010/00010','11111/10000/10000/11110/00001/00001/11110','01110/10000/10000/11110/10001/10001/01110','11111/00001/00010/00100/01000/01000/01000','01110/10001/10001/01110/10001/10001/01110','01110/10001/10001/01111/00001/00001/01110','00000/00000/00000/11111/00000/00000/00000','00000/00000/00000/00000/00000/00110/00110','00000/00000/00000/00000/00000/00000/11111','00001/00001/00010/00100/01000/10000/10000']))

def text(x,y,s,size=20,cls='',anchor='start',extra=''):
    value=str(s);token=hashlib.sha256(f'{x}/{y}/{size}/{cls}/{value}'.encode()).hexdigest()[:12]
    if 'font-style="italic"' in extra:
        return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'
    curves=['cubic-bezier(.12,.7,.22,1)','cubic-bezier(.18,.82,.3,1)','cubic-bezier(.08,.6,.2,1)']
    style='<style>@keyframes reel-settle{0%{transform:translateY(-60px)}84%{transform:translateY(.65px)}94%{transform:translateY(-.18px)}100%{transform:translateY(0)}}@keyframes line-settle{0%{transform:translateY(-60px)}88%{transform:translateY(.8px)}100%{transform:translateY(0)}}@media(prefers-reduced-motion:reduce){.reel-column,.reel-line{animation:none!important}}</style>'
    if cls not in ('muted','label'):
        unit=size/10;width=max(0,len(value)*6*unit-unit)
        left=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
        columns=[]
        for i,c in enumerate(value.upper()):
            cells=[]
            for slot in range(7):
                char=c if slot==0 or not c.isalnum() else ('0123456789' if c.isdigit() else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')[(ord(c)+slot*7+i)% (10 if c.isdigit() else 26)]
                glyph='00000/00000/00000/00000/00110/00100/01000' if char==',' else PIXEL_GLYPHS.get(char,'00000/'*6+'00000')
                for row,bits in enumerate(glyph.split('/')):
                    for col,on in enumerate(bits):
                        if on=='1':cells.append(f'M{col} {slot*10+row}h.92v.92h-.92Z')
            # Fixed increasing settle times guarantee high-place digits settle before lower places.
            duration=1.05+i*.075+(int(token[:2],16)%5)*.065
            clip=f'reel-{token}-{i}'
            columns.append(f'<g transform="translate({i*6} 0)"><defs><clipPath id="{clip}"><rect x="-.2" y="-1" width="5.5" height="9"/></clipPath></defs><g clip-path="url(#{clip})"><g class="reel-column" style="animation:reel-settle {duration:.3f}s {curves[i%3]} 1 both"><path d="{"".join(cells)}"/></g></g></g>')
        return style+f'<g class="pixel-type" aria-label="{esc(value)}" transform="translate({left:.3f} {y-7*unit:.3f}) scale({unit:.3f})"><title>{esc(value)}</title>{"".join(columns)}</g>'
    effective=size*.84 if cls=='muted' else size;clip='line-'+token
    lines=''.join(f'<text x="{x}" y="{y+k*20}" font-size="{effective}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>' for k in range(4))
    duration=1.15+(int(token[:4],16)%13)*.095
    return style+f'<g aria-label="{esc(value)}"><defs><clipPath id="{clip}"><rect x="0" y="{y-effective-2}" width="900" height="{effective+6}"/></clipPath></defs><g clip-path="url(#{clip})"><g class="reel-line" style="animation:line-settle {duration:.3f}s {curves[int(token[0],16)%3]} 1 both">{lines}</g></g></g>'

def ornaments(kind, dark=False, mobile=False):
    """Original vector miniatures; no third-party artwork or external requests."""
    ink = '#dce6ef' if dark else '#29364b'
    paper = '#263345' if dark else '#f2f6fc'
    blue = '#75a9ff' if dark else '#3b78d6'
    style = '''<style>
    .float{animation:float 6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
    .blink{animation:blink 7s infinite;transform-box:fill-box;transform-origin:center}
    .tap{animation:tap 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
    .twinkle{animation:twinkle 5s ease-in-out infinite}
    @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
    @keyframes blink{0%,44%,48%,100%{transform:scaleY(1)}46%{transform:scaleY(.15)}}
    @keyframes tap{0%,100%{transform:translateY(0)}50%{transform:translateY(3px)}}
    @keyframes twinkle{0%,100%{opacity:.45}50%{opacity:1}}
    @media(prefers-reduced-motion:reduce){.float,.blink,.tap,.twinkle{animation:none}}
    </style>'''
    if kind == 'orbit':
        x,y,scale = (426,21,.48) if mobile else (795,43,.72)
        return style + f'''<g transform="translate({x} {y}) scale({scale})"><g class="float">
        <circle cx="0" cy="0" r="22" fill="{paper}" stroke="{ink}" stroke-width="1.6"/>
        <path d="M-12-12Q-5-19 3-18M10 11l3 2" fill="none" stroke="{blue}" stroke-width="3" stroke-linecap="round"/>
        <ellipse rx="39" ry="9" transform="rotate(-25)" fill="none" stroke="#d8b64c" stroke-width="2.4"/>
        <circle cx="34" cy="-16" r="3" fill="{blue}"/></g>
        <path class="twinkle" d="M-49-25v10m-5-5h10M41 24v8m-4-4h8" stroke="#d8b64c" stroke-width="1.6" stroke-linecap="round"/></g>'''
    x,y,scale = (416,15,.62) if mobile else (818,12,.75)
    return style + f'''<g transform="translate({x} {y}) scale({scale})">
    <path d="M-26 37Q-44 38-36 21" fill="none" stroke="{ink}" stroke-width="3" stroke-linecap="round"/>
    <path d="M-24 35L-23 6-11 13Q0 9 11 13L23 6 24 35Q0 46-24 35" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
    <path d="M-19 13l6 4m26 0 6-4" stroke="#d8b64c" stroke-width="3" stroke-linecap="round"/>
    <g class="blink" fill="{ink}"><ellipse cx="-9" cy="25" rx="1.7" ry="2.3"/><ellipse cx="9" cy="25" rx="1.7" ry="2.3"/></g>
    <path d="M-3 30q3 4 6 0" fill="none" stroke="{ink}" stroke-width="1.5" stroke-linecap="round"/>
    <rect x="-31" y="39" width="62" height="12" rx="4" fill="{blue}"/>
    <path d="M-22 45h5m5 0h5m5 0h5m5 0h5m5 0h5" stroke="{paper}" stroke-width="2"/>
    <g class="tap" fill="{paper}" stroke="{ink}" stroke-width="1.5"><ellipse cx="-14" cy="39" rx="7" ry="4"/><ellipse cx="14" cy="39" rx="7" ry="4"/></g></g>'''

def data_ornament(key, value, x, y, dark=False):
    """Milestone decorations derive only from the successful public snapshot."""
    ink='#dce6ef' if dark else '#29364b';blue='#75a9ff' if dark else '#3b78d6';paper='#263345' if dark else '#f2f6fc'
    style='''<style>.bob{animation:bob 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.pulse{animation:pulse 5s ease-in-out infinite}@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}@keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.bob,.pulse{animation:none}}</style>'''
    body=''
    if key=='stars':
        n=min(5,value//50)
        for i in range(5):
            fill='#d8b64c' if i<n else paper
            body+=f'<path transform="translate({(i-2)*16} 0)" d="M0-6 2-2 6-2 3 1 4 6 0 3-4 6-3 1-6-2-2-2Z" fill="{fill}" stroke="#bca04b" stroke-width=".7"/>'
        desc=f'{value} public stars; each filled star marks 50, capped at 250'
    elif key=='repos':
        n=min(12,value)
        for i in range(n):
            xx=(i-(n-1)/2)*7
            body+=f'<rect x="{xx-2.5}" y="-7" width="5" height="14" rx="1" fill="{blue if i%3 else "#d8b64c"}"/><path d="M{xx-1} -3h2" stroke="{paper}"/>'
        body+=f'<path d="M-48 9h96" stroke="{ink}" stroke-width="1.2"/>'
        desc=f'{value} public repositories; one book per repository, up to 12'
    elif key=='forks':
        body=f'<path d="M-28 5H0V-5H28M0 5h28" fill="none" stroke="{blue}" stroke-width="1.5"/>'
        for xx,yy in [(-28,5),(28,-5),(28,5)]:body+=f'<circle class="pulse" cx="{xx}" cy="{yy}" r="3" fill="#d8b64c" stroke="{ink}" stroke-width=".6"/>'
        desc=f'{value} public forks; decorative branch diagram, not a live event stream'
    else:
        width=70*(value%1000)/1000
        body=f'<path d="M-40 9h70" stroke="{paper}" stroke-width="3"/><path d="M-40 9h{width:.2f}" stroke="{blue}" stroke-width="3"/><g class="bob"><rect x="32" y="-9" width="18" height="15" rx="4" fill="{paper}" stroke="{ink}"/><path d="M41-9v-4" stroke="{ink}"/><circle cx="41" cy="-14" r="2" fill="#d8b64c"/><circle cx="37" cy="-2" r="1" fill="{ink}"/><circle cx="45" cy="-2" r="1" fill="{ink}"/><rect x="22" y="-4" width="10" height="10" rx="1" fill="#d8b64c" stroke="{ink}" stroke-width=".7"/></g>'
        desc=f'{value} release asset downloads; progress toward next 1000-download milestone; robot motion is decorative'
    return style+f'<g transform="translate({x} {y})"><title>{esc(desc)}</title>{body}</g>'

def calendar_companion(days, dark=False, mobile=False):
    active=[i for i,(_,level) in enumerate(days) if level>0]
    if not active:return ''
    i=active[-1];date,level=days[i];start=dt.date.fromisoformat(days[0][0]);offset=(start.weekday()+1)%7
    cols=(offset+len(days)+6)//7;col=(offset+i)//7
    width=444 if mobile else 864;x=18+width*(col/max(1,cols-1));y=352 if mobile else int(65+7*min(16,864/cols)+46)
    ink='#dce6ef' if dark else '#29364b';blue='#75a9ff' if dark else '#3b78d6';paper='#263345' if dark else '#f2f6fc'
    # A small rover points to the latest active week without changing calendar cells.
    return f'''<style>.bob{{animation:bob 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}@media(prefers-reduced-motion:reduce){{.bob{{animation:none}}}}</style><path d="M18 {y+7}H{18+width}" stroke="{blue}" stroke-opacity=".25" stroke-dasharray="2 5"/>
    <g transform="translate({min(18+width-16,max(34,x)):.2f} {y})"><title>Rover marks latest active week: {date}, GitHub intensity {level}; not live activity</title><g class="bob"><rect x="-11" y="-11" width="22" height="13" rx="5" fill="{paper}" stroke="{ink}"/><path d="M0-11v-6m-3 0h6" stroke="#d8b64c" stroke-width="1.4"/><circle cx="-4" cy="-5" r="1.5" fill="{blue}"/><circle cx="4" cy="-5" r="1.5" fill="{blue}"/></g><circle cx="-7" cy="4" r="3" fill="{ink}"/><circle cx="7" cy="4" r="3" fill="{ink}"/></g>'''

def language_plane(x,y,language,dark=False):
    return f'<g transform="translate({x:.2f} {y}) scale(.7)"><title>Paper plane marks largest repository-language segment: {esc(language)}</title><path d="M-13-5 14-10 2 8-1 0Z" fill="#d8b64c" stroke="{"#dce6ef" if dark else "#29364b"}" stroke-width="1" stroke-linejoin="round"/><path d="M-1 0 14-10" stroke="#fff" stroke-width="1"/></g>'

def project_scene(name,stars,maximum,dark=False,mobile=False):
    """Original project identity scenes; interest meter measures cumulative Stars only."""
    ink='#dce6ef' if dark else '#29364b';paper='#263345' if dark else '#f2f6fc';blue='#75a9ff' if dark else '#3b78d6';yellow='#d8b64c'
    x,y,scale=(265,83,.48) if mobile else (558,42,.85)
    style='''<style>
.robot-hop{animation:robot-hop 4.6s linear infinite}.star-loop{animation:star-loop 4.6s cubic-bezier(.37,0,.63,1) infinite}.fly-a{animation:fly-a 4.8s linear infinite}.fly-b{animation:fly-b 6.3s linear infinite}.fly-c{animation:fly-c 5.6s linear infinite}.sun-arc{animation:sun-arc 10s linear infinite;transform:rotate(90deg)}.leaf-sway{animation:leaf-sway 5s ease-in-out infinite;transform-origin:-12px 18px}.coin-flight{animation:coin-flight 4.8s linear infinite}.glow{animation:glow 4s ease-in-out infinite}
@keyframes robot-hop{0%,12%,100%{transform:translate(-4px,0) rotate(-3deg) scale(1)}18%{transform:translate(-3px,2px) rotate(-5deg) scale(1.06,.92);animation-timing-function:cubic-bezier(.18,.7,.3,1)}33%{transform:translate(5px,-11px) rotate(3deg) scale(.97,1.03);animation-timing-function:cubic-bezier(.55,0,.85,.45)}47%{transform:translate(12px,1px) rotate(5deg) scale(1.06,.94)}52%,61%{transform:translate(12px,0) rotate(2deg) scale(1)}67%{transform:translate(11px,2px) rotate(4deg) scale(1.04,.95);animation-timing-function:cubic-bezier(.18,.7,.3,1)}80%{transform:translate(3px,-7px) rotate(-4deg) scale(.98,1.02);animation-timing-function:cubic-bezier(.55,0,.85,.45)}93%{transform:translate(-4px,1px) rotate(-4deg) scale(1.04,.96)}}
@keyframes star-loop{0%,100%{transform:translate(-3px,-4px) rotate(-10deg)}35%{transform:translate(7px,-12px) rotate(15deg)}65%{transform:translate(2px,5px) rotate(-5deg)}}
@keyframes fly-a{0%{transform:translate(0.00px,0.00px)}6.25%{transform:translate(2.30px,0.46px)}12.5%{transform:translate(4.24px,1.76px)}18.75%{transform:translate(5.54px,3.70px)}25%{transform:translate(6.00px,6.00px)}31.25%{transform:translate(5.54px,8.30px)}37.5%{transform:translate(4.24px,10.24px)}43.75%{transform:translate(2.30px,11.54px)}50%{transform:translate(0.00px,12.00px)}56.25%{transform:translate(-2.30px,11.54px)}62.5%{transform:translate(-4.24px,10.24px)}68.75%{transform:translate(-5.54px,8.30px)}75%{transform:translate(-6.00px,6.00px)}81.25%{transform:translate(-5.54px,3.70px)}87.5%{transform:translate(-4.24px,1.76px)}93.75%{transform:translate(-2.30px,0.46px)}100%{transform:translate(-0.00px,0.00px)}}
@keyframes fly-b{0%{transform:translate(0.00px,-0.00px)}6.25%{transform:translate(1.91px,-0.46px)}12.5%{transform:translate(3.54px,-1.76px)}18.75%{transform:translate(4.62px,-3.70px)}25%{transform:translate(5.00px,-6.00px)}31.25%{transform:translate(4.62px,-8.30px)}37.5%{transform:translate(3.54px,-10.24px)}43.75%{transform:translate(1.91px,-11.54px)}50%{transform:translate(0.00px,-12.00px)}56.25%{transform:translate(-1.91px,-11.54px)}62.5%{transform:translate(-3.54px,-10.24px)}68.75%{transform:translate(-4.62px,-8.30px)}75%{transform:translate(-5.00px,-6.00px)}81.25%{transform:translate(-4.62px,-3.70px)}87.5%{transform:translate(-3.54px,-1.76px)}93.75%{transform:translate(-1.91px,-0.46px)}100%{transform:translate(-0.00px,-0.00px)}}
@keyframes fly-c{0%{transform:translate(0.00px,-0.00px)}6.25%{transform:translate(3.06px,-0.84px)}12.5%{transform:translate(5.66px,-3.22px)}18.75%{transform:translate(7.39px,-6.79px)}25%{transform:translate(8.00px,-11.00px)}31.25%{transform:translate(7.39px,-15.21px)}37.5%{transform:translate(5.66px,-18.78px)}43.75%{transform:translate(3.06px,-21.16px)}50%{transform:translate(0.00px,-22.00px)}56.25%{transform:translate(-3.06px,-21.16px)}62.5%{transform:translate(-5.66px,-18.78px)}68.75%{transform:translate(-7.39px,-15.21px)}75%{transform:translate(-8.00px,-11.00px)}81.25%{transform:translate(-7.39px,-6.79px)}87.5%{transform:translate(-5.66px,-3.22px)}93.75%{transform:translate(-3.06px,-0.84px)}100%{transform:translate(-0.00px,-0.00px)}}
@keyframes sun-arc{0%{transform:rotate(0deg);opacity:0}8%{opacity:1}84%{opacity:1}92%{transform:rotate(180deg);opacity:0}100%{transform:rotate(180deg);opacity:0}}
@keyframes leaf-sway{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(9deg)}}
@keyframes coin-flight{0%,12%{transform:translate(-28px,-7px);opacity:0}14.000%{transform:translate(-28.000px,-7.000px);opacity:1}16.167%{transform:translate(-26.833px,-10.382px);opacity:1}18.333%{transform:translate(-25.667px,-13.444px);opacity:1}20.500%{transform:translate(-24.500px,-16.188px);opacity:1}22.667%{transform:translate(-23.333px,-18.611px);opacity:1}24.833%{transform:translate(-22.167px,-20.715px);opacity:1}27.000%{transform:translate(-21.000px,-22.500px);opacity:1}29.167%{transform:translate(-19.833px,-23.965px);opacity:1}31.333%{transform:translate(-18.667px,-25.111px);opacity:1}33.500%{transform:translate(-17.500px,-25.938px);opacity:1}35.667%{transform:translate(-16.333px,-26.444px);opacity:1}37.833%{transform:translate(-15.167px,-26.632px);opacity:1}40.000%{transform:translate(-14.000px,-26.500px);opacity:1}42.167%{transform:translate(-12.833px,-26.049px);opacity:1}44.333%{transform:translate(-11.667px,-25.278px);opacity:1}46.500%{transform:translate(-10.500px,-24.188px);opacity:1}48.667%{transform:translate(-9.333px,-22.778px);opacity:1}50.833%{transform:translate(-8.167px,-21.049px);opacity:1}53.000%{transform:translate(-7.000px,-19.000px);opacity:1}55.167%{transform:translate(-5.833px,-16.632px);opacity:1}57.333%{transform:translate(-4.667px,-13.944px);opacity:1}59.500%{transform:translate(-3.500px,-10.938px);opacity:1}61.667%{transform:translate(-2.333px,-7.611px);opacity:1}63.833%{transform:translate(-1.167px,-3.965px);opacity:1}66.000%{transform:translate(0.000px,-0.000px);opacity:1}67.500%{transform:translate(0,-1.528px);opacity:1}69.000%{transform:translate(0,-2.778px);opacity:1}70.500%{transform:translate(0,-3.750px);opacity:1}72.000%{transform:translate(0,-4.444px);opacity:1}73.500%{transform:translate(0,-4.861px);opacity:1}75.000%{transform:translate(0,-5.000px);opacity:1}76.500%{transform:translate(0,-4.861px);opacity:1}78.000%{transform:translate(0,-4.444px);opacity:1}79.500%{transform:translate(0,-3.750px);opacity:1}81.000%{transform:translate(0,-2.778px);opacity:1}82.500%{transform:translate(0,-1.528px);opacity:1}84.000%{transform:translate(0,-0.000px);opacity:1}92%{transform:translate(0,0);opacity:1}100%{transform:translate(0,0);opacity:0}}
@keyframes glow{0%,100%{opacity:.55}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.robot-hop,.star-loop,.fly-a,.fly-b,.fly-c,.sun-arc,.leaf-sway,.coin-flight,.glow{animation:none}}
</style>'''
    if name=='Bilibili_Innocent_Lab':
        scene=f'<path d="M-33 20H34" stroke="{ink}" stroke-opacity=".25"/><g class="robot-hop"><rect x="-28" y="-15" width="38" height="30" rx="9" fill="{paper}" stroke="{ink}" stroke-width="1.7"/><rect x="-24" y="-11" width="30" height="20" rx="6" fill="{blue}" opacity=".09"/><path d="M-23-11h13" stroke="#fff" stroke-opacity=".7" stroke-width="1.5" stroke-linecap="round"/><circle cx="-23" cy="5" r="1.5" fill="{yellow}"/><circle cx="5" cy="5" r="1.5" fill="{yellow}"/><path d="M-20-15l-5-9m27 9 5-9" stroke="{ink}" stroke-width="2" stroke-linecap="round"/><path d="M-19-2v6m17-6v6M-14 9h8" stroke="{blue}" stroke-width="2" stroke-linecap="round"/><path d="M-20 15v5m21-5v5" stroke="{ink}" stroke-width="3"/></g><path class="star-loop" d="M28-18l3 8 9 1-7 5 2 9-7-5-7 5 2-9-7-5 9-1Z" fill="{yellow}" stroke="{ink}" stroke-width="1"/>'
    elif name=='LumenCoacervationEngine':
        scene=f'<ellipse cx="0" cy="22" rx="30" ry="3" fill="{blue}" opacity=".1"/><path d="M-16-19h32v9l5 6v22q0 5-6 5h-30q-6 0-6-5V-4l5-6Z" fill="{paper}" stroke="{ink}" stroke-width="1.5"/><rect x="-18" y="-24" width="36" height="6" rx="2" fill="{yellow}"/><path d="M-14-4v17" stroke="{blue}" stroke-opacity=".45" stroke-width="3" stroke-linecap="round"/><path d="M-18-21h36m-32 3v-6m7 6v-6m7 6v-6m7 6v-6m7 6v-6" stroke="{ink}" stroke-opacity=".2" stroke-width=".7"/><path d="M-16 15q16 6 32 0" fill="none" stroke="{blue}" stroke-opacity=".25"/><path d="M-10-9v5m0 5v5" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity=".7"/><g class="glow" fill="{yellow}"><circle class="fly-a" cx="5" cy="-2" r="4"/><circle class="fly-b" cx="-3" cy="12" r="3"/><g class="fly-c"><ellipse cx="26" cy="-17" rx="3.5" ry="2" fill="{paper}" stroke="{blue}" stroke-width=".6"/><ellipse cx="32" cy="-17" rx="3.5" ry="2" fill="{paper}" stroke="{blue}" stroke-width=".6"/><circle cx="29" cy="-15" r="3"/><circle cx="29" cy="-15" r="6" opacity=".13"/></g></g><path d="M25-19l-3-3m11 1 3-3" stroke="{blue}" stroke-linecap="round"/>'
    elif name=='SplashScreenAdvanced':
        scene=f'<path d="M-35 18q35-9 70 0" fill="none" stroke="{blue}" stroke-opacity=".4"/><g transform="translate(0 13)"><g class="sun-arc"><circle cx="-27" cy="0" r="12" fill="{yellow}" opacity=".12"/><circle cx="-27" cy="0" r="9" fill="{yellow}"/><path d="M-32-5q4-4 8-1" fill="none" stroke="#fff" stroke-opacity=".65" stroke-width="1.4" stroke-linecap="round"/><path d="M-27-13v-3m0 29v3m-13-16h-3m29 0h3" stroke="{yellow}" stroke-width="1.5"/></g></g><path d="M-12 18V-5" stroke="{ink}" stroke-width="2"/><g class="leaf-sway"><path d="M-12 4q-20-2-17-16 17 0 17 16q18-4 18-17-16 0-18 17" fill="{paper}" stroke="{blue}" stroke-width="1.5"/><path d="M-12 4l-12-11m12 11L1-8" stroke="{blue}" stroke-opacity=".55" stroke-width=".7"/></g><path d="M-19 19q7-4 14 0m-24 2h4m23-1h5" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width=".8"/>'
    else:
        scene=f'<rect x="-29" y="-20" width="58" height="36" rx="6" fill="{paper}" stroke="{ink}" stroke-width="1.6"/><path d="M-25-13h49" stroke="{ink}" stroke-opacity=".2" stroke-width=".8"/><circle cx="-23" cy="-16" r="1" fill="{yellow}"/><circle cx="-19" cy="-16" r="1" fill="{blue}"/><path d="M-23 10h17m4 0h6" stroke="{blue}" stroke-opacity=".25" stroke-width="1"/><path d="M-18-8l6 5-6 5m12 0h12" fill="none" stroke="{blue}" stroke-width="2" stroke-linecap="round"/><path class="glow" d="M12 3h5" stroke="{yellow}" stroke-width="2"/><path d="M-7 16v7m14-7v7M-17 23h34" stroke="{ink}" stroke-width="1.5"/><g class="coin-flight"><circle cx="38" cy="9" r="7" fill="{yellow}"/><circle cx="38" cy="9" r="5.2" fill="none" stroke="{ink}" stroke-opacity=".3" stroke-width=".6"/><path d="M34 6q2-3 5-2" stroke="#fff" stroke-opacity=".7" fill="none" stroke-width="1"/><path d="M38 5v8m-2-6h4m-4 4h4" stroke="{ink}" stroke-width="1"/></g>'
    ratio=stars/maximum if maximum else 0
    meterx,metery,width=(407,98,50) if mobile else (792,70,60)
    meter=f'<g><title>Cumulative public Stars: {stars}; relative to most-starred featured project ({maximum}), not recent traffic or trend</title><rect x="{meterx}" y="{metery}" width="{width}" height="3" rx="1.5" fill="{paper}"/><rect x="{meterx}" y="{metery}" width="{width*ratio:.3f}" height="3" rx="1.5" fill="{yellow}"/></g>'
    return style+f'<g transform="translate({x} {y}) scale({scale})"><title>Original decorative scene for {esc(name)}</title>{scene}</g>'+meter

def render(s,dark):
    out={}
    out['header']=svg(128,text(450,63,'Many begin well; few see it through.',25,anchor='middle',extra='font-style="italic"')+'<path d="M414 87H486" stroke="#d8b64c" stroke-width="2"/>',dark,'Many begin well; few see it through.')
    body=''
    for i,(key,label) in enumerate([('stars','STARS'),('repos','REPOSITORIES'),('forks','FORKS'),('downloads','DOWNLOADS¹')]):
        x=112.5+i*225
        body+=text(x,53,format(s[key],','),42,anchor='middle')+text(x,81,label,cls='label',anchor='middle')
    out['header']=out['header'].replace('</svg>',ornaments('orbit',dark)+'</svg>')
    body+=''.join(data_ornament(k,s[k],112.5+i*225,108,dark) for i,k in enumerate(('stars','repos','forks','downloads')))
    out['stats']=svg(137,body,dark,'Public repository statistics; downloads across four featured projects')
    out['projects-title']=svg(64,text(18,44,'Projects',30,extra='font-weight="bold"'),dark,'Projects')
    out['projects-title']=out['projects-title'].replace('</svg>',ornaments('cat',dark)+'</svg>')
    for p in s['projects']:
        # Long names remain readable; repository links sit below the composite poster.
        size=26 if len(p['name'])<25 else 24
        body=text(18,34,p['name'],size,extra='font-weight="bold"')+text(18,62,p['description'],18,'muted')
        body+=text(710,38,p['version'],19,anchor='end')+text(822,35,p['stars'],25,anchor='middle')+text(822,59,'stars',15,'muted',anchor='middle')
        body+=project_scene(p['name'],p['stars'],max(q['stars'] for q in s['projects']),dark)
        body+='<path d="M18 88H882" class="rule"/>'
        out['project-'+p['name']]=svg(94,body,dark,p['name']+'; '+p['version']+'; '+str(p['stars'])+' stars')
    palette={'Kotlin':'#2367ee','Rust':'#566573','Java':'#9aa4b1','Python':'#d8b64c','Other':'#bcbfc5'}
    languages=sorted(s['languages'].items(),key=lambda x:(-x[1],{'Kotlin':0,'Rust':1,'Java':2,'Python':3}.get(x[0],99),x[0]))
    body=text(18,43,'Repository languages',30,extra='font-weight="bold"'); x=18; total=sum(s['languages'].values())
    for lang,count in languages:
        w=864*count/total
        body+=f'<rect x="{x:.3f}" y="66" width="{w:.3f}" height="23" fill="{palette.get(lang,"#8598ac")}"/>'
        x+=w
    for i,(lang,count) in enumerate(languages):
        x=18+(i%4)*216; y=120+(i//4)*30
        body+=f'<rect x="{x}" y="{y-12}" width="12" height="12" fill="{palette.get(lang,"#8598ac")}"/>'+text(x+21,y,f'{lang} {count}',17,'muted')
    body+=language_plane(18+432*languages[0][1]/total,98,languages[0][0],dark)
    h=162+max(0,(len(languages)-1)//4)*30
    body+=text(18,h-10,'Repos by primary language · includes public forks',13,'muted')
    out['languages']=svg(h,body,dark,'Number of public repositories by primary language, not code volume')
    days=s['calendar']; start=dt.date.fromisoformat(days[0][0]); offset=(start.weekday()+1)%7
    cols=(offset+len(days)+6)//7; step=min(16,864/cols); cell=step-3
    colors=['#e9ecf0','#c8daf9','#8ab0ef','#4e88e3','#2367ee'] if not dark else ['#21262d','#203b64','#2b5590','#3778cc','#6aa7ff']
    body=text(18,44,'Contributions',30,extra='font-weight="bold"')
    for i,(date,level) in enumerate(days):
        col,row=divmod(i+offset,7); x=18+col*step; y=65+row*step
        body+=f'<rect x="{x:.3f}" y="{y:.3f}" width="{cell:.3f}" height="{cell:.3f}" fill="{colors[level]}"><title>{esc(date)} · GitHub level {level}</title></rect>'
    y=65+7*step+22
    body+=text(18,y,f'{days[0][0]} — {days[-1][0]}',13,'muted')
    body+=calendar_companion(days,dark)
    out['contributions']=svg(int(y+54),body,dark,'Actual GitHub public contribution calendar, intensity levels 0 to 4')
    body=text(18,30,'¹ Release asset downloads across the four featured repositories; not unique users.',12,'muted')
    body+=text(18,52,'Updated '+s['checked_at'].replace('T',' ').replace('+00:00',' UTC').replace('Z',' UTC'),12,'muted')
    out['footnote']=svg(70,body,dark,'Statistics scope and last successful update')
    return out

def mobile_render(s,dark):
    out={}
    def wrap(h,body,title):
        return svg(h,body,dark,title).replace('width="900"','width="480"',1).replace('viewBox="0 0 900','viewBox="0 0 480',1)
    out['header']=wrap(100,text(240,48,'Many begin well; few see it through.',19,anchor='middle',extra='font-style="italic"')+'<path d="M212 68H268" stroke="#d8b64c" stroke-width="2"/>','Motto')
    body=''
    for i,(key,label) in enumerate([('stars','STARS'),('repos','REPOSITORIES'),('forks','FORKS'),('downloads','DOWNLOADS¹')]):
        x=120+(i%2)*240;y=43+(i//2)*110
        body+=text(x,y,format(s[key],','),36,anchor='middle')+text(x,y+25,label,cls='label',anchor='middle')
    out['header']=out['header'].replace('</svg>',ornaments('orbit',dark,True)+'</svg>')
    body+=''.join(data_ornament(k,s[k],120+(i%2)*240,90+(i//2)*110,dark) for i,k in enumerate(('stars','repos','forks','downloads')))
    out['stats']=wrap(225,body,'Public repository statistics')
    out['projects-title']=wrap(60,text(18,40,'Projects',28,extra='font-weight="bold"'),'Projects')
    out['projects-title']=out['projects-title'].replace('</svg>',ornaments('cat',dark,True)+'</svg>')
    for p in s['projects']:
        body=text(18,31,p['name'],23,extra='font-weight="bold"')+text(18,58,p['description'],16,'muted')
        body+=text(18,87,p['version'],16,'muted')+text(460,87,str(p['stars'])+' stars',16,'muted','end')+'<path d="M18 106H462" class="rule"/>'
        body+=project_scene(p['name'],p['stars'],max(q['stars'] for q in s['projects']),dark,True)
        out['project-'+p['name']]=wrap(112,body,p['name'])
    palette={'Kotlin':'#2367ee','Rust':'#566573','Java':'#9aa4b1','Python':'#d8b64c','Other':'#bcbfc5'}
    langs=sorted(s['languages'].items(),key=lambda x:(-x[1],{'Kotlin':0,'Rust':1,'Java':2,'Python':3}.get(x[0],99),x[0]));body=text(18,40,'Repository languages',28,extra='font-weight="bold"');x=18
    for lang,n in langs:
        w=444*n/sum(s['languages'].values());body+=f'<rect x="{x:.3f}" y="60" width="{w:.3f}" height="20" fill="{palette.get(lang,"#8598ac")}"/>';x+=w
    for i,(lang,n) in enumerate(langs):
        x=18+i%2*230;y=107+i//2*26;body+=f'<rect x="{x}" y="{y-12}" width="12" height="12" fill="{palette.get(lang,"#8598ac")}"/>'+text(x+20,y,f'{lang} {n}',16,'muted')
    body+=language_plane(18+222*langs[0][1]/sum(s['languages'].values()),88,langs[0][0],dark)
    h=142+((len(langs)-1)//2)*26
    body+=text(18,h-10,'Primary language per public repo; includes forks.',12,'muted')
    out['languages']=wrap(h,body,'Repository primary languages')
    days=s['calendar'];offset=(dt.date.fromisoformat(days[0][0]).weekday()+1)%7
    colors=['#e9ecf0','#c8daf9','#8ab0ef','#4e88e3','#2367ee'] if not dark else ['#21262d','#203b64','#2b5590','#3778cc','#6aa7ff']
    body=text(18,40,'Contributions',28,extra='font-weight="bold"')
    for i,(date,level) in enumerate(days):
        col,row=divmod(i+offset,7);panel,col=divmod(col,27);x=18+col*16.4;y=62+panel*143+row*16.4
        body+=f'<rect x="{x:.2f}" y="{y:.2f}" width="13.4" height="13.4" fill="{colors[level]}"><title>{esc(date)} · GitHub level {level}</title></rect>'
    body+=text(18,334,days[0][0]+' — '+days[-1][0],13,'muted')
    body+=calendar_companion(days,dark,True)
    out['contributions']=wrap(378,body,'Actual contribution calendar; chronological rows of 27 weeks')
    body=text(18,25,'¹ Downloads: four featured repos; not unique users.',12,'muted')+text(18,47,'Updated '+s['checked_at'][:19].replace('T',' ')+' UTC',12,'muted')
    out['footnote']=wrap(65,body,'Statistics scope and update time')
    return out

def picture(name,alt,url=None):
    p=f'<picture>\n  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{name}-mobile-dark.svg">\n  <source media="(max-width: 600px)" srcset="assets/{name}-mobile-light.svg">\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n  <img alt="{esc(alt)}" src="assets/{name}-light.svg" width="900">\n</picture>'
    return (f'<a href="{esc(url)}">\n{p}\n</a>' if url else p)

def entrance_pass(content,kind):
    """One-shot entrance wrappers keep ongoing animation transforms independent."""
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns);root=ET.fromstring(content)
    style=ET.Element('{'+ns+'}style')
    style.text='@keyframes enter-rise{0%{opacity:0;transform:translateY(10px) scale(.9)}72%{opacity:1;transform:translateY(-1.4px) scale(1.015)}100%{opacity:1;transform:translateY(0) scale(1)}}@keyframes enter-land{0%{opacity:0;transform:translateY(-15px) rotate(-8deg)}65%{opacity:1;transform:translateY(2px) rotate(2deg)}84%{transform:translateY(-1px) rotate(-1deg)}100%{opacity:1;transform:translateY(0) rotate(0deg)}}@keyframes enter-fly{0%{opacity:0;transform:translate(-20px,8px) rotate(-15deg)}76%{opacity:1;transform:translate(2px,-1px) rotate(2deg)}100%{opacity:1;transform:translate(0,0) rotate(0deg)}}@keyframes enter-grow{0%{opacity:0;transform:scaleX(0)}100%{opacity:1;transform:scaleX(1)}}@keyframes enter-cell{0%{opacity:0;transform:scale(.2)}75%{opacity:1;transform:scale(1.08)}100%{opacity:1;transform:scale(1)}}@media(prefers-reduced-motion:reduce){.entrance{animation:none!important;opacity:1!important}}'
    root.insert(1,style);count=0
    for element in list(root):
        tag=element.tag.rsplit('}',1)[-1];effect=None;delay=.15
        if tag=='g' and 'aria-label' not in element.attrib and 'pixel-type' not in element.get('class',''):
            title=''.join(element.itertext())
            effect='enter-rise'
            if 'Bilibili' in title or 'plane' in title:effect='enter-fly'
            elif 'Lumen' in title or kind=='projects-title':effect='enter-land'
            elif 'Cumulative public Stars' in title:effect='enter-grow'
            elif kind=='header':effect='enter-fly'
            delay=.25+(count%5)*.12
        elif tag=='rect' and element.get('x') is not None and element.get('width')!='900':
            effect='enter-cell' if kind=='contributions' else 'enter-grow'
            delay=.3+float(element.get('x','0'))*.0014+(float(element.get('y','0'))%29)*.008
        elif tag=='path' and element.get('class')=='rule':effect='enter-grow';delay=.4
        if effect:
            index=list(root).index(element);root.remove(element)
            wrap=ET.Element('{'+ns+'}g',{'class':'entrance','style':f'transform-box:fill-box;transform-origin:{"left center" if effect=="enter-grow" else "center"};animation:{effect} {1.0+(count%3)*.12:.2f}s cubic-bezier(.18,.7,.3,1) {delay:.3f}s 1 both'})
            wrap.append(element);root.insert(index,wrap);count+=1
    return ET.tostring(root,encoding='unicode')

def outputs(s):
    out={}
    for dark in (False,True):
        for name,content in mobile_render(s,dark).items(): out[f'assets/{name}-mobile-{"dark" if dark else "light"}.svg']=content
        for name,content in render(s,dark).items(): out[f'assets/{name}-{"dark" if dark else "light"}.svg']=content
    parts=[picture('header','Many begin well; few see it through.'),picture('stats','Public repository statistics'),picture('projects-title','Projects')]
    parts += [picture('project-'+p['name'],p['name']+' — '+p['description'],f'https://github.com/{OWNER}/{p["name"]}') for p in s['projects']]
    parts += [picture('languages','Repository count by primary language'),picture('contributions','GitHub contribution calendar',f'https://github.com/{OWNER}?tab=overview'),picture('footnote','Statistics scope and update time')]
    order=['header','stats','projects-title']+['project-'+p['name'] for p in s['projects']]+['languages','contributions','footnote']
    for dark in (False,True):
        for mobile in (False,True):
            theme='dark' if dark else 'light';suffix=('-mobile' if mobile else '')+'-'+theme
            width=480 if mobile else 900;y=0;panels=[]
            for name in order:
                panel=entrance_pass(out[f'assets/{name}{suffix}.svg'],name)
                h=int(re.search(r'height="(\d+)"',panel).group(1))
                panel=panel.replace('<svg ',f'<svg x="0" y="{y}" ',1)
                panels.append(panel);y+=h
            wall='#0d1117' if dark else '#f1eee7';curl='#363946' if dark else '#e4d3af';ink='#05070a' if dark else '#8b7753'
            # One SVG clock moves the entire sheet, keeping typography and all sections aligned.
            css='<style>.poster-sheet{animation:none;transform-box:fill-box;transform-origin:20% 2%}.poster-flutter{animation:none;transform-box:fill-box;transform-origin:20% 2%}.poster-curl{animation:curl-gust 7.1s cubic-bezier(.22,.7,.3,1) infinite;transform-box:fill-box;transform-origin:bottom right}.paper-shadow{animation:none}@keyframes paper-gust{0%,9%,100%{transform:translate(0,0) rotate(0deg) skewY(0deg)}16%{transform:translate(-2px,-1px) rotate(-.12deg) skewY(-.08deg)}23%{transform:translate(-3px,-3px) rotate(-.35deg) skewY(-.12deg)}29%{transform:translate(1px,0) rotate(.13deg) skewY(.05deg)}36%{transform:translate(-1px,-1px) rotate(-.07deg)}43%,57%{transform:translate(0,0) rotate(0deg)}63%{transform:translate(-1px,-2px) rotate(-.18deg)}69%{transform:translate(-3px,-3px) rotate(-.3deg) skewY(-.1deg)}74%{transform:translate(2px,0) rotate(.12deg)}81%{transform:translate(-1px,-1px) rotate(-.07deg)}90%{transform:translate(0,0) rotate(.02deg)}}@keyframes paper-flutter{0%,100%{transform:translate(0,0) rotate(0deg)}21%{transform:translate(.7px,-.4px) rotate(.025deg)}38%{transform:translate(-.8px,.3px) rotate(-.035deg)}62%{transform:translate(.3px,-.2px) rotate(.015deg)}78%{transform:translate(0,0)}}@keyframes curl-gust{0%,9%,100%{transform:scale(1)}23%{transform:scale(2.2,1.9) skewX(-8deg)}29%{transform:scale(1.2,1.1)}36%{transform:scale(1.45,1.3)}43%,57%{transform:scale(1.05)}69%{transform:scale(1.95,1.7) skewX(-6deg)}74%{transform:scale(1.15)}81%{transform:scale(1.3,1.2)}90%{transform:scale(1)}}@keyframes shadow-gust{0%,9%,43%,57%,100%{opacity:.12}23%,69%{opacity:.28}29%,74%{opacity:.15}36%,81%{opacity:.2}}@media(prefers-reduced-motion:reduce){.poster-sheet,.poster-flutter,.poster-curl,.paper-shadow{animation:none}}</style>'
            pad=24;w=width+pad*2;h=y+pad*2
            shadow=f'<rect class="paper-shadow" x="{pad+4}" y="{pad+6}" width="{width}" height="{y}" rx="2" fill="{ink}" opacity=".12"/>'
            corner=f'<g class="poster-curl"><path d="M{width-34} {y}Q{width-12} {y-8} {width} {y-36}L{width} {y}Z" fill="{wall}"/><path d="M{width-34} {y}Q{width-13} {y-10} {width} {y-36}Q{width-24} {y-30} {width-34} {y}Z" fill="{curl}" stroke="{ink}" stroke-opacity=".2"/></g>'
            out[f'assets/poster{suffix}.svg']=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Animated project statistics poster"><title>Public project statistics, updated every six hours</title>{css}<rect width="{w}" height="{h}" fill="{wall}"/>{shadow}<g transform="translate({pad} {pad})"><g class="poster-sheet"><g class="poster-flutter">'+''.join(panels)+corner+'</g></g></g></svg>'
    links=' · '.join(f'<a href="https://github.com/{OWNER}/{p["name"]}">{p["name"]}</a>' for p in s['projects'])
    out['assets/portal.svg']='<svg xmlns="http://www.w3.org/2000/svg" width="48" height="40" viewBox="0 0 48 40" role="img" aria-label="Explore the interactive paper"><circle cx="24" cy="20" r="11" fill="#f5edda" stroke="#4479c4"/><ellipse cx="24" cy="20" rx="21" ry="6" transform="rotate(-25 24 20)" fill="none" stroke="#c7a341" stroke-width="1.5"/><circle cx="42" cy="10" r="2" fill="#c7a341"/></svg>'
    portal='<p align="right"><a href="https://paper-observatory.airymink6.chatgpt.site" title="探索互动纸张"><img src="assets/portal.svg" width="40" height="34" alt="探索互动主页"></a></p>\n'
    out['README.md']=portal+picture('poster','Animated public project statistics poster',f'https://github.com/{OWNER}?tab=overview')+'\n\n<p align="center">'+links+'</p>\n'

    out['data/snapshot.json']=json.dumps(s,ensure_ascii=False,indent=2)+'\n'
    return out

def write_all(out,root=ROOT):
    # All validation/rendering finishes before any file is replaced. CI publishes one commit.
    staged=[]
    try:
        for path,body in out.items():
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(dir=target.parent,prefix='.stage-')
            with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(body);f.flush();os.fsync(f.fileno())
            staged.append((tmp,target))
        for tmp,target in staged:os.replace(tmp,target)
    finally:
        for tmp,_ in staged:
            if os.path.exists(tmp):os.unlink(tmp)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--calendar',type=Path);a=p.parse_args()
    if bool(a.source)!=bool(a.calendar):p.error('Provide both --source and --calendar')
    if a.source:
        source=json.loads(a.source.read_text());raw=a.calendar.read_text()
    else:
        token=os.environ.get('GITHUB_TOKEN')
        repos=pages(f'/users/{OWNER}/repos?type=owner',token)
        repos=[{k:r[k] for k in ('name','full_name','private','fork','language','stargazers_count','forks_count')} for r in repos if not r['private']]
        releases={name:pages(f'/repos/{OWNER}/{name}/releases',token) for name in FEATURED}
        # Public HTML requires no PAT and exposes no private repository names.
        raw=get(f'https://github.com/users/{OWNER}/contributions')
        source={'repos':repos,'releases':releases,'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}
    s=summarize(source,calendar(raw));write_all(outputs(s))
    print('Generated verified snapshot:',s['checked_at'],s['repos'],'public repositories',len(s['calendar']),'calendar days')

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'Update failed ({type(e).__name__}); no new snapshot published.',file=sys.stderr);sys.exit(1)
