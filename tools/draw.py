# Draws levels + bot route to PNGs: python3 tools/draw.py results.json outdir
import json,sys,os
from PIL import Image,ImageDraw
res=json.load(open(sys.argv[1]));out=sys.argv[2];os.makedirs(out,exist_ok=True)
COL={'plat':(60,70,90),'brk':(240,140,40),'brk2':(170,80,20),'spring':(60,180,90),'spike':(220,40,60)}
for i,r in enumerate(res):
    L=r['level'];xs=[];ys=[]
    for o in L['objs']:
        xs+= [o['x'],o['x']+o.get('w',0)];ys+=[o['y']]
    for x,y in r['trace']['pts']: xs.append(x);ys.append(y)
    x0,x1,y0,y1=min(xs)-80,max(xs)+80,min(ys)-120,max(ys)+80
    S=0.5;W=int((x1-x0)*S);H=int((y1-y0)*S)
    im=Image.new('RGB',(W,H),(235,240,250));d=ImageDraw.Draw(im)
    T=lambda x,y:((x-x0)*S,(y-y0)*S)
    for gy in range(int(y0//100)*100,int(y1)+1,100): d.line([T(x0,gy),T(x1,gy)],fill=(220,225,235))
    for o in L['objs']:
        t=o['type']
        if t=='coin': x,y=T(o['x'],o['y']);d.ellipse([x-5,y-5,x+5,y+5],fill=(240,200,40))
        elif t=='goal': x,y=T(o['x'],o['y']);d.rectangle([x-4,y-22,x+12,y+18],fill=(40,160,60))
        else:
            a=T(o['x'],o['y']-(20 if t=='spring' else 0));b=T(o['x']+o['w'],o['y']+18)
            d.rectangle([a,b],fill=COL[t])
    pts=[T(x,y) for x,y in r['trace']['pts']]
    if len(pts)>1:d.line(pts,fill=(60,110,245),width=2)
    for x,y in r['trace']['taps']:
        a,b=T(x,y);d.ellipse([a-6,b-6,a+6,b+6],outline=(230,0,120),width=3)
    sx,sy=T(L['spawn']['x'],L['spawn']['y']);d.ellipse([sx-9,sy-9,sx+9,sy+9],outline=(0,0,0),width=2)
    d.text((6,6),f"{i+1} {L.get('name')} {'WIN' if r['ok'] else 'FAIL'} taps {r['taps']} tight {r['tight']} score {r['score']} short {r['short']}",fill=(0,0,0))
    im.save(f"{out}/{i+1:02d}.png")
