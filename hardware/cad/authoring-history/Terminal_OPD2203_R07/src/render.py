import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.35;return m
white=mat('PETG un singur material',(.78,.77,.73));black=mat('Sticla tabletei',(.008,.012,.016));objs={}
for a in json.loads((R/'preview/manifest.json').read_text()):
 if a['kind']=='probe':continue
 bpy.ops.wm.stl_import(filepath=str(R/'preview'/(a['id']+'.stl')));o=bpy.context.object;o.name=a['id']+' '+a['name'];o.data.materials.append(black if a['id'] in ['R01','P01','O01','O03'] else white);objs[a['id']]=o
 if a['kind']=='reference' and a['id']!='R01':o.hide_render=True;o.hide_set(True)
bpy.ops.mesh.primitive_plane_add(size=2500,location=(0,0,-.05));ground=bpy.context.object;ground.name='Studio';ground.data.materials.append(mat('Fond',(.055,.07,.085)))
for name,pos,power,size in [('Key',(200,400,650),14000000,420),('Fill',(-400,100,300),9000000,400),('Rim',(100,-450,550),16000000,330)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,165))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.world.color=(.22,.22,.22)
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);bpy.context.collection.objects.link(cam);s.camera=cam;d.type='ORTHO'
def view(name,pos,target,scale):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;s.render.filepath=str(R/'preview'/(name+'.png'));bpy.ops.render.render(write_still=True)
view('01_asamblat',(470,650,420),(0,0,166),480)
view('02_spate',(-420,-650,390),(0,0,166),480)
view('03_porturi',(150,-450,145),(0,-105,22),240)
# Save assembled state only; future views can hide components but never shift them.
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=480
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_location=(0,0,166);a.spaces.active.region_3d.view_distance=540;a.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion();a.spaces.active.clip_end=10000
for o in bpy.data.objects:
 if o.type in ['LIGHT','CAMERA'] or o.name=='Studio':o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'preview/Terminal_OPD2203_R07_ASAMBLAT.blend'))
for code,o in objs.items():o.hide_render=code not in ['B07']
view('04_picior_monobloc',(-320,250,230),(0,-30,130),260)
for c,o in objs.items():o.hide_render=c!='B07'
bpy.ops.mesh.primitive_cube_add(size=1,location=(200,0,150));cutter=bpy.context.object;cutter.scale=(400,600,600);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cutter.hide_render=True;cutter.hide_set(True)
mod=objs['B07'].modifiers.new('Sectiune canal CAD','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
view('05_canal_sectiune',(440,100,240),(0,-30,135),260)
objs['B07'].modifiers.remove(mod)
ground.hide_render=True
dl=bpy.data.lights.new('Interior fill','AREA');dl.energy=4000000;dl.size=250
lo=bpy.data.objects.new('Interior fill',dl);bpy.context.collection.objects.link(lo);lo.location=(0,0,-130);lo.rotation_euler=(Vector((0,-30,55))-lo.location).to_track_quat('-Z','Y').to_euler()
view('06_nervuri_interioare',(300,350,-200),(0,-30,70),310)
