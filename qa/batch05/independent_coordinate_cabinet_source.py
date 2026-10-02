"""Read-only verification of current source hinge coordinate custom properties."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';p=ROOT/'assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);o=bpy.data.objects['AST-STF-007_door_hinge_pivot']
def value(v):
 if hasattr(v,'to_list'):return v.to_list()
 if hasattr(v,'to_dict'):return {k:value(x) for k,x in v.to_dict().items()}
 return v
props={k:value(v) for k,v in o.items()};loc=list(o.matrix_world.translation);source_expected=[-.837,-.317,.2];checks={'revision':props.get('coordinate_metadata_revision')=='hinge-frame-metadata-02','explicit_source_axis':props.get('hinge_axis_blender_source')==[0,0,1],'explicit_gltf_axis':props.get('hinge_axis_gltf_yup')==[0,1,0],'actual_source_pivot_matches':max(abs(a-b) for a,b in zip(loc,source_expected))<1e-6,'metadata_source_pivot_matches':props.get('hinge_pivot_blender_source_m')==source_expected,'metadata_gltf_pivot_matches':props.get('hinge_pivot_gltf_yup_m')==[-.837,.2,.317],'unqualified_axis_absent':'axis' not in props}
r={'path':str(p.relative_to(ROOT)),'source_sha256':before,'actual_pivot_source_m':loc,'custom_properties':props,'checks':checks,'pass':all(checks.values()),'read_only_hash_unchanged':before==hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Current source custom properties and actual hinge transform. Semantic source preservation is separately bound by the metadata-revision snapshot comparison.'};(OUT/'independent_coordinate_cabinet_source.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
