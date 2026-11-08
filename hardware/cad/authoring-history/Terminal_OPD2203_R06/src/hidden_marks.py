"""Tiny recessed 3x5 block-font IDs on specified hidden mounting faces, mm."""
import FreeCAD as A, Part
V=A.Vector
FONT={
'0':['111','101','101','101','111'],'1':['010','110','010','010','111'],
'2':['111','001','111','100','111'],'3':['111','001','111','001','111'],
'4':['101','101','111','001','001'],'5':['111','100','111','001','111'],
'6':['111','100','111','101','111'],'7':['111','001','010','010','010'],
'8':['111','101','111','101','111'],'9':['111','101','111','001','111'],
'H':['101','101','111','101','101'],'O':['111','101','101','101','111'],
'B':['110','101','110','101','110'],'P':['110','101','110','100','100'],
'S':['111','100','111','001','111'],'T':['111','010','010','010','010'],
'Q':['111','101','101','111','001']}
def mark(shape,code,axis):
    n=V(*axis);u=V(1,0,0) if abs(n.x)<.9 else V(0,1,0);v=n.cross(u)
    pitch=.48; pixel=.40; depth=.28
    w=(len(code)*4-1)*pitch;h=5*pitch
    fs=[]
    for f in shape.Faces:
        if not isinstance(f.Surface,Part.Plane):continue
        nn=f.normalAt(0,0)
        if nn.dot(n)>.98 and f.Area>w*h:fs.append(f)
    for f in sorted(fs,key=lambda q:q.Area,reverse=True):
        pts=[q.Point for q in f.Vertexes];us=[q.dot(u) for q in pts];vs=[q.dot(v) for q in pts]
        if max(us)-min(us)<w+.4 or max(vs)-min(vs)<h+.4:continue
        d=f.CenterOfMass.dot(n)
        for fx,fy in [(.5,.5),(.25,.5),(.75,.5),(.5,.25),(.5,.75),(.25,.25),(.75,.75)]:
            xx=min(us)+(max(us)-min(us))*fx;yy=min(vs)+(max(vs)-min(vs))*fy
            origin=u*(xx-w/2)+v*(yy-h/2)+n*(d+.01);tools=[]
            for k,ch in enumerate(code):
                for row,line in enumerate(FONT.get(ch,FONT['0'])):
                    for col,on in enumerate(line):
                        if on!='1':continue
                        p=origin+u*(w-(k*4+col)*pitch-pixel)+v*((4-row)*pitch) # pre-reflect text; whole part is reflected later
                        wire=Part.makePolygon([p,p+u*pixel,p+u*pixel+v*pixel,p+v*pixel,p])
                        tools.append(Part.Face(wire).extrude(n*(-depth-.01)))
            tool=Part.makeCompound(tools)
            vol=shape.common(tool).Volume
            if vol<sum(t.Volume for t in tools)*.93:continue
            out=shape.cut(tool).removeSplitter()
            if out.isValid() and len(out.Solids)==len(shape.Solids):
                return out,{'code':code,'normal':axis,'centre':[xx,yy,d],'depth_mm':depth,'character_height_mm':h,'removed_mm3':vol}
    return shape,None
