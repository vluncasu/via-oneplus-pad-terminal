exec(compile(__import__('pathlib').Path(__file__).with_name('service_r12.py').read_text().split("d=A.openDocument")[0],__file__,'exec'))
d=A.openDocument(str(R/'cad/Terminal_OPD2203_R12.FCStd'))
s=d.getObject('H01').Shape.copy();s.Placement=H.inverse().multiply(s.Placement)
s=s.cut(Part.makeBox(259.5,40,6.9,V(-129.75,78,0))).removeSplitter()
for x in [-65,65]:s=s.cut(Part.makeBox(1.8,23.2,3.5,V(x-.9,86.3,7.2)))
for x,sign in [(131,-1),(157,1)]:
 for cy in [-50,50]:s=s.cut(Part.makeBox(2.6,3.4,5.9,V(x-sign*.7-1.3,cy+10.3,5.8)))
assert s.isValid() and len(s.Solids)==1
w=s.copy();w.Placement=H.multiply(s.Placement);d.getObject('H01').Shape=w
s.exportStep(str(R/'step/H01.step'))
t=s.copy();t.rotate(V(),V(1,0,0),90);t.rotate(V(),V(0,0,1),-45);b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
for shape,path in [(t,R/'stl/H01.stl'),(w,R/'preview/H01.stl')]:
 m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid();m.write(str(path))
d.recompute();d.save();print('UPPER CORNER PATH CLEARED',flush=True)
contacts=[]
for c in ['O01','H05']:
 v=w.common(d.getObject(c).Shape).Volume;contacts.append({'a':'H01','b':c,'mm3':v});assert v<.05,(c,v)
(R/'validation/final_clearances.json').write_text(json.dumps(contacts,indent=2));print('FINAL CLEARANCES',contacts,flush=True)
