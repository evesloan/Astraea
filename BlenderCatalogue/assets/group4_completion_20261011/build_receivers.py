from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2]
F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
family='group4_completion_receiving_20261011';asset_id='AST-TRM-G4-023'
cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
assert asset_id not in json.dumps(cat), 'Catalogue ID already owned'
plan=json.loads((W/'RECEIVING_PLAN.json').read_text())
assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in plan['source_pins'].items())
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0]
sc=sc.replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name",'OUT=W;FAMILY=family')
sc=sc.replace("assert FAMILY=='group4_tram_connections_20261009'",'')
sc=sc.replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']",'IDS=[asset_id]')
sc=sc.replace("['FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO']","['COMPLETION_RECEIVERS','UNEXPORTED_REFERENCE_AND_STUDIO']")
exec(sc,globals());current=collections['COMPLETION_RECEIVERS']
for q in plan['new_members']:
    lo=q['min'];hi=q['max'];o=box(q['name'],[(a+b)/2 for a,b in zip(lo,hi)],[b-a for a,b in zip(lo,hi)],materials[q['material']],q['role'])
    o['receiver']=str(q['receiver'] or 'proposed station threshold')
for st in plan['stations']:
    for i,t in enumerate(st.get('floor_triangles_xz',[])):
        vs=[(x,y,z) for y in [52.26,52.5] for x,z in t]
        o=mesh(st['label']+'_MissingFloor_'+str(i),vs,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],stone,'missing-only station annex floor; original floor and pit subtracted')
        o['floor_region_proposal']='G4_'+st['label']+'_ANNEX'
        pass  # markers are added once per station below
for st in plan['stations']:
    marker(st['label']+'_LOWER_LIFT_ROOT',st['lift_root'],'existing commons_lift two-stop binding; no original stop retiming')
# Six weighted opal lenses fit the original end/central station backplates.
# The long stations already retain their source opal fittings.
for label,x,zs,direction in [('FORWARD',1.605,[-434.25,-429.75],-1),('AFT',1.605,[429.75,434.25],-1),('CENTRAL',-7.405,[-74.25,-69.75],1)]:
    for i,z in enumerate(zs):
        o=box(label+'_OpalLens_'+str(i),(x+direction*.035,58.15,z),(.08,.23,.32),ivory,'opal lens with 5mm backplate embed','no_collision_detail')
        marker(label+'_LIGHT_EXIT_'+str(i),(x+direction*.085,58.15,z),'visible opal light exit; warm 8m range; existing budget')
asset=asset_id+'_station_receiving_r002.glb';native='Group4_Completion_Receiving_r002.blend'
for im in bpy.data.images:
    if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.object.select_all(action='DESELECT')
for o in current.objects:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
def export(path):
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
export(W/asset);bpy.ops.wm.save_as_mainfile(filepath=str(W/native),compress=True)
rows=[]
for o in parts:
    v=[G(o.matrix_world@p.co) for p in o.data.vertices]
    rows.append(dict(mesh=o.name,min=[min(p[i] for p in v) for i in range(3)],max=[max(p[i] for p in v) for i in range(3)],role=o['role'],policy=o['collision_policy'],vertices=len(v),faces=len(o.data.polygons)))
(W/'MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n')
report=dict(asset=asset,native=native,catalogue_id=asset_id,registered=False,meshes=len(parts),materials=texture_pins,source_only=True)
(W/'NATIVE_BUILD.json').write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_RECEIVERS_BUILT',len(parts),'parts; originals untouched')
