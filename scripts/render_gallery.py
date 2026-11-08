import bpy,json,math,os
from pathlib import Path
from mathutils import Vector,Matrix
r=Path(__file__).resolve().parents[1];labels=json.loads((r/'hardware/cad/english-part-labels.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(r/'media/terminal-opd2203-r14-baseline.blend'))
s=bpy.context.scene;objs={}
for old in list(bpy.data.objects):
 code=old.name.split(' ')[0]
 if code in labels and old.type=='MESH':
  mats=list(old.data.materials);bpy.data.objects.remove(old,do_unlink=True)
  bpy.ops.wm.stl_import(filepath=str(r/'hardware/cad/assembly-meshes'/f'{code}.stl'))
  obj=bpy.context.object;obj.name=code+' '+labels[code].replace('_',' ')
  for m in mats:obj.data.materials.append(m)
  objs[code]=obj
# Translate all collection/material labels in the delivered inspection file.
for collection in bpy.data.collections:
 collection.name={'01_STRUCTURA':'01_STRUCTURE','02_OPTICA_SI_PORTURI':'02_OPTICS_AND_PORTS','03_FOITA':'03_OPTICAL_FILM','04_REFERINTE':'04_REFERENCE_ENVELOPES'}.get(collection.name,collection.name)
for mat in bpy.data.materials:
 mat.name={'PETG alb':'White satin PETG','PETG negru':'Black PETG','Sticla tabletei':'Tablet glass','Fond':'Backdrop','PETG natural subtire - aspect orientativ':'Natural PETG film - illustrative transmission'}.get(mat.name,mat.name)

def material(name,color,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
white=material('White satin PETG',(.76,.77,.73),.32);black=material('Near-black navy PETG',(.008,.018,.028),.28);glass=material('Original tablet glass',(.004,.009,.014),.14);light=material('Intended LED transmission zone - illustrative',(.95,.7,.38),.4,2)
H=Matrix.Translation(Vector((-12,10,240))) @ Matrix.Rotation(math.radians(120),4,'X');inv=H.inverted()
for code,o in objs.items():
 o.data.materials.clear();o.data.materials.append(glass if code=='R01' else black if code in ['P01','O01','O03','O06'] else white)
 o.hide_set(False);o.hide_render=code.startswith('R') and code!='R01'
 if code=='O05':
  # Assembly amendment may be exported separately; keep this visual at exactly 0.20 mm.
  local=[inv @ v.co for v in o.data.vertices];zlo=min(v.z for v in local);zhi=max(v.z for v in local)
  if zhi-zlo>.3:
   for vertex,p in zip(o.data.vertices,local):p.z=zlo+(p.z-zlo)*.5;vertex.co=H@p
  o.data.materials.clear();film=material('Natural PETG film - illustrative transparency',(.7,.75,.78),.12);film.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.95;film.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.45;o.data.materials.append(film)
 if code in ['H01','B01']:
  o.data.materials.append(light)
  for face in o.data.polygons:
   point=inv@face.center if code=='H01' else face.center
   if (12.001<point.z<14.999 if code=='H01' else 4.001<point.z<6.999):face.material_index=1
# Deep plum studio with restrained procedural texture; no default gray environment.
ground=bpy.data.objects.get('Studio');ground.hide_set(False);ground.hide_render=False;ground.data.materials.clear();bg=material('Deep plum architectural studio',(.045,.033,.055),.75);ground.data.materials.append(bg)
p=bg.node_tree.nodes.get('Principled BSDF');noise=bg.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.3;bump=bg.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.04;bg.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);bg.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
s.use_nodes=False;s.render.film_transparent=False;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=4
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.06,.045,.075,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
cam=s.camera;cam.hide_set(False);cam.data.type='ORTHO';cam.data.clip_end=10000
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.hide_set(False);ob.hide_render=False
s.view_settings.view_transform='AgX'
base={c:o.hide_render for c,o in objs.items()}
def isolate(ids):
 for c,o in objs.items():o.hide_render=c not in ids
 ground.hide_render=True

def view(name,pos,target,scale):
 selected=os.environ.get('VIA_RENDER_ONLY','')
 if selected and name[:2] not in selected.split(','):return
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 points=[o.matrix_world@Vector(v)-Vector(target) for o in objs.values() if not o.hide_render for v in o.bound_box]
 if points:
  right=cam.rotation_euler.to_quaternion()@Vector((1,0,0));up=cam.rotation_euler.to_quaternion()@Vector((0,1,0))
  required=max(2*max(abs(p.dot(right)) for p in points),2*max(abs(p.dot(up)) for p in points)*s.render.resolution_x/s.render.resolution_y)*1.10
  cam.data.ortho_scale=max(scale,required)
 s.render.filepath=str(r/'media/renders'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)

def center(code):
 o=objs[code];return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8

# Save a normal assembled inspection scene before any isolated/detail views.
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=520
for c,o in objs.items():o.hide_set(c.startswith('R') and c!='R01')
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(r/'media/via-oneplus-pad-r14-1-assembled.blend'))
view('01-oneplus-pad-terminal-front',(470,650,420),(0,0,165),520)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'media/via-oneplus-pad-r14-1-assembled.blend'))
view('02-oneplus-pad-terminal-rear',(-420,-650,390),(0,0,165),520)
view('03-continuous-s-stand-side',(620,0,285),(0,0,165),470)
isolate(['B01','P01']);view('04-recessed-dummy-usb-ethernet-ports',(160,-460,170),(0,-100,24),255)
isolate(['O01','O03','O05','O06']);target=center('O01');view('05-optical-cassette-assembly',target+Vector((160,270,120)),target,250)
isolate(['H05','H06']);target=center('H06');view('06-top-service-locking-bar',target+Vector((200,-280,180)),target,330)
isolate(['H01','R05']);objs['R05'].data.materials.clear();objs['R05'].data.materials.append(material('LED clearance envelope - not a physical strip',(.8,.18,.025),.4));view('07-integrated-head-led-channel',(260,-430,90),(0,0,230),375)
isolate(['B01','R04']);objs['R04'].data.materials.clear();objs['R04'].data.materials.append(objs['R05'].data.materials[0]);view('08-integrated-base-led-channel',(280,-350,330),(0,0,10),315)
isolate(['B07']);ground.hide_render=True
bpy.ops.object.light_add(type='AREA',location=(140,160,-160));underfill=bpy.context.object;underfill.name='Underside inspection fill';underfill.data.energy=180000;underfill.data.shape='DISK';underfill.data.size=250;underfill.rotation_euler=(Vector((0,0,40))-underfill.location).to_track_quat('-Z','Y').to_euler()
view('09-stand-root-reinforcement',(300,350,-200),(0,-30,70),315)
bpy.data.objects.remove(underfill,do_unlink=True)
isolate(['B07']);bpy.ops.mesh.primitive_cube_add(size=1,location=(200,0,150));cutter=bpy.context.object;cutter.scale=(400,600,600);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cutter.hide_render=True;cut=objs['B07'].modifiers.new('Cable duct inspection section','BOOLEAN');cut.operation='DIFFERENCE';cut.object=cutter
view('10-internal-cable-duct-section',(440,100,240),(0,-30,135),270)
objs['B07'].modifiers.remove(cut)
isolate(['O06']);target=center('O06');view('11-flat-print-dummy-sensor-face',target+Vector((130,270,100)),target,230)
isolate(['V21']);target=center('V21');view('12-printed-head-mount-screw',target+Vector((45,55,40)),target,40)
isolate(['V31']);target=center('V31');view('13-printed-spherical-screw-foot',target+Vector((40,-50,-30)),target,42)
print('ALL_RENDERS_COMPLETE',flush=True)
