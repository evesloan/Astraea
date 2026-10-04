"""Read-only geometric probes on actual exported GLB triangles, in Blender metres.

No author helper geometry is used. Support probes require an independently
selected z-height. They check horizontal support, not physics or load capacity.
"""
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspect_glb_independent import GLB


def triangles(path, transform=None):
    glb = GLB(path)
    doc = glb.doc
    rows = []
    def visit(index, parent):
        node = doc['nodes'][index]
        world = parent @ glb.matrix(node)
        if 'mesh' in node:
            for prim in doc['meshes'][node['mesh']]['primitives']:
                vertices = glb.accessor(prim['attributes']['POSITION'])
                p = np.column_stack((vertices, np.ones(len(vertices)))) @ world.T
                p = p[:, [0, 2, 1]]
                p[:, 1] *= -1
                if transform is not None:
                    p = (np.column_stack((p, np.ones(len(p)))) @ transform.T)[:, :3]
                indices = (glb.accessor(prim['indices']).ravel().astype(int)
                           if 'indices' in prim else np.arange(len(p)))
                rows.append({'node': node.get('name'),
                             'role': doc['materials'][prim['material']]['name'],
                             'triangles': p[indices.reshape(-1, 3)]})
        for child in node.get('children', []):
            visit(child, world)
    for root in doc['scenes'][doc.get('scene', 0)]['nodes']:
        visit(root, np.eye(4))
    return rows


def placement(xyz=(0, 0, 0), degrees=0):
    angle = np.deg2rad(degrees)
    c, s = np.cos(angle), np.sin(angle)
    matrix = np.eye(4)
    matrix[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    matrix[:3, 3] = xyz
    return matrix


def contains_xy(points, triangle_set, tolerance=1e-7):
    """Point containment in union of projected triangles, with edge tolerance."""
    points = np.asarray(points)[:, :2]
    t = np.asarray(triangle_set)[:, :, :2]
    covered = np.zeros(len(points), dtype=bool)
    for triangle in t:
        a, b = triangle[1] - triangle[0], triangle[2] - triangle[0]
        determinant = a[0] * b[1] - a[1] * b[0]
        if abs(determinant) < 1e-14:
            continue
        p = points - triangle[0]
        u = (p[:, 0] * b[1] - p[:, 1] * b[0]) / determinant
        v = (a[0] * p[:, 1] - a[1] * p[:, 0]) / determinant
        covered |= (u >= -tolerance) & (v >= -tolerance) & (u + v <= 1 + tolerance)
    return covered


def support_probe(structure_rows, stock_rows, z, tolerance=2e-5):
    """Check every stock projected vertex plus a 2cm grid inside its footprint.

    The all-vertex test detects overhang; actual base-contact vertices are
    reported separately. Grid checks cover solid footprint islands, not a
    bounding rectangle that might span intentional empty space between books.
    """
    structure = np.concatenate([r['triangles'] for r in structure_rows])
    stock = np.concatenate([r['triangles'] for r in stock_rows])
    horizontal = np.ptp(structure[:, :, 2], axis=1) < tolerance
    at_level = np.abs(structure[:, :, 2].mean(axis=1) - z) < tolerance
    support = structure[horizontal & at_level]
    vertices = np.unique(stock.reshape(-1, 3), axis=0)
    lo, hi = vertices.min(0), vertices.max(0)
    xx, yy = np.meshgrid(np.arange(lo[0], hi[0] + .01, .02),
                         np.arange(lo[1], hi[1] + .01, .02))
    grid = np.column_stack((xx.ravel(), yy.ravel()))
    grid = grid[contains_xy(grid, stock)]
    projected_supported = contains_xy(vertices, support)
    grid_supported = contains_xy(grid, support)
    base = vertices[np.abs(vertices[:, 2] - z) < tolerance]
    base_supported = contains_xy(base, support)
    return {'shelf_top_z': z, 'horizontal_support_triangles': len(support),
            'stock_min_xyz': lo.tolist(), 'stock_max_xyz': hi.tolist(),
            'projected_vertices': len(vertices),
            'projected_vertices_unsupported': int((~projected_supported).sum()),
            'unsupported_projected_examples': vertices[~projected_supported][:12].tolist(),
            'interior_grid_spacing_m': .02, 'interior_grid_points': len(grid),
            'interior_grid_points_unsupported': int((~grid_supported).sum()),
            'base_contact_vertices': len(base),
            'base_contact_vertices_unsupported': int((~base_supported).sum()),
            'stock_bottom_to_shelf_m': float(lo[2] - z),
            'scope': 'Static horizontal visual support; no dynamic or load-bearing claim.'}


def vertices_in_box(rows, lower, upper, tolerance=1e-6):
    """Vertex occupancy screen; clear result needs triangle intersection check."""
    lower, upper = np.asarray(lower), np.asarray(upper)
    out = []
    for row in rows:
        p = row['triangles'].reshape(-1, 3)
        inside = ((p > lower + tolerance) & (p < upper - tolerance)).all(axis=1)
        if inside.any():
            out.append({'node': row['node'], 'role': row['role'],
                        'vertices_inside': int(inside.sum()),
                        'examples': p[inside][:8].tolist()})
    return out


def triangles_intersect_box(rows, lower, upper, tolerance=1e-6):
    """Triangle/AABB separating-axis test. Excludes exact boundary touch."""
    center = (np.asarray(lower) + np.asarray(upper)) * .5
    half = (np.asarray(upper) - np.asarray(lower)) * .5 - tolerance
    out = []
    for row in rows:
        hits = []
        for i, triangle in enumerate(row['triangles']):
            tri = triangle - center
            edges = np.roll(tri, -1, axis=0) - tri
            axes = [*np.eye(3), np.cross(edges[0], edges[1])]
            axes.extend(np.cross(edge, unit) for edge in edges for unit in np.eye(3))
            separated = False
            for axis in axes:
                if np.linalg.norm(axis) < 1e-12:
                    continue
                projected = tri @ axis
                radius = np.abs(axis) @ half
                if projected.min() >= radius or projected.max() <= -radius:
                    separated = True
                    break
            if not separated:
                hits.append(i)
        if hits:
            out.append({'node': row['node'], 'role': row['role'],
                        'intersecting_triangles': len(hits), 'first_indices': hits[:12]})
    return out
