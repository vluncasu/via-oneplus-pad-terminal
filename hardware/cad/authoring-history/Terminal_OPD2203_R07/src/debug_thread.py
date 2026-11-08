exec(compile(open(__file__.replace('debug_thread.py','build.py')).read().split('# Base monobloc')[0],__file__,'exec'))
t=thread(12,22,.35);print('tool',t.isValid(),len(t.Solids),t.Volume);t.exportStep(str(R/'validation/thread_debug.step'))
s=Part.Shape();s.read(str(R/'validation/leg_before_thread.step'));print('leg loaded',s.isValid())
for x in [-48,48]:
 for y in [-69,-49]:
  s=s.cut(move(t,x,y,44),.01).removeSplitter();print('cut',x,y,s.isValid(),len(s.Solids),flush=True)
  if not s.isValid():
   s.fix(.01,.001,.1);print('fix',s.isValid(),flush=True)
s.exportStep(str(R/'validation/leg_fixed.step'))
