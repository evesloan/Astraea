"""Copper Kettle deep-pier successor;immutable shallow component remains intact."""
from pathlib import Path
import bpy,bmesh,ast,json,hashlib
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original=P/'source/large_venue_doors/large_foyer_8m_r001.blend';before=sha(original)
bpy.ops.wm.open_mainfile(filepath=str(original))
M={role:bpy.data.materials['ASTRAEA_'+role] for role in ['ivory_enamel','champagne_metal','retail_terracotta_enamel']}
M['glass']=bpy.data.materials['GROUP5_large_foyer_glass']
template=P/'source/build_components.py';parsed=ast.parse(template.read_text())
FACES=ast.literal_eval(next(n.value for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FACES' for t in n.targets)))
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(template),'exec'),globals())
track=bpy.data.objects['FixedTrack'];height=3.9;half=4.0;stand_off=1.3
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('track_wall_mount_'):bpy.data.objects.remove(obj,do_unlink=True)
for x in [-half-.2,half+.2]:
    cube('track_wall_mount_'+str(x),(x-.06,height+.03,.035),(x+.06,height+.06,stand_off-.09),'champagne_metal',track)
# Reveals bridge the retained wall to the mechanism with a clear sliding plane.
# No aperture narrowing,original cuts or floor addition.
for side,lo,hi in [('L',-half-.12,-half),('R',half,half+.12)]:
    cube('track_pocket_reveal_'+side,(lo,0,.12),(hi,height,stand_off-.105),'ivory_enamel',track)
bpy.context.scene['scope']='Copper Kettle original deep-pier correction;extended wall mounts and bounded pocket reveals;original source and shallow pair preserved'
native=P/'source/large_venue_doors/large_foyer_8m_deep_r002.blend';out=P/'exports/large_venue_doors/large_foyer_8m_deep_r002.glb'
assert not native.exists() and not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
nsha=sha(native);esha=sha(out)
bpy.ops.wm.open_mainfile(filepath=str(native))
repeat=Path('/tmp/group5_large_foyer_8m_deep_repeat.glb')
bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
assert sha(repeat)==esha and sha(native)==nsha and sha(original)==before
row={'width_m':8.0,'height_m':3.9,'stand_off_m':stand_off,'source_meshes':35,'native':str(native.relative_to(P)),
    'native_sha256':nsha,'export':str(out.relative_to(P)),'export_sha256':esha,'parent_shallow_native_sha256':before,
    'primitive_template_sha256':sha(template),'fresh_native_repeat_export_byte_identical':True,
    'panels':4,'wall_mounts':2,'pocket_reveals':2,'role_and_pressure_acceptance':False}
p=P/'docs/LARGE_VENUE_DOOR_COMPONENTS.json';d=json.loads(p.read_text())
for r in d['variants']:r['stand_off_m']=.3
d['variants'].append(row);p.write_text(json.dumps(d,indent=2)+'\n')
print('GROUP5_LARGE_FOYER_DEEP_SOURCE_PASS',35)
