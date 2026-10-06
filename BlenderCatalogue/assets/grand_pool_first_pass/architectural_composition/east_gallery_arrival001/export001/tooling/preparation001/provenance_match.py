"""Architecture keeper matcher reused with correspondence reporting added.
Candidate search, cyclic winding, complete bipartite matching and all attribute
limits are unchanged. The appended map makes each exported triangle traceable.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from check_glb import np, cKDTree, csr_matrix, maximum_bipartite_matching, require, POSITION_LIMIT, NORMAL_LIMIT, LOCAL_LIMIT

def match_with_provenance(expected,actual,check_local=True):
    ep,ap=expected['positions'],actual['positions'];eu,au=expected['uvs'],actual['uvs'];en,an=expected['normals'],actual['normals']
    require(ep.shape==ap.shape and eu.shape==au.shape and en.shape==an.shape,'Triangle/corner cardinality differs')
    require(ep.ndim==3 and ep.shape[1:]==(3,3),'Invalid triangle shape')
    n=len(ep);tree=cKDTree(ep.mean(axis=1));candidates=tree.query_ball_point(ap.mean(axis=1),r=POSITION_LIMIT)
    rows=[];cols=[];measurements={}
    for ai,possible in enumerate(candidates):
        for ei in possible:
            for shift in range(3):
                p=np.roll(ap[ai],-shift,axis=0);pd=float(np.max(np.linalg.norm(ep[ei]-p,axis=1)))
                if pd>POSITION_LIMIT:continue
                # UV export flips V and stores float32. Test the exact representable
                # result, rather than applying a broad UV epsilon at large UV values.
                uv=np.roll(au[ai],-shift,axis=0);expected_uv=eu[ei].astype(np.float32).astype(float)
                ud=float(np.max(np.abs(eu[ei]-uv)))
                if not np.array_equal(expected_uv,uv):continue
                nd=float(np.max(np.linalg.norm(en[ei]-np.roll(an[ai],-shift,axis=0),axis=1)))
                if nd>NORMAL_LIMIT:continue
                ld=0.
                if check_local:
                    ld=float(np.max(np.abs(expected['local_positions'][ei]-np.roll(actual['local_positions'][ai],-shift,axis=0))))
                    if ld>LOCAL_LIMIT:continue
                rows.append(ai);cols.append(ei);measurements[(ai,ei)]=(pd,ud,nd,ld,shift);break
        require(len(rows)>0 and rows[-1]==ai,'No cyclic-winding full-attribute source triangle for exported triangle '+str(ai))
    graph=csr_matrix((np.ones(len(rows),dtype=np.int8),(rows,cols)),shape=(n,n))
    match=maximum_bipartite_matching(graph,perm_type='column')
    require(len(match)==n and np.all(match>=0) and len(set(match))==n,'No complete triangle bijection; duplicated/lost topology')
    vals=[measurements[(ai,int(ei))] for ai,ei in enumerate(match)]
    return {'triangles':n,'corner_count':n*3,'max_position_deviation_m':max(v[0] for v in vals),
            'max_uv_float32_rounding':max(v[1] for v in vals),'max_normal_deviation':max(v[2] for v in vals),
            'max_local_coordinate_deviation_m':max(v[3] for v in vals),'local_coordinates_checked':check_local,
            'triangle_correspondence':[{'export_triangle':ai,'source_triangle':int(ei),'corner_cyclic_shift':measurements[(ai,int(ei))][4]} for ai,ei in enumerate(match)],
            'complete_bijection':True,'cyclic_winding_preserved':True,'uvs_exact_float32_export':True}
