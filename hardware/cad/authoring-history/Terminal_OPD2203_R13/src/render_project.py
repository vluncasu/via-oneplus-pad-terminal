import bpy,json,math,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];OUT=R/'randari_proiect';OUT.mkdir(exist_ok=True)
exec(compile((R/'src/render.py').read_text().split("view('01_asamblat'")[0],'setup','exec'))
s.cycles.samples=24;s.render.resolution_x=2000;s.render.resolution_y=1600
d.clip_end=20000;d.clip_start=.1
# Custom warm editorial studio; the huge floor has no visible horizon.
# A continuous circular cyclorama bends the floor into a wall in every direction.
verts=[(0,0,-4.05)];faces=[];N=128
profile=[(650,-4.05),(800,5),(950,45),(1100,130),(1250,270),(1400,470),(1520,750),(1580,1100),(1600,1700),(1600,4000)]
for radius,z in profile:
 for i in range(N):
  angle=2*math.pi*i/N;verts.append((radius*math.cos(angle),radius*math.sin(angle),z))
for i in range(N):faces.append((0,1+i,1+(i+1)%N))
for j in range(len(profile)-1):
 for i in range(N):
  a=1+j*N+i;b=1+j*N+(i+1)%N;faces.append((a,1+(j+1)*N+i,1+(j+1)*N+(i+1)%N,b))
mesh=bpy.data.meshes.new('Ciclorama circulara');mesh.from_pydata(verts,[],faces);mesh.update();ground.data=mesh
ground.location=(0,0,0)
ground.scale=(3,3,1)
for face in mesh.polygons:face.use_smooth=True
ground.data.materials.clear();ground.data.materials.append(mat('Studio nisip cald',(.48,.35,.25)))
s.render.film_transparent=True;s.use_nodes=True
nodes=s.node_tree.nodes;nodes.clear()
layer=nodes.new('CompositorNodeRLayers');over=nodes.new('CompositorNodeAlphaOver');out=nodes.new('CompositorNodeComposite')
over.inputs[1].default_value=(.48,.35,.25,1)
s.node_tree.links.new(layer.outputs['Image'],over.inputs[2]);s.node_tree.links.new(over.outputs[0],out.inputs[0])
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
rot=Matrix.Rotation(math.radians(120),4,'X')
def wp(p):return rot@Vector(p)+Vector((-12,10,240))
records=json.loads((OUT/'imagini.json').read_text()) if os.environ.get('SELECT_VIEWS') else []
prod=[c for c in objs if not c.startswith('R')]+['R01']
def show(codes,floor=False):
 ground.hide_render=not floor
 for c,o in objs.items():o.hide_render=c not in codes
def shot(code,title,pos,target,scale,note=''):
 if os.environ.get('SELECT_VIEWS') and code[:2] not in os.environ['SELECT_VIEWS'].split(','):return
 if os.environ.get('RERENDER_INTERNAL') and int(code[:2])<10:return
 s.view_settings.exposure=-.7 if int(code[:2])>=10 else -.15
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
 # Fit visible CAD bounds with an 8% margin; exclude studio and cutter geometry.
 rotation=cam.rotation_euler.to_matrix();inv=rotation.transposed()
 points=[inv@(ob.matrix_world@Vector(v)) for ob in objs.values() if not ob.hide_render for v in ob.bound_box]
 if points and code!='16_prindere_filetata' and code!='08_porturi':
  xmin,xmax=min(v.x for v in points),max(v.x for v in points)
  ymin,ymax=min(v.y for v in points),max(v.y for v in points)
  center=inv@cam.location
  cam.location+=rotation@Vector(((xmin+xmax)/2-center.x,(ymin+ymax)/2-center.y,0))
  d.ortho_scale=max(scale,(xmax-xmin)*1.16,(ymax-ymin)*s.render.resolution_x/s.render.resolution_y*1.16)
 s.render.filepath=str(OUT/(code+'.png'));bpy.ops.render.render(write_still=True)
 record=dict(file=code+'.png',title=title,note=note)
 existing=next((i for i,a in enumerate(records) if a['file']==record['file']),None)
 if existing is None:records.append(record)
 else:records[existing]=record
 (OUT/'imagini.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 print('FINISHED',code,flush=True)
show(prod,True)
shot('01_perspectiva_fata','Ansamblu — perspectivă frontală',(470,650,420),(0,0,166),490)
shot('02_perspectiva_spate','Ansamblu — perspectivă posterioară',(-420,-650,390),(0,0,166),490)
shot('03_fata','Vedere frontală',(0,800,220),(0,0,166),460)
shot('04_spate','Vedere posterioară',(0,-800,220),(0,0,166),460)
shot('05_lateral','Profil lateral',(800,0,200),(0,0,166),460)
shot('06_de_sus','Vedere de sus',(300,220,850),(0,0,120),490)
show(prod)
shot('07_dedesubt','Capac service și picioare',(-260,-320,-480),(0,0,30),390)
shot('08_porturi','Porturi dummy și intrare cablu',(120,-450,110),(0,-105,22),240)
show(['B07'])
shot('09_picior_integral','Picior și capac sursă monobloc',(-320,250,230),(0,-30,130),320,'B07 izolată, poziție de asamblare păstrată.')
# Underlighting makes the actual braces readable.
ld=bpy.data.lights.new('Lumina inspectie inferioara','AREA');ld.energy=1800000;ld.size=280
lo=bpy.data.objects.new('Lumina inspectie inferioara',ld);s.collection.objects.link(lo);lo.location=(100,80,-170);lo.rotation_euler=(Vector((0,-30,60))-lo.location).to_track_quat('-Z','Y').to_euler()
shot('10_nervuri_radacina','Întăririle rădăcinii piciorului',(270,340,-220),(0,-30,75),330,'B07 izolată; interiorul volumului pentru sursă.')
show(['B07','R02']);ref=mat('Gabarit sursa — referinta',(.05,.4,.55));objs['R02'].data.materials.clear();objs['R02'].data.materials.append(ref)
shot('11_rezerva_sursa','Nervuri și gabaritul sursei',(270,340,-220),(0,-30,65),330,'Albastru: volum de referință al sursei, fără electronica detaliată.')
show(['B07'])
bpy.ops.mesh.primitive_cube_add(size=1,location=(200,0,150));cut=bpy.context.object;cut.scale=(400,600,600);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cut.hide_render=True
mod=objs['B07'].modifiers.new('Sectiune inspectie','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
shot('12_sectiune_canal_cabluri','Secțiune — canalul interior al piciorului',(600,50,220),(0,-30,130),310,'Secțiune virtuală; jumătatea dreaptă este ascunsă prin tăiere. Nu este piesă separată.')
objs['B07'].modifiers.remove(mod);bpy.data.objects.remove(cut,do_unlink=True)
show(['B01']);shot('13_baza_interior','Bază monobloc — canal LED integrat',(280,-330,350),(0,0,10),360,'B01 izolată; fostul L11 este parte din structură.')
show(['B03']);shot('14_capac_inferior','Capacul inferior — fața interioară',(200,-220,350),(0,0,6),340,'B03 izolată.')
show(['H01']);shot('15_cap_interior','Cap monobloc — canal LED integrat',wp((180,-220,380)),wp((12,0,12)),480,'H01 izolată; fostul L21 este parte din structură.')
shot('16_prindere_filetata','Detaliu — suport filetat și punte',wp((-125,-140,105)),wp((-96,-92,19)),78,'Geometrie CAD; rezistența mecanică nu este validată prin randare.')
show(['H04']);shot('17_capac_posterior_interior','Capac posterior — opritoare și nervuri',wp((180,-200,-350)),wp((12,0,28)),470,'H04 văzut dinspre interior; opritoare tabletă și ghidaje cabluri.')
show(['O01']);shot('18_caseta_optica_fata','Caseta optică — elemente dummy',wp((200,-60,-330)),wp((144,0,12)),245,'O01 izolată; filament negru, detalii geometrice reale.')
shot('19_caseta_optica_interior','Caseta optică — interior și filete',wp((270,-80,300)),wp((144,0,15)),245,'O01 izolată; accesul USB-C se află în zona mediană.')
show(['O01','O03','V61','V62']);shot('20_caseta_asamblata','Casetă cu capac service',wp((280,-100,300)),wp((144,0,18)),250,'Ansamblu local în poziția normală; fără deplasarea pieselor.')
orange=mat('Gabarit banda LED — referinta',(1,.28,.02))
for c in ['R04','R05']:objs[c].data.materials.clear();objs[c].data.materials.append(orange)
show(['B01','R04']);shot('21_led_baza','Bază — poziția rezervată benzii LED',(260,-330,360),(0,0,10),360,'Portocaliu: gabarit de montaj; nu simulare de lumină.')
show(['H01','R05']);shot('22_led_cap','Cap — poziția rezervată benzii LED',wp((180,-220,380)),wp((12,0,12)),480,'Portocaliu: gabarit de montaj; nu simulare de lumină.')
show(['V52']);ob=objs['V52'];target=sum((Vector(v) for v in ob.bound_box),Vector())/8
shot('23_surub_posterior','Șurub imprimat posterior',target+Vector((45,55,40)),target,38,'Piesă izolată, filet imprimabil experimental.')
show(['V31']);ob=objs['V31'];target=sum((Vector(v) for v in ob.bound_box),Vector())/8
shot('24_picior_filetat','Picior sferic filetat cu fantă',target+Vector((30,-45,-30)),target,40,'Piesă izolată.')
show(prod,True);lo.hide_render=True
cam.location=(470,650,420);cam.rotation_euler=(Vector((0,0,166))-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=490
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scena_randari_R11_ASAMBLAT.blend'))
