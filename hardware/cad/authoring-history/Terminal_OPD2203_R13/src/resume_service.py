from pathlib import Path
src=Path(__file__).with_name('service_r12.py').read_text()
exec(compile(src.split("h=local('H01')")[0],__file__,'exec'))
parts={}
for p in (R/'validation/service_brep').glob('*.brep'):
 s=Part.Shape();s.read(str(p))
 if not s.isValid():s.fix(.01,.001,.1)
 parts[p.stem]=s;print('LOADED',p.stem,s.isValid(),flush=True)
for x in [-65,65]:parts['H01']=parts['H01'].cut(box(7.6,3.8,4.1,x,111,6.6))
names={'H05':'Traversa superioara cu doua cleme ascunse','O04':'Rama captiva foita optica','O05':'Foita optica PETG natural 0.20 mm'}
tail=src[src.index("manifest=json.loads"):]
tail=tail.replace("s=s.removeSplitter()","s=s.removeSplitter()\n if not s.isValid():s.fix(.01,.001,.1)")
exec(compile(tail,__file__,'exec'))
