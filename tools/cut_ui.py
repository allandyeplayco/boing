"""Cut the shiny star and coin out of the ChatGPT level-clear design (art/ui/src/level-clear-concept.png).
Writes art/ui/star.png, art/ui/star-empty.png, art/ui/coin.png. Run: python3 tools/cut_ui.py"""
import cv2, numpy as np, os
ROOT=os.path.join(os.path.dirname(__file__),'..'); im=cv2.imread(os.path.join(ROOT,'art/ui/src/level-clear-concept.png'))
def enclosed(x0,y0,x1,y1,vmax=110,keep_outline=True,pad=0):
    c=im[y0:y1,x0:x1]; v=cv2.cvtColor(c,cv2.COLOR_BGR2HSV)[...,2]
    dark=(v<vmax).astype(np.uint8)
    dark=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    free=(1-dark).astype(np.uint8); n,lab=cv2.connectedComponents(free)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    inside=np.isin(lab,[k for k in range(1,n) if k not in edge]).astype(np.uint8)
    # keep the biggest enclosed area (the star/coin body) and everything inside it
    n2,l2,st,_=cv2.connectedComponentsWithStats(inside);k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]);body=(l2==k).astype(np.uint8)
    body=cv2.morphologyEx(body,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    ff=body.copy();h,w=body.shape;cv2.floodFill(ff,np.zeros((h+2,w+2),np.uint8),(0,0),1);body=body|(1-ff)
    m=cv2.dilate(body,np.ones((3,3),np.uint8),iterations=pad if pad else 4) if keep_outline else body
    a=cv2.GaussianBlur(m.astype(np.float32),(3,3),0.8)
    out=np.dstack([c.astype(np.float32),a*255])
    if not keep_outline: pass
    ys,xs=np.nonzero(m);return out[ys.min()-2:ys.max()+3,xs.min()-2:xs.max()+3].clip(0,255).astype(np.uint8)
star=enclosed(345,480,600,725)
cv2.imwrite(os.path.join(ROOT,'art/ui/star.png'),star)
# empty star: same shape, cool grey-blue, keeps the shine
g=cv2.cvtColor(star[...,:3],cv2.COLOR_BGR2GRAY).astype(np.float32)
e=np.dstack([g*0.62+70,g*0.55+60,g*0.5+55]); dk=g<90; e[dk]=star[...,:3][dk]
cv2.imwrite(os.path.join(ROOT,'art/ui/star-empty.png'),np.dstack([e.clip(0,255),star[...,3]]).astype(np.uint8))
coin=enclosed(338,830,428,920,vmax=95,pad=2)
cv2.imwrite(os.path.join(ROOT,'art/ui/coin.png'),coin)
for n in ('star','star-empty','coin'):print(n,cv2.imread(os.path.join(ROOT,f'art/ui/{n}.png'),cv2.IMREAD_UNCHANGED).shape)
