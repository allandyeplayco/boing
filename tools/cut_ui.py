"""Cut baked pieces for the level-clear popup out of Allan's ChatGPT design (art/ui/src/level-clear-concept-2.png).
Writes art/ui/: title.png ("Level clear!"), crown.png (top badge with ribbons), star.png, star-empty.png, coin.png,
Run: python3 tools/cut_ui.py"""
import cv2, numpy as np, os
ROOT=os.path.join(os.path.dirname(__file__),'..'); SRC=os.path.join(ROOT,'art/ui/src/level-clear-concept-2.png'); OUT=os.path.join(ROOT,'art/ui')
im=cv2.imread(SRC); HSV=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
def save(n,a): cv2.imwrite(os.path.join(OUT,n),a); print(n,a.shape[1],'x',a.shape[0])
def finish(x0,y0,x1,y1,m,fill=True,soft=0.8,minarea=40):
    m=m.astype(np.uint8)
    if fill:
        inv=(1-m).astype(np.uint8);n,lab=cv2.connectedComponents(inv)
        edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
        for k in range(1,n):
            if k not in edge: m[lab==k]=1
    n,lab,st,_=cv2.connectedComponentsWithStats(m);keep=[k for k in range(1,n) if st[k,cv2.CC_STAT_AREA]>minarea];m=np.isin(lab,keep).astype(np.float32)
    a=cv2.GaussianBlur(m,(3,3),soft); c=im[y0:y1,x0:x1].astype(np.float32)
    out=np.dstack([c,a*255]); ys,xs=np.nonzero(a>0.05)
    return out[max(0,ys.min()-1):ys.max()+2,max(0,xs.min()-1):xs.max()+2].clip(0,255).astype(np.uint8)
def region(x0,y0,x1,y1): h,s,v=[HSV[y0:y1,x0:x1,i] for i in range(3)]; return h,s,v
def enclosed(x0,y0,x1,y1,vmax=120,grow=4,every=False,nocream=False):
    h,s,v=region(x0,y0,x1,y1); dark=cv2.morphologyEx((v<vmax).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,lab=cv2.connectedComponents((1-dark).astype(np.uint8)); edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    inside=np.isin(lab,[k for k in range(1,n) if k not in edge]).astype(np.uint8)
    n2,l2,st,_=cv2.connectedComponentsWithStats(inside)
    body=(np.isin(l2,[k for k in range(1,n2) if st[k,cv2.CC_STAT_AREA]>400]) if every else (l2==1+np.argmax(st[1:,cv2.CC_STAT_AREA]))).astype(np.uint8)
    body=cv2.morphologyEx(body,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    m=cv2.dilate(body,np.ones((3,3),np.uint8),iterations=grow)
    if nocream: m=m&((v<215)|(s>110)).astype(np.uint8)
    return finish(x0,y0,x1,y1,m)
# crown with ribbons, over the blue game scene
X0,Y0,X1,Y1=180,150,752,281; h,s,v=region(X0,Y0,X1,Y1)
blue=(h>=85)&(h<=135); cloud=(s<70)&(v>150)
save('crown.png',finish(X0,Y0,X1,Y1,~(blue|cloud),minarea=2000))
# stars and coin
star=enclosed(352,500,592,738,vmax=185,grow=3); save('star.png',star)
g=cv2.cvtColor(star[...,:3],cv2.COLOR_BGR2GRAY).astype(np.float32)
e=np.dstack([g*0.55+95,g*0.5+80,g*0.5+92]); dk=g<100; e[dk]=star[...,:3][dk]
save('star-empty.png',np.dstack([e.clip(0,255),star[...,3]]).astype(np.uint8))
save('coin.png',enclosed(338,852,428,942,vmax=185,grow=2))
# "Level clear!": yellow letters and plum outline on cream
X0,Y0,X1,Y1=105,362,845,512; h,s,v=region(X0,Y0,X1,Y1)
save('title.png',enclosed(X0,Y0,X1,Y1,vmax=170,grow=14,every=True,nocream=True))
