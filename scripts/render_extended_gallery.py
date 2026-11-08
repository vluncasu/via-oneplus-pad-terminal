"""Render additional actual-mesh product, service and manufacturing views.
Blender 4.2 LTS; all transformations are inspection-only, never print-file edits.
VIA_RENDER_ONLY can select comma-separated two-digit figure numbers.
"""
import os,runpy
from pathlib import Path
os.environ['VIA_NO_SCENE_SAVE']='1'
if not os.environ.get('VIA_RENDER_ONLY'):os.environ['VIA_RENDER_ONLY']=','.join(str(i) for i in range(14,34))
globals().update(runpy.run_path(str(Path(__file__).with_name('render_gallery.py'))))
s.cycles.samples=int(os.environ.get('VIA_RENDER_SAMPLES','28'))
s.render.threads=int(os.environ.get('VIA_RENDER_THREADS','4'))
s.render.resolution_x=1700;s.render.resolution_y=1250
# Fill from below makes internal load paths and thread seats readable.
bpy.ops.object.light_add(type='AREA',location=(140,160,-180));fill=bpy.context.object
fill.name='Service inspection underside fill';fill.data.energy=200000;fill.data.shape='DISK';fill.data.size=270
fill.rotation_euler=(Vector((0,0,100))-fill.location).to_track_quat('-Z','Y').to_euler()
def assembled():
 for c,o in objs.items():o.hide_render=base[c]
 ground.hide_render=False
assembled();view('14-orthographic-front',(0,900,170),(0,0,170),500)
assembled();view('15-orthographic-rear',(0,-900,170),(0,0,170),500)
assembled();view('16-opposite-front-three-quarter',(-470,650,440),(0,0,165),520)
assembled();view('17-overhead-product-view',(0,40,950),(0,0,150),490)
assembled();original_floor_scale=ground.scale.copy();ground.scale*=100
view('18-low-angle-led-belts',(420,700,200),(0,0,160),510)
ground.scale=original_floor_scale
assembled();view('19-opposite-rear-three-quarter',(440,-650,390),(0,0,165),520)
# Head in normal assembly coordinates with service covers omitted.
isolate(['H01','R01','O01','O05','O06','H05','V21','V22','V23','V24'])
view('20-open-head-tablet-seating',(230,-480,340),(0,0,240),390)
isolate(['H01','H04','H05','H06','V51','V52','V53','V54'])
view('21-rear-cover-and-retention-assembly',(-250,-500,340),(0,0,245),400)
isolate(['B01','P01','B07','R02']);objs['R02'].data.materials.clear();objs['R02'].data.materials.append(material('Provisional supply envelope - reference only',(.8,.23,.035),.4))
view('22-base-underside-supply-envelope',(320,330,-220),(0,-20,55),340)
isolate(['B07','R02']);view('23-stand-root-supply-clearance',(-250,320,-180),(0,-25,65),330)
isolate(['B03','V41','V42','V43','V44','V31','V32','V33','V34'])
view('24-bottom-service-cover-fasteners',(260,330,-260),(0,0,0),300)
isolate(['P01']);target=center('P01');view('25-dummy-ports-front-detail',target+Vector((30,-290,80)),target,215)
isolate(['P01']);view('26-port-cartridge-rear-cable-funnel',target+Vector((-40,240,100)),target,215)
isolate(['O01','O06','O03','V61','V62']);target=center('O01');view('27-optical-cassette-film-omitted',target+Vector((110,270,110)),target,240)
isolate(['O01','O03','V61','V62','R03']);objs['R03'].data.materials.clear();objs['R03'].data.materials.append(objs['R02'].data.materials[0]);view('28-optical-usb-service-side',target+Vector((-120,-240,130)),target,240)
isolate(['H01','H05','H06']);target=center('H05');view('29-tablet-retention-interface',target+Vector((200,-250,150)),target,330)
# Explicit stand section: exposes the CAD void; it is not an invented cable diagram.
isolate(['B07']);bpy.ops.mesh.primitive_cube_add(size=1,location=(-200,0,150));box=bpy.context.object;box.scale=(400,600,600);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);box.hide_render=True
cut=objs['B07'].modifiers.new('Opposite duct section - inspection only','BOOLEAN');cut.operation='DIFFERENCE';cut.object=box
view('30-cable-duct-opposite-section',(-450,180,240),(0,-30,130),300)
objs['B07'].modifiers.remove(cut);bpy.data.objects.remove(box,do_unlink=True)
isolate(['H01']);view('31-head-structure-front-camera-region',(0,550,320),(0,0,240),390)
isolate(['H04','H06']);view('32-symmetric-rear-ventilation',(-120,-600,310),(0,0,240),390)
isolate(['O06']);target=center('O06')
face_material=material('Black PETG - matte detail inspection',(.004,.008,.012),.58)
face_material.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.08
objs['O06'].data.materials.clear();objs['O06'].data.materials.append(face_material)
view('33-dummy-sensor-face-raking-light',target+Vector((25,320,20)),target,235)
print('EXTENDED_GALLERY_COMPLETE',flush=True)
