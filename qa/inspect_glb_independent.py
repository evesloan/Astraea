#!/usr/bin/env python3
"""Independent, read-only GLB structural/geometry checks for catalogue QA.

This reads actual exported bytes, not authoring helper results. It is not a full
Khronos validator and makes no engine, collision, performance, or room-fit claim.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import numpy as np
from PIL import Image

DTYPES = {5120: '<i1', 5121: '<u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
COMPONENTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}


class GLB:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        magic, version, length = struct.unpack_from('<4sII', self.data)
        assert magic == b'glTF' and version == 2 and length == len(self.data), 'GLB header invalid'
        offset, chunks = 12, {}
        while offset < len(self.data):
            size, kind = struct.unpack_from('<I4s', self.data, offset)
            offset += 8
            chunks[kind] = self.data[offset:offset + size]
            offset += size
        self.doc = json.loads(chunks[b'JSON'])
        self.bin = chunks.get(b'BIN\0', b'')

    def accessor(self, index):
        a = self.doc['accessors'][index]
        assert 'sparse' not in a, 'Sparse accessor needs separate validator'
        v = self.doc['bufferViews'][a['bufferView']]
        assert v.get('buffer', 0) == 0, 'External buffer not handled'
        typ = np.dtype(DTYPES[a['componentType']])
        n = COMPONENTS[a['type']]
        offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = v.get('byteStride', typ.itemsize * n)
        assert offset + max(0, a['count'] - 1) * stride + n * typ.itemsize <= len(self.bin)
        arr = np.ndarray((a['count'], n), dtype=typ, buffer=self.bin, offset=offset, strides=(stride, typ.itemsize)).copy()
        if a.get('normalized') and a['componentType'] != 5126:
            info = np.iinfo(typ)
            arr = np.maximum(arr.astype(float) / info.max, -1)
        return arr

    def matrix(self, node):
        if 'matrix' in node:
            return np.array(node['matrix'], float).reshape(4, 4).T
        t = np.array(node.get('translation', [0, 0, 0]), float)
        s = np.array(node.get('scale', [1, 1, 1]), float)
        x, y, z, w = node.get('rotation', [0, 0, 0, 1])
        r = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                      [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                      [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
        m = np.eye(4); m[:3, :3] = r @ np.diag(s); m[:3, 3] = t
        return m

    def inspect(self):
        d = self.doc
        result = {'path': str(self.path), 'sha256': hashlib.sha256(self.data).hexdigest(),
                  'byte_size': len(self.data), 'generator': d.get('asset', {}).get('generator'),
                  'extensions_used': d.get('extensionsUsed', []), 'images': [], 'materials': [],
                  'nodes': [], 'issues': [], 'measurement_frame': 'Blender Z-up metres: (glTF x, -glTF z, glTF y)'}
        for im in d.get('images', []):
            row = {'name': im.get('name'), 'mimeType': im.get('mimeType'), 'embedded': 'bufferView' in im}
            if 'bufferView' in im:
                v = d['bufferViews'][im['bufferView']]
                b = self.bin[v.get('byteOffset', 0): v.get('byteOffset', 0)+v['byteLength']]
                with Image.open(io.BytesIO(b)) as img:
                    row.update(size=list(img.size), mode=img.mode)
                row['embedded_sha256'] = hashlib.sha256(b).hexdigest()
            else:
                row['uri'] = im.get('uri'); result['issues'].append('Image is not embedded')
            result['images'].append(row)
        for mat in d.get('materials', []):
            pbr = mat.get('pbrMetallicRoughness', {})
            row = {'name': mat.get('name'), 'base_color_texture': pbr.get('baseColorTexture'),
                   'metallic': pbr.get('metallicFactor', 1), 'roughness': pbr.get('roughnessFactor', 1),
                   'double_sided': mat.get('doubleSided', False)}
            if row['base_color_texture']:
                texture = d['textures'][row['base_color_texture']['index']]
                row['image_index'] = texture.get('source')
                assert row['image_index'] < len(result['images'])
            result['materials'].append(row)
        nodes = d.get('nodes', [])
        scene = d.get('scenes', [{}])[d.get('scene', 0)]
        bounds, total_triangles = [], 0
        def visit(index, parent, ancestors):
            nonlocal total_triangles
            assert index not in ancestors, 'Node hierarchy cycle'
            node = nodes[index]
            world = parent @ self.matrix(node)
            det = float(np.linalg.det(world[:3, :3]))
            row = {'name': node.get('name', str(index)), 'index': index, 'mesh_index': node.get('mesh'),
                   'transform_determinant': det, 'local_translation': node.get('translation', [0, 0, 0]),
                   'local_scale': node.get('scale', [1, 1, 1]), 'primitives': []}
            if 'mesh' in node:
                for p in d['meshes'][node['mesh']]['primitives']:
                    assert p.get('mode', 4) == 4, 'Nontriangle primitive'
                    attrs = p['attributes']; pos = self.accessor(attrs['POSITION']).astype(float)
                    assert np.isfinite(pos).all(), 'Nonfinite position'
                    world_pos = np.column_stack((pos, np.ones(len(pos)))) @ world.T
                    xyz = world_pos[:, [0, 2, 1]]; xyz[:, 1] *= -1
                    bounds.append(xyz)
                    indices = self.accessor(p['indices']).ravel().astype(int) if 'indices' in p else np.arange(len(pos))
                    assert len(indices) % 3 == 0 and indices.min() >= 0 and indices.max() < len(pos)
                    tris = indices.reshape(-1, 3); tri_pos = world_pos[tris, :3]
                    cross = np.cross(tri_pos[:,1]-tri_pos[:,0], tri_pos[:,2]-tri_pos[:,0])
                    areas = np.linalg.norm(cross, axis=1)/2
                    total_triangles += len(tris)
                    prim = {'material': result['materials'][p['material']]['name'] if 'material' in p else None,
                            'vertices': len(pos), 'triangles': len(tris), 'min_xyz': xyz.min(axis=0).tolist(),
                            'max_xyz': xyz.max(axis=0).tolist(), 'degenerate_triangles': int((areas < 1e-12).sum()),
                            'signed_volume_m3': float(np.einsum('ij,ij->i', tri_pos[:,0], np.cross(tri_pos[:,1], tri_pos[:,2])).sum()/6),
                            'normals_present': 'NORMAL' in attrs, 'uv_present': 'TEXCOORD_0' in attrs}
                    if 'NORMAL' in attrs:
                        normals = self.accessor(attrs['NORMAL']).astype(float)
                        assert np.isfinite(normals).all(), 'Nonfinite normal'
                        prim['normal_length_range'] = [float(x) for x in (np.linalg.norm(normals,axis=1).min(),np.linalg.norm(normals,axis=1).max())]
                        normals = normals @ np.linalg.inv(world[:3,:3])
                        face_normal = normals[tris].mean(axis=1)
                        cosine = np.einsum('ij,ij->i', cross, face_normal) / np.maximum(np.linalg.norm(cross,axis=1)*np.linalg.norm(face_normal,axis=1),1e-20)
                        prim['winding_normal_opposed_triangles'] = int(((cosine < -1e-5) & (areas > 1e-12)).sum())
                        prim['winding_normal_cosine_min'] = float(cosine[areas > 1e-12].min()) if (areas > 1e-12).any() else None
                    if 'TEXCOORD_0' in attrs:
                        uv = self.accessor(attrs['TEXCOORD_0']).astype(float)
                        assert np.isfinite(uv).all(), 'Nonfinite UV'
                        prim['uv_min'] = uv.min(axis=0).tolist(); prim['uv_max'] = uv.max(axis=0).tolist()
                        tri_uv = uv[tris]
                        delta_a, delta_b = tri_uv[:,1]-tri_uv[:,0], tri_uv[:,2]-tri_uv[:,0]
                        uv_area = np.abs(delta_a[:,0]*delta_b[:,1]-delta_a[:,1]*delta_b[:,0])/2
                        collapsed = (uv_area < 1e-12) & (areas > 1e-12)
                        prim['collapsed_uv_triangles'] = int(collapsed.sum())
                        prim['collapsed_uv_surface_m2'] = float(areas[collapsed].sum())
                        prim['total_surface_m2'] = float(areas.sum())
                    for k in ('degenerate_triangles','winding_normal_opposed_triangles'):
                        if prim.get(k): result['issues'].append(f"{row['name']}: {k}={prim[k]}")
                    if prim.get('collapsed_uv_surface_m2', 0) > max(1e-4, prim.get('total_surface_m2', 0)*1e-3):
                        result['issues'].append(f"{row['name']}/{prim['material']}: substantial collapsed texture UV area {prim['collapsed_uv_surface_m2']:.6f} m²")
                    if det <= 0: result['issues'].append(f"{row['name']}: nonpositive transform determinant")
                    row['primitives'].append(prim)
            result['nodes'].append(row)
            for child in node.get('children', []): visit(child, world, ancestors | {index})
        for root in scene.get('nodes', []): visit(root, np.eye(4), set())
        if bounds:
            allpos = np.concatenate(bounds)
            result['min_xyz'] = allpos.min(axis=0).tolist(); result['max_xyz'] = allpos.max(axis=0).tolist()
            result['dimensions_xyz'] = (allpos.max(axis=0)-allpos.min(axis=0)).tolist()
            result['vertices_at_z0'] = int((np.abs(allpos[:,2]) < 1e-6).sum())
        result['triangles'] = total_triangles
        result['scope'] = 'Exported visual geometry/material check only. No engine/physics/performance/whole-room proof.'
        return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('root', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reports = []
    for path in sorted(args.root.rglob('*.glb')):
        try: reports.append(GLB(path).inspect())
        except Exception as exc: reports.append({'path': str(path), 'error': repr(exc)})
    args.output.write_text(json.dumps(reports, indent=2) + '\n')
    print(json.dumps([{'asset': Path(r['path']).stem, 'dimensions_xyz': r.get('dimensions_xyz'), 'triangles':r.get('triangles'), 'issues':r.get('issues'), 'error':r.get('error')} for r in reports], indent=2))


if __name__ == '__main__': main()
