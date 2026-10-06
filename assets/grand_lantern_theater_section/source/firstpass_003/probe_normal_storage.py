import bpy,numpy as np,json
from pathlib import Path
R=Path(__file__).resolve().parent;E=R/'exports_run002';A=np.load(E/'source_triangle_attributes.npz');name='C005_P_0942';xyz=A[name+'_xyz'].reshape(-1,3);norm=A[name+'_normal'].reshape(-1,3)
# Native XYZ -> Blender XYZ, same mesh reconstruction and split-normal setter.
v=xyz[:,[0,2,1]].copy();v[:,1]*=-1;n=norm[:,[0,2,1]].copy();n[:,1]*=-1
m=bpy.data.meshes.new('NORMAL_STORAGE_WITNESS');m.from_pydata(v,[],np.arange(len(v)).reshape(-1,3).tolist());m.update()
for p in m.polygons:p.use_smooth=True
m.normals_split_custom_set(n.tolist());actual=np.array([x.vector[:]for x in m.corner_normals]);delta=np.max(abs(actual-n),axis=1);idx=int(np.argmax(delta));report={'source_batch':name,'pre_export_max_custom_normal_storage_error':float(delta.max()),'loop_index':idx,'intended':n[idx].tolist(),'stored':actual[idx].tolist(),'scope':'Reproduces intermediary custom-normal storage loss before glTF export; no source file opened or saved'}
f=R/'NORMAL_STORAGE_DIAGNOSIS.json';assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
