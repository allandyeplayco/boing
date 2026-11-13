"""Cut game pieces out of a painted concept (art/world/src/concept-1.png) into art/world/*.png.
Run: python3 tools/cut_world.py   (needs opencv-python-headless, numpy, pillow)
The concept is about 0.6 game units per pixel (Boing is ~90 px wide there, 54 units in game)."""
import cv2, numpy as np, os, sys
ROOT=os.path.join(os.path.dirname(__file__),'..'); SRC=os.path.join(ROOT,'art/world/src/concept-1.png'); OUT=os.path.join(ROOT,'art/world')
im=cv2.imread(SRC)
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); Hh,S,V=[hsv[...,i].astype(int) for i in range(3)]
def cap_mask(x0,y0,x1,y1):
    h,s,v=Hh[y0:y1,x0:x1],S[y0:y1,x0:x1],V[y0:y1,x0:x1]
    m=((((h<=32)|(h>=170))&(s>80))|(v<100)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(lab==k).astype(np.uint8)
    # fill holes
    inv=(1-m).astype(np.uint8);n2,lab2=cv2.connectedComponents(inv)
    edge=set(np.unique(np.concatenate([lab2[0],lab2[-1],lab2[:,0],lab2[:,-1]])))
    for k2 in range(1,n2):
        if k2 not in edge: m[lab2==k2]=1
    a=cv2.GaussianBlur(m.astype(np.float32),(3,3),0.7)
    return a
def rgba(x0,y0,x1,y1,a):
    c=im[y0:y1,x0:x1].astype(np.float32); return np.dstack([c,a*255]).clip(0,255).astype(np.uint8)
def save(n,img): cv2.imwrite(os.path.join(OUT,n),img); print('wrote',n,img.shape[1],'x',img.shape[0])
def dips(a):
    # x of the high points between scallops (the cap's bottom edge rises there)
    bot=np.array([ (np.nonzero(a[:,x]>0.5)[0].max() if (a[:,x]>0.5).any() else 0) for x in range(a.shape[1])])
    sm=np.convolve(bot,np.ones(5)/5,'same'); d=[x for x in range(6,len(sm)-6) if sm[x]==sm[x-6:x+7].min() and sm[x]<np.median(sm)-4]
    out=[];[out.append(x) for x in d if not out or x-out[-1]>20];return out,bot
if __name__=='__main__':
    # long bottom platform cap
    Y0,Y1=1612,1676; a=cap_mask(0,Y0,852,Y1); d,_=dips(a); print('dips',d)
    P=np.diff(d); print('periods',P)
    lx=int(np.nonzero(a.max(0)>0.5)[0].min())-1;d=[x for x in d if x>lx+30]
    save('cap-left.png',rgba(lx,Y0,d[0],Y1,a[:,lx:d[0]]))
    # middle: 4 scallops, ends crossfaded so it repeats with no seam
    i=0;xa,xb=d[i],d[i+4];ov=12
    t=rgba(xa,Y0,xb+ov,Y1,a[:,xa:xb+ov]).astype(np.float32)
    w=xb-xa;head=t[:,:ov].copy();tail=t[:,w:w+ov]
    f=np.linspace(0,1,ov)[None,:,None];t[:,:ov]=tail*(1-f)+head*f
    save('cap-mid.png',t[:,:w].astype(np.uint8))
    # right end: the left end mirrored, so both ends match
    save('cap-right.png',cv2.flip(cv2.imread(os.path.join(OUT,'cap-left.png'),cv2.IMREAD_UNCHANGED),1))
    print('cap top row (walk line) at',int(np.nonzero(a.max(1)>0.5)[0].min()),'of',Y1-Y0)
    # floating platform: thinner cap on a wooden plank with pegs underneath (right platform in the concept)
    FY0,FY1=909,975; f=cap_mask(499,FY0,852,FY1)
    bot=np.array([(np.nonzero(f[:,x]>0.5)[0].max() if (f[:,x]>0.5).any() else 0) for x in range(f.shape[1])])
    pegx=np.nonzero(bot>=np.percentile(bot,90)-1)[0]; runs=np.split(pegx,np.nonzero(np.diff(pegx)>3)[0]+1)
    pegs=[int(r.mean()) for r in runs if len(r)>8]; print('pegs',pegs)
    fl=max(0,int(np.nonzero(f.max(0)>0.5)[0].min())-1); c1=(pegs[0]+pegs[1])//2; c2=(pegs[1]+pegs[2])//2
    save('float-left.png',rgba(499+fl,FY0,499+c1,FY1,f[:,fl:c1]))
    ov=10;t=rgba(499+c1,FY0,499+c2+ov,FY1,f[:,c1:c2+ov]).astype(np.float32);w=c2-c1
    head=t[:,:ov].copy();tail=t[:,w:w+ov];g=np.linspace(0,1,ov)[None,:,None];t[:,:ov]=tail*(1-g)+head*g
    save('float-mid.png',t[:,:w].astype(np.uint8))
    save('float-right.png',cv2.flip(cv2.imread(os.path.join(OUT,'float-left.png'),cv2.IMREAD_UNCHANGED),1))
    print('float walk line at',int(np.nonzero(f.max(1)>0.5)[0].min()))
    # stone base: a clean patch of the tower, made to repeat both ways
    SX,SY,SW=466,1675,84; ov=12
    p=im[SY:SY+SW+ov,SX:SX+SW+ov].astype(np.float32); p=(p-p.mean((0,1)))*1.12+p.mean((0,1))*0.98 # a little less foggy
    g=np.linspace(0,1,ov)
    p[:,:ov]=p[:,SW:SW+ov]*(1-g)[None,:,None]+p[:,:ov]*g[None,:,None]; p=p[:,:SW]
    p[:ov]=p[SW:SW+ov]*(1-g)[:,None,None]+p[:ov]*g[:,None,None]; p=p[:SW]
    save('base-mid.png',p.astype(np.uint8))
    # decorations for bases: the banner and a vine
    def decal(x0,y0,x1,y1,keep):
        c=im[y0:y1,x0:x1];hh,ss,vv=[cv2.cvtColor(c,cv2.COLOR_BGR2HSV)[...,i].astype(int) for i in range(3)]
        m=keep(hh,ss,vv).astype(np.uint8);m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        dk=((vv<95)&(cv2.dilate(m,np.ones((5,5),np.uint8))>0));m=(m|dk).astype(np.uint8)
        n,lab,st,_=cv2.connectedComponentsWithStats(m);keepk=[k for k in range(1,n) if st[k,cv2.CC_STAT_AREA]>60];m=np.isin(lab,keepk).astype(np.float32)
        return np.dstack([c.astype(np.float32),cv2.GaussianBlur(m,(3,3),0.7)*255]).clip(0,255).astype(np.uint8)
    save('deco-banner.png',decal(188,1035,378,1255,lambda h,s,v:(((h<=32)|(h>=165))&(s>70))))
    save('deco-vine.png',decal(292,1212,482,1475,lambda h,s,v:((h>=30)&(h<=90)&(s>60))))
    # background: the sky, far castles and islands above the platforms; mirrored copies make it loop sideways
    bg=im[0:828].copy(); save('bg-far.png',np.hstack([bg,cv2.flip(bg,1)]))
    # clouds from the top of the sky
    def cloud(x0,y0,x1,y1):
        c=im[y0:y1,x0:x1];hh,ss,vv=[cv2.cvtColor(c,cv2.COLOR_BGR2HSV)[...,i].astype(int) for i in range(3)]
        a=np.clip((ss.astype(np.float32)*-1+95)/40,0,1)*(vv>200)
        n,lab,st,_=cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8));k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]);a=a*cv2.dilate((lab==k).astype(np.uint8),np.ones((5,5),np.uint8))
        return np.dstack([c.astype(np.float32),a*255]).clip(0,255).astype(np.uint8)
    save('cloud-1.png',cloud(450,215,725,335)); save('cloud-2.png',cloud(0,285,172,385)); save('cloud-3.png',cloud(295,490,488,575))
