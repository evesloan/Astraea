import bpy,pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[4];D=pathlib.Path(__file__).resolve().parents[1]
receipt=json.loads((D/'BUILD_RECEIPT.json').read_text());changed=set(receipt['changed_native_objects'])
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.data.objects:
  data={'type':o.type,'matrix':[list(v) for v in o.matrix_world],'props':{k:str(v) for k,v in o.items()}}
  if o.type=='MESH':data.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],uv={layer.name:[list(p.uv) for p in layer.data] for layer in o.data.uv_layers},materials=[m.name if m else None for m in o.data.materials])
  result[o.name]=data
 return result
a=snap(R/'BlenderCatalogue/assets/aft_crown_platform/source/AST-CMD-005.blend');b=snap(D/'AST-CMD-005_fixture_clearance_r002.blend');assert a.keys()==b.keys()
for name in a:
 old=a[name];new=b[name]
 if name in changed:
  for i in range(4):
   for j in range(4):assert abs(new['matrix'][i][j]-old['matrix'][i][j]-(.05 if (i,j)==(2,3) else 0))<.00002,(name,i,j)
  old=dict(old);new=dict(new);old.pop('matrix');new.pop('matrix');assert old==new,name
 else:assert old==new,name
report={'status':'PASS','objects':len(a),'exact_unchanged_objects':len(a)-len(changed),'exact_unchanged_mesh_arrays_uv_material_names_and_properties':True,'changed_transforms_only':sorted(changed),'translation_blender_z_m':.05,'runtime_Godot_Y_m':.05,'largest_transform_error_m':max(abs(b[n]['matrix'][2][3]-a[n]['matrix'][2][3]-.05) for n in changed)}
(D/'NATIVE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
