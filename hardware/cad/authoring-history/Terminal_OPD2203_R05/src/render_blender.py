"""Render actual exported CAD meshes; no generative reconstruction of design."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
manifest=json.loads((ROOT/'preview/manifest.json').read_text())
def mat(name,color,metal=0,rough=.35):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if name=='BLACK':
        bs.inputs['Base Color'].default_value=(.002,.006,.012,1)
        bs.inputs['Roughness'].default_value=.48
        bs.inputs['Specular IOR Level'].default_value=.13
    if name=='DIFF':
        bs.inputs['Emission Color'].default_value=(1,.54,.19,1); bs.inputs['Emission Strength'].default_value=2
    if name=='PMMA':
        bs.inputs['Base Color'].default_value=(.94,.97,1,1)
        bs.inputs['Transmission Weight'].default_value=.92; bs.inputs['IOR'].default_value=1.49
        bs.inputs['Roughness'].default_value=.04
        # Thin clear cover, approximate transmissive appearance for product preview.
        trans=m.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        mix=m.node_tree.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.10
        m.node_tree.links.new(trans.outputs[0],mix.inputs[1]); m.node_tree.links.new(bs.outputs[0],mix.inputs[2])
        m.node_tree.links.new(mix.outputs[0],m.node_tree.nodes.get('Material Output').inputs['Surface'])
    return m
mats={i['material']:mat(i['material'],i['color'],.1 if i['material']=='REF' else 0,.19 if i['material']=='BLACK' else .35) for i in manifest}
objects={}
for it in manifest:
    bpy.ops.wm.stl_import(filepath=str(ROOT/'preview'/(it['id']+'.stl')))
    ob=bpy.context.object; ob.name=it['id']+' '+it['name']; ob.data.materials.append(mats[it['material']])
    # CAD edges retain their real dimensions; render-only tiny edge highlight.
    if it['material'] not in ('DIFF','PMMA','PCB'):
        mod=ob.modifiers.new('Photographic edge highlight 0.18mm','BEVEL'); mod.width=.18; mod.segments=2
        mod=ob.modifiers.new('Normals','WEIGHTED_NORMAL')
    objects[it['id']]=ob
    if it['id'].startswith('S3'):
        ob.data.materials.clear();ob.data.materials.append(mat('TPU alb',(.84,.82,.77),0,.5))
    if it['id']=='R04':
        ob.data.materials.append(mat('Camera lens',(.002,.004,.008),.15,.18))
        for poly in ob.data.polygons:
            zh=-(poly.center.y-10)*.8660254-(poly.center.z-240)*.5
            if zh<13.9: poly.material_index=1
    if it['id']=='R01':
        ob.data.materials.clear(); ob.data.materials.append(mat('Tablet front glass',(.002,.004,.006),.05,.19))
    if it['id'] in ('R02','R03','R05','R06','R07','R08'): ob.hide_render=True
# Display appearance on tablet's existing front, simple black UI (not an added sheet).
angle=math.radians(120)
def head_point(x,y,z): return (12-x,10+y*math.cos(angle)-z*math.sin(angle),240+y*math.sin(angle)+z*math.cos(angle))
glassmat=mat('screen',(0.003,.006,.009),.05,.21)
verts=[head_point(x,y,-.035) for x,y in [(-119,-85),(119,-85),(119,85),(-119,85)]]
mesh=bpy.data.meshes.new('Active area illustration'); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update()
ob=bpy.data.objects.new('Illustrative display / active area unmeasured',mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(glassmat)
# Ground and studio.
bpy.ops.mesh.primitive_plane_add(size=3000,location=(0,0,-.05)); ground=bpy.context.object; ground.name='Studio floor'; ground.data.materials.append(mat('Ground',(.065,.082,.094),0,.7))
def light(name,xyz,power,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=xyz
    ob.rotation_euler=(Vector((0,0,170))-ob.location).to_track_quat('-Z','Y').to_euler()
light('Key',(200,350,650),14000000,420)
light('Fill',(-450,100,350),9000000,400)
light('Rim',(50,-380,520),19000000,330)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.world.color=(.22,.22,.22); scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'
camdata=bpy.data.cameras.new('Camera'); camera=bpy.data.objects.new('Camera',camdata); bpy.context.collection.objects.link(camera); scene.camera=camera
def render(name,pos,target,scale,ortho=True):
    camera.location=pos; camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO' if ortho else 'PERSP'; camdata.ortho_scale=scale; camdata.lens=48
    scene.render.filepath=str(ROOT/'preview'/(name+'.png')); bpy.ops.render.render(write_still=True)
render('01_perspectiva_CAD',(470,650,420),(0,0,166),480)
render('02_spate_CAD',(-420,-650,390),(0,0,167),470)
render('03_lateral_CAD',(800,0,170),(0,0,170),440)
render('04_frontal_CAD',(0,900,190),(0,0,176),440)
render('13_insula_spate',(-240,-450,350),head_point(144,5,36),225)
render('11_grile_detaliu',(-230,-560,440),head_point(0,64,36),300)
render('12_racord_baza',(380,480,190),(0,-20,64),285)
render('06_porturi_detaliu',(220,-420,130),(0,-108,24),245)
render('07_camera_detaliu',(-260,440,360),head_point(144,10,0),230)
# Assembly views of the real separate cartridges and printed guide system.
port_saved={k:o.hide_render for k,o in objects.items()}
for k,o in objects.items():o.hide_render=k not in ('B01','P01','P02','P03','P04','P05','P06','P07','P08','P09','P10','P11','P12')
render('14_porturi_interior',(-160,250,185),(0,-108,22),250)
objects['P07'].location.z+=24;objects['P10'].location.z+=50
objects['P11'].location.y+=18;objects['P12'].location.y+=18
render('15_porturi_montaj',(-180,250,210),(0,-108,36),270)
objects['P07'].location.z-=24;objects['P10'].location.z-=50
objects['P11'].location.y-=18;objects['P12'].location.y-=18
for k,o in objects.items():o.hide_render=port_saved[k]
stand_saved={k:o.hide_render for k,o in objects.items()}
for k,o in objects.items():o.hide_render=k not in ('S01','S02','S21','S22','S23','S24')
objects['S02'].location.x-=100
render('16_picior_chei',(-450,300,230),(-45,-45,128),350)
objects['S02'].location.x+=100
marks=json.loads((ROOT/'docs/hidden_marks.json').read_text())
mark=next((m for m in marks if m.get('full_code',m['code'])=='S01' and 'centre' in m),None)
if mark:
    for k,o in objects.items():o.hide_render=k!='S01'
    yy,zz,xx=mark['centre']; target=(-xx,yy,zz)
    render('17_cod_ascuns',(-xx-120,yy+30,zz+20),target,38)
for k,o in objects.items():o.hide_render=stand_saved[k]
# Details from actual component meshes, repositioned only by camera.
saved={k:o.hide_render for k,o in objects.items()}
for k,o in objects.items(): o.hide_render=k not in ('H01','H02','R07')
ob=bpy.data.objects.get('Illustrative display / active area unmeasured'); ob.hide_render=True
render('08_LED_cap_integrare',(-330,-420,400),head_point(135,-75,13),150)
for k,o in objects.items(): o.hide_render=k not in ('B01','B02','B03','R08')
objects['B01'].hide_render=True
render('09_LED_baza_integrare',(260,340,240),(65,65,10),195)
for k,o in objects.items(): o.hide_render=k not in ('O01','O02','O03','O04','O05','O06','O07','O08','O09','O11','O12','O13','O14','O15','O16','O17','R03','R04')
objects['O03'].hide_render=True
render('10_camera_interior',(-320,-460,320),head_point(144,15,10),245)
for k,o in objects.items(): o.hide_render=saved[k]
ob.hide_render=False
base_saved={k:o.hide_render for k,o in objects.items()}
for k,o in objects.items():o.hide_render=k not in ('B01','B02','B03','B07','B05','B06','P01','P02','P03','P04','P05','P06','P07','P08','P09','P10','P11','P12')
objects['B07'].location.z+=85
objects['B03'].location.z-=35
ground.hide_render=True
render('19_baza_capace_ghidaje',(360,-480,370),(0,-15,55),330)
objects['B07'].location.z-=85
objects['B03'].location.z+=35
for k,o in objects.items():o.hide_render=base_saved[k]
for code,ob in objects.items():
    if code=='H01': delta=(0,125,72)
    elif code=='H02': delta=(0,74,42)
    elif code=='R01': delta=(0,35,20)
    elif code=='H04': delta=(0,-110,0)
    elif code.startswith('O'): delta=(80,30,10)
    elif code=='B03' or code.startswith('T3'): delta=(0,0,-45)
    elif code=='S02': delta=(85,0,0)
    else: delta=(0,0,0)
    ob.location+=Vector(delta)
ground.hide_render=True
render('05_explodata_CAD',(540,740,480),(0,0,155),620)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'preview/Terminal_OPD2203_R05.blend'))
