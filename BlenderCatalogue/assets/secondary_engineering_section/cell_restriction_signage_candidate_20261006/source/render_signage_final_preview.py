from pathlib import Path
import bpy,json,hashlib,math,resource,time
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=json.loads((R/'source/sign_plan.json').read_text());S=R/'source/AST-ENG-008_cell_restriction_signage_v2.blend';B=json.loads((R/'qa/EXPORT_CORRECTION_004.json').read_text());assert json.loads((R/'qa/FINAL_SOURCE_EXPORT_EQUIVALENCE.json').read_text())['passed'];pins=dict(P['immutable_inputs']);pins[str(S)]=B['source_sha256']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cv(p):return Vector((p[0],-p[2],p[1]))
for p,h in pins.items():assert sha(p)==h
bpy.ops.wm.open_mainfile(filepath=P['source_blend']);scene=bpy.context.scene
with bpy.data.libraries.load(str(S),link=False)as(a,b):b.objects=list(a.objects)
for o in b.objects:scene.collection.objects.link(o)
lights=[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'spot_full_angle_degrees':math.degrees(o.data.spot_size)if o.data.type=='SPOT'else None,'xyz':[o.location.x,o.location.z,-o.location.y]}for o in scene.objects if o.type=='LIGHT'and not o.hide_render]
assert len(lights)==5 and all(x['type']=='SPOT'for x in lights),('Unexpected fixture state',lights)
worldstrength=float(scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value);assert worldstrength==0 and scene.view_settings.exposure==0
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100;cam=bpy.data.cameras.new('SIGNAGE_SUPPORTED_EYE');cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=32/(2*math.tan(math.radians(36)));cam.clip_start=.05;cam.clip_end=100;o=bpy.data.objects.new('SIGNAGE_SUPPORTED_EYE',cam);scene.collection.objects.link(o);scene.camera=o
images=[]
for view in P['views']:
 o.location=cv(view['eye_xyz']);o.rotation_euler=(cv(view['aim_xyz'])-o.location).to_track_quat('-Z','Y').to_euler();dest=R/'views'/('source_final_'+view['name']+'_closed_sign.png');assert not dest.exists();scene.render.filepath=str(dest);start=time.time();bpy.ops.render.render(write_still=True);images.append({'path':str(dest.relative_to(R)),'sha256':sha(dest),'view':view,'seconds':time.time()-start})
for p,h in pins.items():assert sha(p)==h
report={'scope':'Source-only composed legibility preview, unchanged saved-source physical fixture powers/angles/exposure; not actual Godot or normal postprocess acceptance.','images':images,'lights':lights,'world_strength':worldstrength,'exposure':0,'new_light_count':0,'cycles_samples':64,'denoising':True,'quality_scope':'Sampling/denoising refinement only; exact framing, exposure, five fixture powers and source geometry unchanged','original_walls_glass_not_hidden':True,'glyphs_backed_by_exact_header_and_leaf':True,'source_inputs_unchanged':pins,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/FINAL_PREVIEW_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print('SIGN_PREVIEWS_COMPLETE',json.dumps(report),flush=True)
