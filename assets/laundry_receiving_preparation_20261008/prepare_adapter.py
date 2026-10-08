from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;C=R/'runtime_candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):
 p=C/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
materials=json.loads((R/'FLOOR_MATERIALS.json').read_text());textures=[]
for i,m in enumerate(materials[:2]):
 t=m['textures'][0];p=Path(t['path']);textures.append({'role':['staff_floor','staff_spine'][i],'file':'res://'+str(p.relative_to(C)),'sha256':t['sha256'],'tile_uv_m':m['tile_uv_m']})
names=json.loads((C/'data/architecture/laundry/NODE_NAME_MAP.json').read_text());lights=[{'runtime_name':n['runtime_name'],'source_name':n['source_name'],'energy':.65 if any(k in n['source_name']for k in ['Care','Portal'])else .9,'range_m':6.0 if any(k in n['source_name']for k in ['Care','Portal'])else 8.0,'color':[.78,.88,1.0],'requested_shadow':True}for n in names if n['light_index']is not None]
meta=json.loads((C/'data/architecture/laundry/BINARY_PRESERVATION.json').read_text());manifest={'programme':'D01_directory_03','historical_alias':None,'root_name':'D01_Laundry_Receiving_WIP','model_file':'WP08_laundry_runtime_names001.glb','runtime_sha256':meta['runtime_sha256'],'source_sha256':meta['source_sha256'],'placement':[0,0,0],'source_light_count':28,'floor_owners':['D01_laundry_floor','D01_laundry_entry'],'textures':textures,'lights':lights,'operational_acceptance':False,'scope':'Source geometry preserved. Local light-unit/range adaptation and parent floor finish. Care cupboards remain unstocked; no laundry throughput, machine operation, restocking, cart or final art acceptance.'};assert len(lights)==28
put('data/architecture/laundry/runtime_manifest.json',json.dumps(manifest,indent=2)+'\n')
put('shaders/laundry_receiving_finish.gdshader','''shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
varying vec2 ship_xz;
uniform sampler2D staff_floor:source_color,filter_nearest_mipmap,repeat_enable;
uniform sampler2D staff_spine:source_color,filter_nearest_mipmap,repeat_enable;
void vertex(){ship_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;}
void fragment(){
 float u=ship_xz.x+54.0;float v=ship_xz.y+250.0;
 vec2 uv=vec2(ship_xz.x,-ship_xz.y);
 ALBEDO=texture(staff_floor,uv/0.8).rgb;ROUGHNESS=0.87;
 if(u>=0.24&&u<=45.76&&v>=30.0&&v<=38.0){ALBEDO=texture(staff_spine,uv).rgb;ROUGHNESS=0.78;}
 if(u>=1.0&&u<=45.5&&((v>=30.1&&v<=30.25)||(v>=37.75&&v<=37.9))){ALBEDO=vec3(0.84,0.70,0.36);ROUGHNESS=0.8;}
}
''')
s=Path('/workspace/scratch/375c2e438292/night_table_receiving_20261008/runtime_candidate/scripts/night_table_receiving.gd').read_text().replace('night_table','laundry').replace('NightTableSource','LaundrySource').replace('Vector3(-31,61,216)','Vector3.ZERO').replace(';root.set_meta("source_dining_places",240)','').replace(';root.set_meta("historical_alias",str(data.historical_alias))','')
put('scripts/laundry_receiving.gd',s);print('Prepared source-preserved Laundry adapter, 28 bounded mounted lights and source-derived staff floor/spine/line finish')
