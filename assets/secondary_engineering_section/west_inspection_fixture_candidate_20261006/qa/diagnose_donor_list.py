from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).parents[1];P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/source/AST-ENG-008.blend');assert hashlib.sha256(P.read_bytes()).hexdigest()=='af5064eeeaccb436f1371ae43eca346f11f6f18fe3090e93a2a01a52c6cbfead'
bpy.ops.wm.read_factory_settings(use_empty=True)
names=['plant_inspection_n_mount','plant_inspection_n_housing','plant_inspection_n_opal','plant_inspection_n_ceiling_stem'];wanted=tuple(names)
with bpy.data.libraries.load(str(P),link=False)as(src,dst):
 assert all(n in src.objects for n in wanted);dst.objects=names
result={'original_requested_names':list(wanted),'requested_list_types_after_load':[type(x).__name__for x in names],'requested_list_values_after_load':[x.name if hasattr(x,'name')else x for x in names],'returned_names':[x.name if x else None for x in dst.objects],'exact_donors_present':sorted(x.name for x in dst.objects)==sorted(wanted),'source_unchanged':hashlib.sha256(P.read_bytes()).hexdigest()=='af5064eeeaccb436f1371ae43eca346f11f6f18fe3090e93a2a01a52c6cbfead','no_saved_source_or_export':not list((R/'source').glob('*.blend')) and not list((R/'exports').glob('*.glb'))}
p=R/'qa/DONOR_LIST_MUTATION_DIAGNOSTIC.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
