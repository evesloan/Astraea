from pathlib import Path
import bpy,json
P=Path(__file__).parent;T=P/'import/Game';bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.75;return m
stone=mat('Receiving_warm_stone',(.52,.49,.40));steel=mat('Receiving_dark_zinc',(.18,.20,.21));parts=[]
def box(key,name,a,kind):
 x0,x1,y0,y1,z0,z1=a;vs=[(x,-z,y)for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]];fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];mesh=bpy.data.meshes.new(key+'_'+name);mesh.from_pydata(vs,[],[tuple(reversed(f))for f in fs]);mesh.update();obj=bpy.data.objects.new(key+'_'+name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(stone if kind=='floor'else steel);parts.append({'site':key,'name':obj.name,'bounds_xyz':a,'kind':kind})
sites=[{'key':'port_forward_upper_house','x':[ -75,-64],'centre':-69.5,'receiver_root':'TidalGardenReceivingCandidate','receiver_model':'AST-RES-TIDAL_lift_fit_r003.glb','floor_batch':'TG_Batch_82','pier_batch':'TG_Batch_47','guard_batches':['TG_Batch_141','TG_Batch_212'],'mask':[ -70.4,-68.6,101.99,103.16,-384.12,-383.79],'pier_bounds':[-63.67,-63.23,84,106.02,-396.22,-395.78],'source_floor_m2':198.,'pier_void_m2':0.},{'key':'starboard_forward_upper_house','x':[63,74],'centre':69.,'receiver_root':'QuietGroveReceivingCandidate','receiver_model':'QUIET_GROVE_ARCHITECTURE_lift_r003.glb','floor_batch':'QG_Batch_134','pier_batch':'QG_Batch_264','guard_batches':['QG_Batch_146','QG_Batch_147','QG_Batch_151','QG_Batch_154','QG_Batch_155'],'mask':[68.1,69.9,101.99,103.16,-384.12,-383.79],'pier_bounds':[63.21,63.69,84,105.92,-390.24,-389.76],'source_floor_m2':198.,'pier_void_m2':.3364}]
for site in sites:
 k=site['key'];lo,hi=site['x'];c=site['centre']
 rects=[[lo,hi,-404,-386]]if lo<0 else [[63,74,-404,-390.29],[63,74,-389.71,-386],[63,63.16,-390.29,-389.71],[63.74,74,-390.29,-389.71]]
 for i,r in enumerate(rects):box(k,'source_floor_'+str(i),[r[0],r[1],101.76,102,r[2],r[3]],'floor')
 box(k,'missing_connector',[c-.9,c+.9,101.76,102,-386,-384],'floor')
 xs=[lo+.5,c,hi-.5]if lo<0 else [64.5,c,73.5]
 for i,x in enumerate(xs):
  box(k,'longitudinal_'+str(i),[x-.12,x+.12,101.5,101.84,-404,-384.15],'frame')
  box(k,'retained_slab_transfer_'+str(i),[x-.12,x+.12,101.78,101.84,-384.5,-382.5],'slab_bearing')
 for i,z in enumerate([-403.7,-400,-396,-390,-386.25]):box(k,'crossmember_'+str(i),[xs[0]-.12,xs[-1]+.12,101.5,101.84,z-.12,z+.12],'frame')
 if lo<0:
  box(k,'existing_pier_coupling',[-64.6,-63.65,101.9,101.98,-396.15,-395.85],'pier_bearing')
 else:
  box(k,'existing_pier_coupling',[63.67,64.7,101.9,101.98,-390.15,-389.85],'pier_bearing')
 segments=[(lo,-404,hi,-404),(hi,-404,hi,-386),(hi,-386,c+.9,-386),(c+.9,-386,c+.9,-383.83),(c-.9,-383.83,c-.9,-386),(c-.9,-386,lo,-386),(lo,-386,lo,-404)]
 for i,(x0,z0,x1,z1)in enumerate(segments):
  for j,y in enumerate([102.55,103.05]):box(k,'rail_'+str(i)+'_'+str(j),[min(x0,x1)-.03,max(x0,x1)+.03,y-.03,y+.03,min(z0,z1)-.03,max(z0,z1)+.03],'guard')
  count=max(1,int(max(abs(x1-x0),abs(z1-z0))/2+.999))
  for j in range(count+1):
   x=x0+(x1-x0)*j/count;z=z0+(z1-z0)*j/count;box(k,'post_'+str(i)+'_'+str(j),[x-.03,x+.03,101.97,103.08,z-.03,z+.03],'guard')
plan={'base':'f64d79dcc9a2a1bf1fa1e9320a8f01294cc9c16c','sites':sites,'parts':parts,'unchanged_source_floor_proposal_m2':396.,'source_floor_derivative_m2':395.6636,'pier_void_m2':.3364,'missing_connector_m2':7.2,'primary_models_or_piers_changed':False,'structural_capacity_accepted':False};(P/'FORWARD_FRAME_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');bpy.data.texts.new('FORWARD_FRAME_PLAN.json').write(json.dumps(plan,indent=2));out=T/'assets/group2_forward_receiving_20261013/FORWARD_ADJUNCT_FRAMES_r002.glb';out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True);(P/'native').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/FORWARD_ADJUNCT_FRAMES_r002.blend'));print('FORWARD_FRAMES_EXPORTED',len(parts))
