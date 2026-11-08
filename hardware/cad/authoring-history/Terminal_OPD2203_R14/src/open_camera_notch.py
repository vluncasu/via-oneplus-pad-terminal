exec(compile(__import__('pathlib').Path(__file__).with_name('check_service.py').read_text().split('report={}')[0],__file__,'exec'))
s=local('H05').cut(Part.makeBox(26,4,11,V(-13,92.3,-2))).removeSplitter()
assert s.isValid() and len(s.Solids)==1
w=s.copy();w.Placement=H.multiply(s.Placement);d.getObject('H05').Shape=w
s.exportStep(str(R/'step/H05.step'))
t=s.copy();t.rotate(V(),V(0,0,1),45);b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
for sh,p in [(t,R/'stl/H05.stl'),(w,R/'preview/H05.stl')]:
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid();m.write(str(p))
d.recompute();d.save();print('CAMERA NOTCH OPEN THROUGH',flush=True)
