import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
# Reuse scene setup only; never import old inspection states or old .blend geometry.
source=(R/'src/render.py').read_text()
exec(compile(source.split("view('01_asamblat'")[0],str(R/'src/render.py'),'exec'))
for label,ids in [('01_ALB',[c for c in objs if c not in ['P01','O01','O03','R01','R02','R03','R04','R05'] and not c.startswith('L')]),('02_NEGRU',[c for c in objs if c in ['P01','O01','O03'] or c.startswith('L')]),('03_REFERINTE',[c for c in objs if c.startswith('R')])]:
 collection=bpy.data.collections.new(label);s.collection.children.link(collection)
 for c in ids:
  ob=objs[c]
  for old in list(ob.users_collection):old.objects.unlink(ob)
  collection.objects.link(ob)
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=480
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=(0,0,166);area.spaces.active.region_3d.view_distance=540
   area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();area.spaces.active.clip_end=10000
for ob in bpy.data.objects:
 if ob.type in ['LIGHT','CAMERA'] or ob.name=='Studio':ob.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'preview/Terminal_OPD2203_R10_ASAMBLAT.blend'))
s.cycles.samples=12;s.render.resolution_x=1100;s.render.resolution_y=900
ground.hide_render=True
for c,ob in objs.items():ob.hide_render=c!='H01'
rot=Matrix.Rotation(math.radians(120),4,'X')
def wp(p):return rot@Vector(p)+Vector((-12,10,240))
view('R10_prindere_filetata',wp((-125,-140,105)),wp((-96,-92,19)),72)
objs['H01'].hide_render=True
bpy.ops.wm.stl_import(filepath=str(R.parent/'Terminal_OPD2203_R09/preview/H01.stl'))
old=bpy.context.object;old.data.materials.append(white)
view('R09_prindere_filetata',wp((-125,-140,105)),wp((-96,-92,19)),72)
print('SAVED R10 ASSEMBLY AND COMPARISON',flush=True)
