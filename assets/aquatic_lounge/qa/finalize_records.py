"""Label verified actual-GLB media and record the complete family handoff."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size):return ImageFont.truetype(fontpath,size)
qa=ROOT/'qa';render=json.loads((qa/'render_evidence.json').read_text())
initial=json.loads((qa/'initial_rejected/first_render_evidence.json').read_text())
if 'table_detail' not in render['views']:
    assert initial['export_hashes']['AST-AQU-002.glb']==sha(ROOT/'exports/AST-AQU-002.glb')
    render['views']['table_detail']=initial['views']['table_detail']
    render['views']['table_detail']['preserved_identical_table_glb']='Table bytes unchanged by lounger support correction; exact source hash verified.'
render['correction_record']={'table':'Scoped 1 micrometre post-bevel WELD removes nanometre duplicates; metric UV reprojection of evaluated trestle corners. No silhouette change. Initial rejected numerical reports retained.','lounger':'Actual first GLB render exposed flat support crossbars on top of reclined contact panels. Cross supports now rotate to the local reclining slope, stay under contact skin, and remain joined to skin/rails. Replaced family, standing, profile and support-detail renders; 18 actual-GLB BVH clearance rays pass.','rejected_reference':'initial_rejected/contact_support_breakthrough.png'}
(qa/'render_evidence.json').write_text(json.dumps(render,indent=2)+'\n')
captions={
 'family':('AST-AQU-001 + 002 | ACTUAL IMPORTED GLBs','QA studio only | 0.827 x 1.980 m lounger; 0.666 x 0.565 m table'),
 'standing':('AQUATIC LOUNGE | 1.65 m CAMERA','Actual GLBs at 640 x 360 | no room, species, water or physics claim'),
 'profile':('AST-AQU-001 | RECLINING SUPPORT PROFILE','9,960 triangles | four floor grips; open underside; contact zones proposed'),
 'table_detail':('AST-AQU-002 | DRAINED TRAY DETAIL','4,284 triangles | raised rim, 8 mm slots, lower teal channel'),
 'support_detail':('AST-AQU-001 | SLOPE-ALIGNED SUPPORT DETAIL','Actual GLB | cross supports stay below contact skin; intersection checks pass')}
media=[]
for name,(title,caption) in captions.items():
    raw=qa/(name+'_raw.png');im=Image.open(raw).convert('RGB');w,h=im.size
    header=27 if w==640 else 38;footer=24 if w==640 else 34
    out=Image.new('RGB',(w,h),(23,33,37));draw=ImageDraw.Draw(out)
    fit=im.copy();fit.thumbnail((w,h-header-footer),Image.Resampling.LANCZOS);out.paste(fit,((w-fit.width)//2,header+(h-header-footer-fit.height)//2))
    draw.text((10,6),title,font=font(13 if w==640 else 20),fill=(236,239,229));draw.text((10,h-footer+5),caption,font=font(10 if w==640 else 15),fill=(197,211,207))
    dest=qa/(name+'_labelled.png');out.save(dest)
    media.append({'view':name,'file':str(dest.relative_to(ROOT)),'raw':str(raw.relative_to(ROOT)),'size_px':[w,h],'sha256':sha(dest),'source':'Actual imported GLBs; label bands added without geometry/image retouch','scope':'Blender component QA only'})
    if name=='table_detail':
        card=Image.new('RGB',(640,360),(23,33,37));d=ImageDraw.Draw(card);small=im.copy();small.thumbnail((640,309),Image.Resampling.LANCZOS);card.paste(small,((640-small.width)//2,27+(309-small.height)//2));d.text((10,6),title,font=font(13),fill=(236,239,229));d.text((10,341),'Actual GLB downsample | 0.438 m usable stone surface; 0.453 m rim',font=font(10),fill=(197,211,207));card.save(qa/'table_640_labelled.png')
        media.append({'view':'table_640','file':'qa/table_640_labelled.png','raw':'qa/table_detail_raw.png','size_px':[640,360],'sha256':sha(qa/'table_640_labelled.png'),'source':'Aspect-preserving downsample of actual imported-GLB 960x720 render','scope':'640x360 legibility card, not an independent render'})
(qa/'review_media_manifest.json').write_text(json.dumps(media,indent=2)+'\n')
assets=[json.loads(p.read_text()) for p in sorted(ROOT.glob('AST-AQU-*.manifest.json'))]
dependencies=[]
for role in sorted({r for a in assets for r in a['material_roles']}):
    p=next(p for p in (CAT/'materials').rglob('*.png') if p.stem==role)
    dependencies.append({'material_role':role,'texture':str(p.relative_to(CAT)),'sha256':sha(p),'packed_in_source':True,'embedded_in_glb':True})
dep={'shared_standard_sources':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)} for p in [CAT/'standards/materials.py',CAT/'standards/aquatic_materials.py',CAT/'standards/qa_frame.py']],'used_textures':dependencies,'scope':'Existing materials unmodified; six used finish roles across this furniture pair'}
(ROOT/'dependency_manifest.json').write_text(json.dumps(dep,indent=2)+'\n')
summary=[]
for a in assets:
    grips=a['floor_contact_checks']['grips'];xmin=min(g['bounds_min_m'][0] for g in grips);xmax=max(g['bounds_max_m'][0] for g in grips);ymin=min(g['bounds_min_m'][1] for g in grips);ymax=max(g['bounds_max_m'][1] for g in grips)
    a['geometric_support_footprint']={'convex_hull_xy_m':[[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]],'origin_projection_inside':xmin<0<xmax and ymin<0<ymax,'interpretation':'Four floor contacts and geometric support envelope; no center-of-mass, tip or load stability certification'}
    a['verification']={'source_reload':'qa/source_reload_checks.json','actual_glb_binary':'qa/glb_independent_validation.json','support_joins':'qa/join_checks.json','camera_preflight':'qa/camera_preflight.json','actual_glb_media':'qa/review_media_manifest.json','contact_clearance':'qa/actual_glb_contact_clearance.json' if a['catalogue_id']=='AST-AQU-001' else None}
    a['triangle_cost_note']='No LOD supplied or target-PC performance claim. Per-semantic-part costs retained for later profiling-driven reduction; shaped contact panels/rails form most lounger cost, table rim/trestles form most table cost.'
    (ROOT/(a['catalogue_id']+'.manifest.json')).write_text(json.dumps(a,indent=2)+'\n')
    summary.append({k:v for k,v in a.items() if k not in ['parts','join_checks']})
(ROOT/'manifest.json').write_text(json.dumps({'family':'Aquatic lounge furniture','unique_artistic_assets':2,'assets':summary,'evidence':'qa/review_media_manifest.json','scope':'Original independent catalogue; original game remains untouched'},indent=2)+'\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in ['SHA256SUMS.txt'] and p.suffix not in ['.blend1','.log','.pyc'])
(ROOT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in files))
print('FINAL_RECORDS_COMPLETE',len(media),len(files))
