import sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
V=A.Vector
helix=Part.makeHelix(2,8,5.25)
wire=Part.Wire(helix.Edges)
pts=[V(5.0,0,-.65),V(6,0,-.12),V(6,0,.12),V(5.0,0,.65)]
profile=Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)
th=wire.makePipeShell([profile],True,True)
s=Part.makeCylinder(5.25,8).fuse(th).common(Part.makeCylinder(6.1,8))
print(s.isValid(),len(s.Solids),s.Volume)
