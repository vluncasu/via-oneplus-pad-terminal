import bpy,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
exec(compile((R/'src/render.py').read_text().split("view('01_asamblat'")[0],'scene_setup','exec'))
for name,blackparts in [('01_STRUCTURA_ALBA',False),('02_DETALII_NEGRE',True)]:
 group=bpy.data.collections.new(name);s.collection.children.link(group)
 for c,ob in objs.items():
  if c.startswith('R'):continue
  if (c in ['P01','O01','O03'])!=blackparts:continue
  for collection in list(ob.users_collection):collection.objects.unlink(ob)
  group.objects.link(ob)
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=480
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_location=(0,0,166);area.spaces.active.region_3d.view_distance=540
   area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();area.spaces.active.clip_end=10000
for ob in bpy.data.objects:
 if ob.type in ['LIGHT','CAMERA'] or ob.name=='Studio':ob.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'preview/Terminal_OPD2203_R11_ASAMBLAT.blend'))
s.cycles.samples=12;s.render.resolution_x=1200;s.render.resolution_y=950;ground.hide_render=True
for c,ob in objs.items():ob.hide_render=c!='B01'
view('B01_canal_integrat',(280,-330,330),(0,0,10),330)
for c,ob in objs.items():ob.hide_render=c!='H01'
rot=Matrix.Rotation(math.radians(120),4,'X')
def wp(p):return rot@Vector(p)+Vector((-12,10,240))
view('H01_canal_integrat',wp((180,-220,380)),wp((12,0,12)),480)
print('R11 SAVED',flush=True)
