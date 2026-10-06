"""Read-only source/GLB failure diagnosis; NOT an acceptance checker.

Requires the parent's coordinated Blender slot. Geometry/UV matching retains
2e-6 limits. Normal discrepancies and the documented exporter round-to-four
effect are measured separately, never accepted by relaxing the keeper.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json,argparse,itertools,datetime
import numpy as np
from export_gate import read_gate,sha,source_unchanged
from verify_exported_sources import source_snapshot
from glb_equivalence import decode
def diagnose(e,a):
    ep=np.asarray(e['positions'],float);eu=np.asarray(e['uvs'],float);en=np.asarray(e['normals'],float);ap=a['positions'];au=a['uvs'];an=a['normals'];assert ep.shape==ap.shape;bins={};size=4e-6
    for i,c in enumerate(ep.mean(axis=1)):bins.setdefault(tuple(np.floor(c/size).astype(int)),[]).append(i)
    available=set(range(len(ep)));mxp=mxu=mxn=mxround=0.;bad=0;examples=[]
    for ai,c in enumerate(ap.mean(axis=1)):
        key=np.floor(c/size).astype(int);matches=[]
        for off in itertools.product([-1,0,1],repeat=3):
            for ei in bins.get(tuple(key+off),[]):
                if ei not in available:continue
                for shift in range(3):
                    p=np.roll(ap[ai],-shift,axis=0);u=np.roll(au[ai],-shift,axis=0);n=np.roll(an[ai],-shift,axis=0);pd=float(np.max(np.linalg.norm(ep[ei]-p,axis=1)));ud=float(np.max(np.abs(eu[ei]-u)))
                    if pd<=2e-6 and ud<=2e-6:matches.append((float(np.max(np.linalg.norm(en[ei]-n,axis=1))),ei,shift,pd,ud,n))
        assert matches,'Actual geometry/UV mismatch at triangle '+str(ai);nd,ei,shift,pd,ud,n=min(matches,key=lambda x:x[0]);available.remove(ei);rounded=np.round(en[ei],4);rounded/=np.linalg.norm(rounded,axis=1)[:,None];rd=float(np.max(np.linalg.norm(rounded-n,axis=1)));mxp=max(mxp,pd);mxu=max(mxu,ud);mxn=max(mxn,nd);mxround=max(mxround,rd)
        if nd>2e-6:
            bad+=1
            if len(examples)<3:examples.append(dict(actual_triangle=ai,source_triangle=ei,position_delta=pd,uv_delta=ud,normal_delta=nd,round4_then_normalize_delta=rd,source_normals=en[ei].tolist(),actual_normals=n.tolist()))
    assert not available;return dict(triangles=len(ep),geometry_and_uv_bijection_at_unchanged_limits=True,max_position_deviation_m=mxp,max_uv_deviation=mxu,max_normal_deviation=mxn,normal_triangles_failing_2e_6=bad,max_round4_renormalized_explanation_deviation=mxround,examples=examples)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--name',default='AST-BOT-003_pool_basal_00');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []);g,plan,qa,source_qa,package,candidate=read_gate();a=next(a for a in plan['assets'] if a['name']==args.name);source=candidate/a['source'];glb=candidate/a['export'];old=sha(glb);spec=json.loads((package/'INPUT_PINS.json').read_text())['material_spec']['materials'];expected,counts,markers=source_snapshot(a,source,spec);actual=decode(glb);rows={}
    for p in actual['primitives']:role=p['node']['extras']['material_role'];rows[role]=diagnose(expected[role],p)
    assert sha(glb)==old;source_unchanged(g,qa);report=dict(status='DIAGNOSTIC_ONLY_NO_ACCEPTANCE',source=str(source),source_sha256=sha(source),glb=str(glb),glb_sha256=old,roles=rows,unchanged_tolerances=dict(position=2e-6,uv=2e-6,normal=2e-6));dest=Path(__file__).resolve().parent/('NORMAL_DIAGNOSTIC_'+a['name']+'_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');dest.write_text(json.dumps(report,indent=2)+'\n');print('DIAGNOSTIC',dest);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
