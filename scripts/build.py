#!/usr/bin/env python3
"""Public-only GitHub profile. Standard library; no persistent credentials."""
import argparse, collections, datetime as dt, html, json, os, re, sys, tempfile
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

def svg(height, body, dark=False, title='Profile statistics'):
    bg,ink,muted,line=('#0d1117','#f0eee8','#a8b4c4','#30363d') if dark else ('#ffffff','#16191c','#626d80','#e4e7eb')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title><style>text{{fill:{ink};font-family:Georgia,'Times New Roman',serif}}.muted{{fill:{muted}}}.label{{font:12px monospace;letter-spacing:1.2px;fill:{muted}}}.rule{{stroke:{line}}}</style><rect width="900" height="{height}" fill="{bg}"/>{body}</svg>'''

def text(x,y,s,size=20,cls='',anchor='start',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'

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

def render(s,dark):
    out={}
    out['header']=svg(128,text(450,63,'Many begin well; few see it through.',25,anchor='middle',extra='font-style="italic"')+'<path d="M414 87H486" stroke="#d8b64c" stroke-width="2"/>',dark,'Many begin well; few see it through.')
    body=''
    for i,(key,label) in enumerate([('stars','STARS'),('repos','REPOSITORIES'),('forks','FORKS'),('downloads','DOWNLOADS¹')]):
        x=112.5+i*225
        body+=text(x,53,format(s[key],','),42,anchor='middle')+text(x,81,label,cls='label',anchor='middle')
    out['header']=out['header'].replace('</svg>',ornaments('orbit',dark)+'</svg>')
    out['stats']=svg(112,body,dark,'Public repository statistics; downloads across four featured projects')
    out['projects-title']=svg(64,text(18,44,'Projects',30,extra='font-weight="bold"'),dark,'Projects')
    out['projects-title']=out['projects-title'].replace('</svg>',ornaments('cat',dark)+'</svg>')
    for p in s['projects']:
        # Long names remain readable at native README width; each entire image is linked.
        size=26 if len(p['name'])<25 else 24
        body=text(18,34,p['name'],size,extra='font-weight="bold"')+text(18,62,p['description'],18,'muted')
        body+=text(710,38,p['version'],19,anchor='end')+text(822,35,p['stars'],25,anchor='middle')+text(822,59,'stars',15,'muted',anchor='middle')
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
    out['contributions']=svg(int(y+18),body,dark,'Actual GitHub public contribution calendar, intensity levels 0 to 4')
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
        x=120+(i%2)*240;y=43+(i//2)*88
        body+=text(x,y,format(s[key],','),36,anchor='middle')+text(x,y+25,label,cls='label',anchor='middle')
    out['header']=out['header'].replace('</svg>',ornaments('orbit',dark,True)+'</svg>')
    out['stats']=wrap(180,body,'Public repository statistics')
    out['projects-title']=wrap(60,text(18,40,'Projects',28,extra='font-weight="bold"'),'Projects')
    out['projects-title']=out['projects-title'].replace('</svg>',ornaments('cat',dark,True)+'</svg>')
    for p in s['projects']:
        body=text(18,31,p['name'],23,extra='font-weight="bold"')+text(18,58,p['description'],16,'muted')
        body+=text(18,87,p['version'],16,'muted')+text(460,87,str(p['stars'])+' stars',16,'muted','end')+'<path d="M18 106H462" class="rule"/>'
        out['project-'+p['name']]=wrap(112,body,p['name'])
    palette={'Kotlin':'#2367ee','Rust':'#566573','Java':'#9aa4b1','Python':'#d8b64c','Other':'#bcbfc5'}
    langs=sorted(s['languages'].items(),key=lambda x:(-x[1],{'Kotlin':0,'Rust':1,'Java':2,'Python':3}.get(x[0],99),x[0]));body=text(18,40,'Repository languages',28,extra='font-weight="bold"');x=18
    for lang,n in langs:
        w=444*n/sum(s['languages'].values());body+=f'<rect x="{x:.3f}" y="60" width="{w:.3f}" height="20" fill="{palette.get(lang,"#8598ac")}"/>';x+=w
    for i,(lang,n) in enumerate(langs):
        x=18+i%2*230;y=107+i//2*26;body+=f'<rect x="{x}" y="{y-12}" width="12" height="12" fill="{palette.get(lang,"#8598ac")}"/>'+text(x+20,y,f'{lang} {n}',16,'muted')
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
    out['contributions']=wrap(355,body,'Actual contribution calendar; chronological rows of 27 weeks')
    body=text(18,25,'¹ Downloads: four featured repos; not unique users.',12,'muted')+text(18,47,'Updated '+s['checked_at'][:19].replace('T',' ')+' UTC',12,'muted')
    out['footnote']=wrap(65,body,'Statistics scope and update time')
    return out

def picture(name,alt,url=None):
    p=f'<picture>\n  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{name}-mobile-dark.svg">\n  <source media="(max-width: 600px)" srcset="assets/{name}-mobile-light.svg">\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n  <img alt="{esc(alt)}" src="assets/{name}-light.svg" width="900">\n</picture>'
    return (f'<a href="{esc(url)}">\n{p}\n</a>' if url else p)

def outputs(s):
    out={}
    for dark in (False,True):
        for name,content in mobile_render(s,dark).items(): out[f'assets/{name}-mobile-{"dark" if dark else "light"}.svg']=content
        for name,content in render(s,dark).items(): out[f'assets/{name}-{"dark" if dark else "light"}.svg']=content
    parts=[picture('header','Many begin well; few see it through.'),picture('stats','Public repository statistics'),picture('projects-title','Projects')]
    parts += [picture('project-'+p['name'],p['name']+' — '+p['description'],f'https://github.com/{OWNER}/{p["name"]}') for p in s['projects']]
    parts += [picture('languages','Repository count by primary language'),picture('contributions','GitHub contribution calendar',f'https://github.com/{OWNER}?tab=overview'),picture('footnote','Statistics scope and update time')]
    out['README.md']='\n\n'.join(parts)+'\n'
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
