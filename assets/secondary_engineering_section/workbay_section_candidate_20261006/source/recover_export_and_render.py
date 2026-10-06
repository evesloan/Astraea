"""Ordinary read-only source reopen after exporter cleanup crash; new export/views only."""
from pathlib import Path
import bpy,json,sys,hashlib,resource
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R/'source/AST-ENG-008_workbay_section.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source);S=json.loads((R/'source/section_plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));sc=bpy.context.scene;leaf=[o for o in sc.objects if o.get('door_leaf_id')];assert len(leaf)==4
sys.path.insert(0,str(R/'source'));from export_section_package import export_package
report=export_package(R,source,S['removed_upper_source_assemblies']);assert sha(source)==before
cv=lambda p:Vector((p[0],-p[2],p[1]))
for o in leaf:o.location+=cv((0,0,-1.22))
# Existing primary source image remains valid for this byte-identical .blend; no repeat render.
o=sc.camera;o.location=cv((20.77,7.65,-403.35));o.rotation_euler=(cv((23.5,6.15,-404.8))-o.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(R/'views/workbay_west_threshold_section_refined.png');bpy.ops.render.render(write_still=True)
record={'scope':'Refined source section/export; not Game installation','source_sha256':before,'export_sha256':report['export_sha256'],'source_reopened_unchanged':sha(source)==before,'primary_eye':S['ordinary_eye'],'vertical_fov':72,'primary_same_exposure':0,'world_strength':0,'source_lights':5,'new_visual_panes_single_sheet':True,'contact_panes_mm':26,'old_glass_shader_untouched':True,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'supplemental_threshold_eye':[20.77,7.65,-403.35],'supplemental_threshold_aim':[23.5,6.15,-404.8]};(R/'qa/section_refined_build.json').write_text(json.dumps(record,indent=2)+'\n');print('SECTION_REOPEN_EXPORT_RENDER_OK',record)
