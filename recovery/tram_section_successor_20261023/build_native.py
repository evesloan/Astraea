#!/usr/bin/env python3
"""Run only by the sole engine owner in a NEW background Blender process.

blender --background --python build_native.py -- --output /new/path/Tram_Section_r002.blend

Imports the exact authored GLBs as editable meshes/materials into an empty scene.
This preserves all original .blend files; it is a named derived native successor,
not a claim to have regenerated the original native construction history.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
out=args.output.resolve();assert out.suffix=='.blend'and not out.exists()
assert not bpy.data.filepath,'Run in a new background process; never replace an opened source'
receipt=json.loads((HERE/'runtime_r002/EXPORT_RECEIPT.json').read_text())
for name,pin in receipt['files'].items():
    data=(HERE/'runtime_r002'/name).read_bytes()
    assert len(data)==pin['bytes']and hashlib.sha256(data).hexdigest()==pin['sha256'],name
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in receipt['files']:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(HERE/'runtime_r002'/name))
    collection=bpy.data.collections.new('SECTION_r002'if'SECTION'in name else'BRIDGE_r002_local_hinge')
    bpy.context.scene.collection.children.link(collection)
    for obj in set(bpy.data.objects)-before:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
        obj['source_candidate']='tram_section_successor_20261023/r002'
        obj['production_admitted']=False
for image in bpy.data.images:
    if image.source=='FILE'and not image.packed_file:image.pack()
bpy.context.scene['status']='Unadopted editable source; runtime connected/native visual gates pending'
bpy.context.scene['original_native_retained']='Group4_Port_Successor_002.blend; Group4_Receiving_Module_003.blend; Group4_Completion_Receiving_r002.blend'
bpy.context.scene['reference_coordinates']='Runtime GLBs use Godot X/Y/Z; importer converts to Blender Z-up'
text=bpy.data.texts.new('SOURCE_RECEIPT.json');text.write(json.dumps(receipt,indent=2))
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=True)
print(json.dumps({'native_file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'UNADOPTED_SOURCE'}))
