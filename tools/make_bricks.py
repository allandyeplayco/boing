"""Draws the brick wall tile for anchored platform bases: art/world/base-bricks.png.
Running bond (rows alternate so joints never line up), chunky soft stones in the concept's lavender.
4 px per game unit, repeats seamlessly both ways. Run: python3 tools/make_bricks.py"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import random, os
PX=4; SS=2; S=PX*SS
TW,ROWS,BH,G,RAD=176,6,26,2.6,4.5
TH=ROWS*BH
GROUT=(92,86,148); BASE=(140,132,196); HI=(166,158,220); LO=(112,105,172); LINE=(78,73,132)
rnd=random.Random(11)
im=Image.new('RGB',(TW*S,TH*S),GROUT); d=ImageDraw.Draw(im)
def rows_widths():
    out=[]
    for r in range(ROWS):
        ws=[];left=TW
        while left>0:
            w=rnd.choice([34,40,44,48,52,58]);w=min(w,left)
            if 0<left-w<26: w=left
            ws.append(w);left-=w
        out.append(ws)
    return out
def stone(x,y,w,h):
    j=rnd.randint(-8,8); c=tuple(max(0,min(255,v+j)) for v in BASE); hi=tuple(max(0,min(255,v+j)) for v in HI)
    for dx in (-TW,0,TW):
        for dy in (-TH,0,TH):
            X,Y,W_,H_,r=(x+dx)*S,(y+dy)*S,w*S,h*S,RAD*S
            d.rounded_rectangle([X,Y,X+W_,Y+H_],r,fill=LINE)
            d.rounded_rectangle([X+S,Y+S,X+W_-S,Y+H_-S],r-S,fill=LO)              # shadowed bottom/right
            d.rounded_rectangle([X+S,Y+S,X+W_-S*2.6,Y+H_-S*3],r-S,fill=c)         # face
            d.rounded_rectangle([X+S*2,Y+S*1.8,X+W_-S*5,Y+H_*0.42],r-S,fill=hi)   # lit top
            d.rounded_rectangle([X+S*2,Y+H_*0.30,X+W_-S*5,Y+H_*0.55],r-S,fill=c)  # soften the lit band
            for _ in range(rnd.randint(0,2)):                                       # chips
                cx,cy=X+rnd.uniform(0.2,0.8)*W_,Y+rnd.uniform(0.35,0.75)*H_;rr=S*rnd.uniform(0.8,1.6)
                d.ellipse([cx-rr,cy-rr*0.7,cx+rr,cy+rr*0.7],fill=LO)
W=rows_widths()
for r_,ws in enumerate(W):
    x=rnd.uniform(0,20)+(r_%2)*22
    for w in ws:
        stone(x+G/2,r_*BH+G/2,w-G,BH-G); x+=w
im=im.filter(ImageFilter.GaussianBlur(S*0.45))
# fine painterly grain
n=Image.effect_noise(im.size,18).convert('L').filter(ImageFilter.GaussianBlur(S*0.6))
im=ImageChops.overlay(im,Image.merge('RGB',[n,n,n]).point(lambda v:128+(v-128)//3))
im=im.resize((TW*PX,TH*PX),Image.LANCZOS)
out=os.path.join(os.path.dirname(__file__),'..','art/world/base-bricks.png'); im.save(out); print('wrote',out,im.size)
