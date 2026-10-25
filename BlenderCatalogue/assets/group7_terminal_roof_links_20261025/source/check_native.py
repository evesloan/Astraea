"""Reopen the saved native; compare editable vertices and exported spatial bounds."""
import bpy
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'PLAN.json').read_text(encoding='utf-8'))
native=ROOT/'G7_TerminalRoofLinks_r011.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
worst=0.0
groups={}
for part in plan['parts']:
    obj=bpy.data.objects.get(part['name'])
    assert obj is not None and obj.type=='MESH',part['name']
    assert obj['stable_part_id']=='G7R11_'+part['name']
    assert len(obj.data.vertices)==len(part['vertices'])
    for vertex,expected in zip(obj.data.vertices,part['vertices']):
        v=obj.matrix_world@vertex.co
        actual=(v.x,v.z,-v.y)
        difference=max(abs(a-b) for a,b in zip(actual,expected))
        worst=max(worst,difference)
        assert difference<.0001,(part['name'],difference)
    groups.setdefault('G7R11_'+part['cell']+'_'+part['role'],[]).extend(part['vertices'])
raw=(ROOT/'G7_TerminalRoofLinks_r011.glb').read_bytes()
size=struct.unpack_from('<I',raw,12)[0]
gltf=json.loads(raw[20:20+size])
nodes=[n for n in gltf['nodes'] if 'mesh' in n]
assert len(nodes)==len(groups),(len(nodes),len(groups))
for node in nodes:
    points=groups[node['name']]
    expected_min=[min(v[i] for v in points) for i in range(3)]
    expected_max=[max(v[i] for v in points) for i in range(3)]
    mesh=gltf['meshes'][node['mesh']]
    assert len(mesh['primitives'])==1
    positions=gltf['accessors'][mesh['primitives'][0]['attributes']['POSITION']]
    for actual,expected in zip(positions['min']+positions['max'],expected_min+expected_max):
        assert math.isfinite(actual) and abs(actual-expected)<.0001,(node['name'],actual,expected)
    assert node['extras']['cell'] and node['extras']['role']
report=dict(status='NATIVE_REOPEN_AND_GLB_BOUNDS_PASS',editable_parts=len(plan['parts']),
            spatial_batches=len(nodes),maximum_native_coordinate_delta_m=worst,
            blender_version=bpy.app.version_string,native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
            glb_sha256=hashlib.sha256(raw).hexdigest(),
            scope='Saved editable geometry and export bounds only; runtime, visual and capacity acceptance pending')
(ROOT/'NATIVE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
