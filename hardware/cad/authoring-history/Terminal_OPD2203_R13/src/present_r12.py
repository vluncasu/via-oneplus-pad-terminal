import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
exec(compile((R/'src/render.py').read_text().split("view('01_asamblat'")[0],'setup','exec'))
white.name='PETG alb';black.name='PETG negru';black.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.5
for c in ['O04','V71','V72','V73','V74']:objs[c].data.materials.clear();objs[c].data.materials.append(black)
film=mat('PETG natural subtire - aspect orientativ',(.65,.75,.8));p=film.node_tree.nodes['Principled BSDF'];p.inputs['Transmission Weight'].default_value=.5;p.inputs['Roughness'].default_value=.25
objs['O05'].data.materials.clear();objs['O05'].data.materials.append(film)
for name,ids in [('01_STRUCTURA',[c for c in objs if not c.startswith('R') and c not in ['O01','O03','O04','O05','P01','V71','V72','V73','V74']]),('02_OPTICA_SI_PORTURI',['O01','O03','O04','P01','V71','V72','V73','V74']),('03_FOITA',['O05']),('04_REFERINTE',[c for c in objs if c.startswith('R')])]:
 col=bpy.data.collections.new(name);s.collection.children.link(col)
 for c in ids:
  ob=objs[c]
  for old in list(ob.users_collection):old.objects.unlink(ob)
  col.objects.link(ob)
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=580;d.clip_end=10000
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_location=(0,0,166);a.spaces.active.region_3d.view_distance=550;a.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();a.spaces.active.clip_end=10000
for ob in bpy.data.objects:
 if ob.type in ['CAMERA','LIGHT'] or ob.name=='Studio':ob.hide_set(True)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(R/'preview/Terminal_OPD2203_R12_ASAMBLAT.blend'))
# Simple technical views on warm background. Geometry remains in assembly coordinates.
s.render.film_transparent=True;s.use_nodes=True;nodes=s.node_tree.nodes;nodes.clear()
l=nodes.new('CompositorNodeRLayers');over=nodes.new('CompositorNodeAlphaOver');out=nodes.new('CompositorNodeComposite');over.inputs[1].default_value=(.48,.35,.25,1)
s.node_tree.links.new(l.outputs['Image'],over.inputs[2]);s.node_tree.links.new(over.outputs[0],out.inputs[0])
ground.hide_render=True;s.cycles.samples=12;s.render.resolution_x=1400;s.render.resolution_y=1000
rot=Matrix.Rotation(math.radians(120),4,'X')
def wp(p):return rot@Vector(p)+Vector((-12,10,240))
for c,ob in objs.items():ob.hide_render=c not in ['H05']
view('R12_traversa_cleme',wp((80,220,170)),wp((0,99,5)),330)
for c,ob in objs.items():ob.hide_render=c!='O01'
view('R12_caseta_cleme',wp((320,-100,230)),wp((144,0,15)),250)
print('SAVED R12',flush=True)
