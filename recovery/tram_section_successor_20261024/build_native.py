#!/usr/bin/env python3
"""Sole engine owner's optional immutable native authoring invocation.

blender --background --python build_native.py -- --output NEW/Tram_Section_20261024_r002.blend

Editable derived successor, not a replacement of any original native revision.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];SOURCE=ROOT/'Game/tram_section_successor_20261024'
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=args.output.resolve()
assert out.suffix=='.blend'and not out.exists()and not bpy.data.filepath
contracts=json.loads((SOURCE/'CONTRACTS.json').read_text())
for name in ['section_r002.glb','bridge.glb']:
    assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==contracts['owned']['res://tram_section_successor_20261024/'+name]
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ['section_r002.glb','bridge.glb']:
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(SOURCE/name))
    collection=bpy.data.collections.new('SECTION_20261024_r002'if name.startswith('section')else'CENTRAL_bridge_local_hinge_unchanged')
    bpy.context.scene.collection.children.link(collection)
    for obj in set(bpy.data.objects)-before:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj);obj['source_candidate']='tram_section_successor_20261024/r002';obj['production_admitted']=False
for image in bpy.data.images:
    if image.source=='FILE'and not image.packed_file:image.pack()
bpy.context.scene['status']='Named source candidate; structural, installed-world, loaded passenger and visual acceptance unfinished'
bpy.context.scene['coordinates']='GLB is Godot Y-up; Blender importer converts to Z-up. Bridge retains local hinge origin.'
bpy.context.scene['original_native_preserved']='All 20261009-20261023 native/source revisions'
text=bpy.data.texts.new('SOURCE_CONTRACTS.json');text.write(json.dumps(contracts,indent=2))
out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=True)
print(json.dumps({'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'accepted':False}))
