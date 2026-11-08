exec(compile(__import__('pathlib').Path(__file__).with_name('check_service.py').read_text().split('report={}')[0],__file__,'exec'))
h=local('H01')
for sign in [-1,1]:
 p=[(sign*126.6,97.7,1.7),(sign*129.6,97.7,1.7),(sign*132.4,97.7,6.3),(sign*126.6,97.7,6.3)]
 wire=Part.makePolygon([V(*q) for q in p]+[V(*p[0])])
 h=h.cut(Part.Face(wire).extrude(V(0,16,0)))
h=h.removeSplitter();assert h.isValid() and len(h.Solids)==1
w=h.copy();w.Placement=H.multiply(h.Placement);d.getObject('H01').Shape=w
h.exportStep(str(R/'step/H01.step'))
t=h.copy();t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45);b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
for s,p in [(t,R/'stl/H01.stl'),(w,R/'preview/H01.stl')]:
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid();m.write(str(p))
d.recompute();d.save()
print('GUIDE CONTACT',h.common(local('H05')).Volume,flush=True)
