exec(compile(__import__('pathlib').Path(__file__).with_name('check_service.py').read_text().split('report={}')[0],__file__,'exec'))
def prism(p,v):return Part.Face(Part.makePolygon([V(*q) for q in p]+[V(*p[0])])).extrude(V(*v))
c=local('O01')
c=c.cut(prism([(128,-11,14),(128,11,14),(128,0,25)],(7,0,0))).removeSplitter()
f=local('O06')
restore=Part.makeBox(5,22,3,V(129.3,-11,-.2))
outline=Part.makeBox(26,194,3,V(131,-97,-.2))
outline=outline.makeFillet(12.8,[e for e in outline.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>2.99])
f=f.fuse(restore.common(outline))
f=f.cut(prism([(128,-11,-.21),(131.29,-11,-.21),(134.3,-11,2.8),(128,-11,2.8)],(0,22,0))).removeSplitter()
for code,s in [('O01',c),('O06',f)]:
 if not s.isValid():s.fix(.01,.001,.1)
 assert s.isValid() and len(s.Solids)==1
 w=s.copy();w.Placement=H.multiply(s.Placement);d.getObject(code).Shape=w
 s.exportStep(str(R/'step'/(code+'.step')))
 t=s.copy()
 if code=='O06':t.rotate(V(),V(1,0,0),180)
 b=t.BoundBox;t.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 for sh,p in [(t,R/'stl'/(code+'.stl')),(w,R/'preview'/(code+'.stl'))]:
  m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.045,AngularDeflection=.12,Relative=False);clean(m);assert m.isSolid();m.write(str(p))
 print('45 DEGREE TRANSITION',code,flush=True)
d.recompute();d.save()
