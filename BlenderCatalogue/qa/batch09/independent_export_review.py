"""Independent export and source-to-export checks, from actual files."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'batch07'))
from independent_geometry import Native,SourceCache,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sys.path.insert(0,str(ROOT/'qa'));from inspect_glb_independent import GLB
FAMILIES=['guest_use','library_use']
paths=[Path(x).resolve() for x in sys.argv[1:]] if len(sys.argv)>1 else [p for f in FAMILIES for p in (ROOT/'assets'/f).rglob('*.glb')]
results=[]
for path in sorted(paths):
    try:
        g=GLB(path);row=g.inspect();row['path']=str(path.relative_to(ROOT))
        sourcefiles=[p for p in (ROOT/'assets'/path.relative_to(ROOT/'assets').parts[0]).rglob('*.blend') if p.stem==path.stem]
        if len(sourcefiles)==1:
            audit=OUT/('independent_source_'+path.stem+'.json')
            if audit.exists():
                s=json.loads(audit.read_text());row['source_audit']=str(audit.relative_to(ROOT))
                row['source_audit_current']=hashlib.sha256(sourcefiles[0].read_bytes()).hexdigest()==s['sha256']
                row['source_export_bounds_max_difference_m']=float(max(np.max(np.abs(np.array(row['min_xyz'])-s['bounds_min_m'])),np.max(np.abs(np.array(row['max_xyz'])-s['bounds_max_m']))))
                row['source_evaluated_triangles']=s['evaluated_triangles']
                row['source_export_triangles_equal']=s['evaluated_triangles']==row['triangles']
                srcmat={m['name'] for m in s['used_materials']};glbmat={m['name'] for m in row['materials']}
                row['used_material_names_match']=srcmat==glbmat
                sourceimage={im['packed_sha256']:im for im in s['used_images']}
                exportimage={im.get('embedded_sha256'):im for im in row['images']}
                row['used_source_images_all_packed']=all(im['packed'] for im in s['used_images'])
                row['used_source_vs_glb_texture_bytes_equal']=set(sourceimage)==set(exportimage)
                row['source_image_count']=len(sourceimage);row['glb_image_count']=len(exportimage)
                row['source_has_named_editable_parts']=len([o for o in s['objects'] if o['type'] in {'MESH','CURVE'}])>1
                row['source_modifier_count']=sum(len(o['modifiers']) for o in s['objects'])
                sourcegeom=np.load(ROOT/s['geometry_cache'])['triangles'].reshape(-1,3)
                actualgeom=Native(path).tris.reshape(-1,3)@C
                source_native=SourceCache(audit);export_native=Native(path)
                surface=[]
                for mat in sorted(srcmat):
                    a=source_native.tris[source_native.select(role=mat)];b=export_native.tris[export_native.select(role=mat)]
                    area=lambda t:float(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).sum()/2)
                    volume=lambda t:float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
                    surface.append({'material':mat,'source_triangles':len(a),'export_triangles':len(b),'surface_area_error_m2':abs(area(a)-area(b)),'signed_volume_error_m3':abs(volume(a)-volume(b))})
                row['source_export_surface_metrics']=surface
                row['source_export_tessellation_equivalent']=all(x['surface_area_error_m2']<1e-6 and x['signed_volume_error_m3']<1e-7 for x in surface)
                row['source_export_vertex_hausdorff_m']=float(max(cKDTree(sourcegeom).query(actualgeom)[0].max(),cKDTree(actualgeom).query(sourcegeom)[0].max()))
                if row['source_export_vertex_hausdorff_m']>1e-5:row['issues'].append('Source/export actual evaluated vertex clouds mismatch')
                if row['source_export_bounds_max_difference_m']>1e-5:row['issues'].append('Source/export bounds mismatch')
                for key in ['source_audit_current','source_export_tessellation_equivalent','used_material_names_match','used_source_images_all_packed','used_source_vs_glb_texture_bytes_equal','source_has_named_editable_parts']:
                    if not row[key]:row['issues'].append(key+' failed')
        for n in row['nodes']:
            for prim in n['primitives']:
                if not prim['normals_present']:row['issues'].append(n['name']+': missing normals')
                if not prim['uv_present']:row['issues'].append(n['name']+': missing TEXCOORD_0')
                if prim.get('normal_length_range',[1,1])[0]<.99 or prim.get('normal_length_range',[1,1])[1]>1.01:row['issues'].append(n['name']+': normals are not unit length')
        if not row['triangles']:row['issues'].append('Empty geometry')
        native=Native(path)
        row['native_gltf_bounds_m']={'min':native.tris.reshape(-1,3).min(axis=0).tolist(),'max':native.tris.reshape(-1,3).max(axis=0).tolist()}
        row['node_extras']=[{'index':i,'name':n.get('name'),'extras':n['extras']} for i,n in enumerate(g.doc['nodes']) if n.get('extras')]
        row['runtime_cost']={'triangles':row['triangles'],'mesh_nodes':len([n for n in row['nodes'] if n['mesh_index'] is not None]),'primitives':sum(len(n['primitives']) for n in row['nodes']),'materials':len(row['materials']),'embedded_texture_count':len(row['images']),'glb_bytes':row['byte_size'],'target_gpu_or_engine_accepted':False}
    except Exception as e:row={'path':str(path),'error':repr(e)}
    results.append(row)
    (OUT/('independent_export_'+path.stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({k:row.get(k) for k in ['path','triangles','dimensions_xyz','runtime_cost','issues','error']}))
(OUT/'independent_export_summary.json').write_text(json.dumps(results,indent=2)+'\n')
