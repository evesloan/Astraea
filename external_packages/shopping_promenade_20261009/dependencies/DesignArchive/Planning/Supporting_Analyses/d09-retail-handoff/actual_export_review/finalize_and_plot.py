"""Verify the final freeze and plot decoded mesh evidence without Blender/Godot."""
from pathlib import Path
import os, ast, json, hashlib
from datetime import datetime, timezone
import numpy as np

OUT=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
os.environ['MPLCONFIGDIR']=str(OUT/'.mpl_cache')
os.environ['XDG_CACHE_HOME']=str(OUT/'.cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.patches import Rectangle, Patch

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda name,obj:(OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
old=OUT/'current_snapshot_actual_export_review.json'
old_bytes=old.read_bytes();old_sha=hashlib.sha256(old_bytes).hexdigest()
assert old_sha=='f618c5b2c1d432e5103cc3396eb764aa8c8fda0da882d804f8c470c751ca7bc1'
receipt_path=CAT/'qa/batch18/arrangement_freeze_receipt.json'
receipt_bytes=receipt_path.read_bytes();receipt_sha=hashlib.sha256(receipt_bytes).hexdigest()
assert receipt_sha=='a25e209aff1076bce13f2d22d1d59f75ca48bd40b9764f48b4dbb78bb7b7883e'
receipt=json.loads(receipt_bytes);assert len(receipt['files'])==18
verified=[]
for row in receipt['files']:
    p=CAT/row['path'];data=p.read_bytes();actual=hashlib.sha256(data).hexdigest()
    assert actual==row['sha256'] and len(data)==row['bytes'],row['path']
    verified.append({**row,'actual_sha256':actual,'actual_bytes':len(data),'verified':True})

# Execute the unchanged independent decoder/checker through report construction only.
# Its final file-writing and printing expressions are deliberately excluded, preserving
# the prior current-snapshot artifact byte-for-byte while rerunning the same checks.
decoder=OUT/'review_exports.py';tree=ast.parse(decoder.read_text());body=[]
for statement in tree.body:
    if isinstance(statement,ast.Expr) and isinstance(statement.value,ast.Call) and isinstance(statement.value.func,ast.Attribute) and statement.value.func.attr=='write_text':break
    body.append(statement)
assert len(body)<len(tree.body)
g={'__file__':str(decoder),'__name__':'bounded_frozen_decode'}
exec(compile(ast.Module(body=body,type_ignores=[]),str(decoder),'exec'),g)
report=g['report'];triangles=g['all_tri'];plan=g['plan']
assert old.read_bytes()==old_bytes

render_path=CAT/'qa/batch18/assembly/r01/render_evidence.json'
render=json.loads(render_path.read_text())
frozen={r['path']:r for r in verified}
assert render['execution_complete'] and render['inputs_unchanged_during_execution']
assert render['plan_sha256']==frozen['qa/batch18/assembly/plan.json']['sha256']
assert render['executed_script_sha256']==frozen['qa/batch18/assembly/build_inspection.py']['sha256']
assert len(render['views'])==4
for item in render['items']:
    assert item['export_sha256']==frozen[item['export']]['sha256']
    plan_item=next(i for i in plan['items'] if i['key']==item['row_key'])
    for k in ['source_path','manifest_path']:
        assert item['base_hashes'][k]==frozen[plan_item[k]]['sha256']

palette={'wall_bay':'#c86f43','island':'#bda36a','workbench':'#55848b',
         'bay_case':'#725887','island_case':'#725887','bench_case':'#725887'}
fig=plt.figure(figsize=(14,8.5),layout='constrained',facecolor='#f5f3ec')
grid=fig.add_gridspec(2,2,width_ratios=[1.05,1.05],height_ratios=[1,1])
planax=fig.add_subplot(grid[:,0]);axA=fig.add_subplot(grid[0,1]);axB=fig.add_subplot(grid[1,1])
for ax in [planax,axA,axB]:
    ax.set_facecolor('#fcfbf7');ax.grid(color='#dad8d0',linewidth=.5);ax.set_axisbelow(True);ax.tick_params(labelsize=8)
planax.add_patch(Rectangle((-6,0),12,12,fill=False,edgecolor='#273e49',linewidth=1.8,zorder=8))
region_colors={r['id']:('#d7dcdd' if r['id'] in ['arrival_band','central_test_strip'] else '#edf0e2') for r in plan['proposed_empty_regions']}
for region in plan['proposed_empty_regions']:
    lo=np.array(region['min_source_m']);hi=np.array(region['max_source_m'])
    planax.add_patch(Rectangle(lo[:2],*(hi-lo)[:2],facecolor=region_colors[region['id']],edgecolor='#91a0a1',linestyle='--',linewidth=.8,zorder=1))

for key,tris in triangles.items():
    # Top-down projection of actual referenced triangles, not an AABB silhouette.
    order=np.argsort(tris[:,:,2].mean(1));poly=tris[order,:,:2]
    planax.add_collection(PolyCollection(poly,facecolors=palette[key],edgecolors='#3b454b',linewidths=.11,alpha=1,zorder=5 if 'case' in key else 3))
labels={
 'wall_bay':((-5.75,6.0),(-4.85,4.75),'001 wall bay'),
 'island':((3.2,5.35),(3.2,4.6),'002 island'),
 'workbench':((4.5,9.6),(4.0,9.1),'003 bench'),
 'bay_case':((-2.35,3.1),(-4.79,3.15),'004a case'),
 'island_case':((4.85,3.25),(3.25,3.88),'004b case'),
 'bench_case':((4.8,8.05),(2.67,8.85),'004c case')}
for key,(txt,xy,label) in labels.items():
    planax.annotate(label,xy=xy,xytext=txt,fontsize=8,ha='center',arrowprops={'arrowstyle':'-','color':'#46565d','lw':.65},zorder=10)
planax.text(0,.65,'arrival band\nPROPOSED',ha='center',va='center',fontsize=8)
planax.text(0,7.2,'central strip\nPROPOSED',ha='center',va='center',fontsize=8,rotation=90)
planax.text(-3.6,4.7,'browse pad',ha='center',fontsize=7,rotation=90)
planax.text(3.2,2.6,'browse pad',ha='center',fontsize=7)
planax.text(3.2,7.5,'public pad',ha='center',fontsize=7)
planax.text(3.2,10.3,'staff pad',ha='center',fontsize=7)
for x,label in [(-4.85,'A'),(3.2,'B')]:
    planax.plot([x,x],[.15,11.7],linestyle='-.',color='#30363b',linewidth=.7,zorder=7)
    planax.text(x,11.8,label,ha='center',fontsize=10,fontweight='bold')
planax.plot([0],[0],'o',color='#273e49',markersize=4,zorder=9)
planax.text(0,-.38,'historical symbolic entrance; aperture / pockets / head UNKNOWN',ha='center',fontsize=7)
planax.set_title('PLAN | actual triangle projection, all six instances',loc='left',fontsize=11)
planax.text(-5.75,11.65,'R070 historical 12 x 12 m outer allocation',ha='left',va='top',fontsize=8)
planax.set_xlim(-6.4,6.4);planax.set_ylim(-.65,12.3);planax.set_aspect('equal');planax.set_xticks(range(-6,7,2));planax.set_yticks(range(0,13,2))
planax.set_xlabel('source X (m)',fontsize=9);planax.set_ylabel('source Y inward (m)',fontsize=9)

def true_section(tris,x):
    segments=[]
    for tri in tris:
        d=tri[:,0]-x
        if np.all(d>1e-8) or np.all(d<-1e-8):continue
        if np.all(np.abs(d)<1e-8):
            segments.extend([tri[[i,(i+1)%3],1:3] for i in range(3)]);continue
        hits=[]
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3];da,db=d[i],d[(i+1)%3]
            if abs(da)<1e-8:hits.append(a[1:3])
            if da*db<0:hits.append((a+(-da/(db-da))*(b-a))[1:3])
        unique=[]
        for p in hits:
            if not any(np.linalg.norm(p-q)<1e-8 for q in unique):unique.append(p)
        if len(unique)>=2:
            pair=max(((a,b) for j,a in enumerate(unique) for b in unique[j+1:]),key=lambda v:np.linalg.norm(v[0]-v[1]))
            if np.linalg.norm(pair[0]-pair[1])>1e-10:segments.append(pair)
    return np.array(segments)

section_meta=[]
for ax,x,ylims,zmax,title in [
    (axA,-4.85,(1.3,5.65),3.25,'A | actual mesh section at source X = -4.85 m'),
    (axB,3.2,(1.65,11.0),1.7,'B | actual mesh section at source X = +3.20 m')]:
    for region in plan['proposed_empty_regions']:
        lo=np.array(region['min_source_m']);hi=np.array(region['max_source_m'])
        if lo[0]<x<hi[0]:
            ax.add_patch(Rectangle((lo[1],0),hi[1]-lo[1],zmax,facecolor=region_colors[region['id']],edgecolor='#91a0a1',linestyle='--',linewidth=.7,zorder=1))
    row={'source_X_m':x,'source_Y_plot_range_m':list(ylims),'source_Z_plot_range_m':[0,zmax],'actual_section_segment_count_by_instance':{}}
    for key,tris in triangles.items():
        segments=true_section(tris,x);row['actual_section_segment_count_by_instance'][key]=len(segments)
        if len(segments):ax.add_collection(LineCollection(segments,colors=palette[key],linewidths=1.0 if 'case' in key else .75,zorder=4))
    ax.axhline(0,color='#273e49',linewidth=1)
    ax.set_xlim(*ylims);ax.set_ylim(-.06,zmax);ax.set_title(title,loc='left',fontsize=10)
    ax.set_xlabel('source Y inward (m)',fontsize=9);ax.set_ylabel('source Z up (m)',fontsize=9)
    section_meta.append(row)
axA.text(1.45,3.1,'Actual cuts through shaped profile, shelves and case',fontsize=8,va='top')
axB.text(1.85,1.6,'Bench case lies off plane B; all three cases are shown in plan',fontsize=8,va='top')
fig.suptitle('Batch18 frozen export evidence | R070 partial source arrangement',fontsize=14,fontweight='bold',color='#273e49')
fig.supxlabel('Colored geometry = decoded frozen GLB meshes. Heavy plan border = historical outer allocation. Dashed fields = new proposed clear bands and pads.\nThe 8.25 m deck allowance is off the section scale; actual local ceiling, host door, support, slots and actor fit remain unknown. No support/contact approval is added here.',fontsize=9,color='#43535a')
png=OUT/'final_actual_geometry_plan_sections.png'
fig.savefig(png,dpi=170)
plt.close(fig)

for r in verified:
    p=CAT/r['path'];assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes']
assert receipt_path.read_bytes()==receipt_bytes and old.read_bytes()==old_bytes

report['schema']='astraea.d09_final_frozen_actual_export_review.v1'
report['generated_utc']=datetime.now(timezone.utc).isoformat()
report['status']='PASS for final frozen source-level arrangement only'
report['final_freeze_confirmed']=True
report['previous_current_snapshot_report']={'file':old.name,'sha256':old_sha,'preserved_byte_for_byte':True}
report['final_freeze']={'receipt_path':str(receipt_path.relative_to(CAT)),'receipt_sha256':receipt_sha,
                      'verified_file_count':18,'verified_files':verified,'verified_again_after_plot':True}
report['main_capture_binding']={'render_evidence_path':str(render_path.relative_to(CAT)),'render_evidence_sha256':sha(render_path),
    'execution_complete':True,'inputs_unchanged_during_execution':True,'four_ordinary_views_recorded':True,
    'plan_script_export_source_and_manifest_hashes_match_freeze':True,
    'limit':'The completed capture and exact input binding are verified from evidence. This review does not add independent pixel/lighting/visual acceptance of the four ordinary views.'}
report['reproducible_scripts']=[{'file':decoder.name,'sha256':sha(decoder),'execution_scope':'Unchanged AST through report construction; final file-write and print expressions excluded to preserve the previous report.'},
                               {'file':Path(__file__).name,'sha256':sha(Path(__file__)),'execution_scope':'18-file freeze check, independent decoder reuse, final rebind and standard plot only.'}]
report['actual_geometry_companion']={'file':png.name,'sha256':sha(png),'pixel_dimensions':[2380,1445],
    'all_six_instances_in_plan':True,'plan_basis':'Projection of actual decoded and transformed referenced triangles, drawn by instance; not nominal bounding boxes.',
    'section_basis':'Exact triangle intersections with the stated source-X planes; no AABB substitutes or imagined interior profiles.',
    'section_planes':section_meta,'historical_outer_allocation_and_proposed_pad_distinction':True,
    'deck_clear_height_limit':'8.25 m historical deck allowance is intentionally outside detail-section scales; no local ceiling fit is certified.',
    'host_or_support_acceptance':False}
report['not_granted']=[s for s in report['not_granted'] if s!='final production freeze']
report['read_only_guarantee']='Only new files under actual_export_review and its cache subdirectories were written. Previous snapshot report, historical handoff, catalogue and all 18 frozen inputs remain unchanged.'
save('final_frozen_actual_export_review.json',report)
save('final_actual_geometry_plan_sections.json',report['actual_geometry_companion'])
save('final_freeze_inputs_verified.json',report['final_freeze'])
save('SHA256_final.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256_final.json'})
print(json.dumps({'status':report['status'],'verified_frozen_files':18,'report':'final_frozen_actual_export_review.json',
                 'report_sha256':sha(OUT/'final_frozen_actual_export_review.json'),'companion':png.name,'companion_sha256':sha(png),
                 'previous_report_unchanged':True,'section_planes':section_meta},indent=2))
