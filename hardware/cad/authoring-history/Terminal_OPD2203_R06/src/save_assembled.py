import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'preview/Terminal_OPD2203_R06.blend'))
ids={a['id'] for a in json.loads((r/'preview/manifest.json').read_text())}
for o in bpy.data.objects:
 code=o.name.split(' ')[0]
 if code in ids:
  o.location=(0,0,0)
  o.hide_render=code in {'R02','R03','R05','R06','R07','R08'}
  o.hide_set(o.hide_render)
 elif o.type in {'LIGHT','CAMERA'} or o.name.lower() in {'plane','ground'}:
  o.hide_set(True)
cam=bpy.context.scene.camera
cam.location=(470,650,420)
cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=480
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_location=(0,0,166)
   a.spaces.active.region_3d.view_distance=540
   a.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
   a.spaces.active.clip_end=10000
bpy.ops.object.select_all(action='DESELECT')
assert all(o.location.length<.001 for o in bpy.data.objects if o.name.split(' ')[0] in ids)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'preview/Terminal_OPD2203_R06_ASAMBLAT.blend'))
