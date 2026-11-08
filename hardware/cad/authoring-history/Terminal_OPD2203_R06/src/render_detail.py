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

for k,o in objects.items():o.hide_render=k not in ('P01','P05','P07')
for ob in bpy.data.objects:
    if ob.name.startswith('Illustrative display'):ob.hide_render=True
for code,dx in [('P01',-112),('P05',-9),('P07',52)]:
    objects[code].location.x=dx
    objects[code].data.materials.clear();objects[code].data.materials.append(mat('Port detail navy',(.035,.065,.09),0,.34))
light('Front detail',(0,-190,70),250000,65)
bpy.data.objects['Front detail'].rotation_euler=(Vector((0,-105,22))-bpy.data.objects['Front detail'].location).to_track_quat('-Z','Y').to_euler()
render('18_porturi_macro',(15,-210,63),(0,-105,21),85)
