"""Author the two D18 neck-to-crown galleries against retained receiving surfaces.

No existing asset is edited. Run before Blender; the generated plan is reviewable
source, not evidence of actual-world clearance or structural engineering approval.
"""
import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
PARTS = []
LIGHTS = []


def prism(name, cell, role, corners, lower, upper):
    """Closed XZ quadrilateral with corresponding lower/upper Y values."""
    vertices = [[x, y, z] for level in (lower, upper)
                for (x, z), y in zip(corners, level)]
    PARTS.append(dict(name=name, cell=cell, role=role, vertices=vertices,
                      faces=[[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4],
                             [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]))


def band(name, cell, role, z0, z1, left0, right0, left1, right1,
         low0, low1, high0, high1):
    prism(name, cell, role, [(left0, z0), (right0, z0), (right1, z1), (left1, z1)],
          [low0, low0, low1, low1], [high0, high0, high1, high1])


def box(name, cell, role, x0, x1, y0, y1, z0, z1):
    band(name, cell, role, z0, z1, x0, x1, x0, x1, y0, y0, y1, y1)


def profile(distance, length, end_y):
    # Preserve the full 8 m route: even the narrowest side member starts at X4.02.
    width = 6.8 + (4.32 - 6.8) * min(1.0, distance / 12.0)
    width += (4.18 - 4.32) * max(0.0, 1.0 - (length - distance) / 12.0)
    underside = 110.9 + (end_y - 110.9) * max(0.0, 1.0 - (length - distance) / 24.0)
    return width, underside


def make_gallery(label, sign, end, end_y):
    start = 509.29998779296875  # Actual R009 landing-cap accessor boundary.
    length = start - end
    segments = math.ceil(length / 8.0)
    for i in range(segments):
        d0, d1 = length * i / segments, length * (i + 1) / segments
        z0, z1 = sign * (start - d0), sign * (start - d1)
        w0, h0 = profile(d0, length, end_y)
        w1, h1 = profile(d1, length, end_y)
        cell = f'{label}_{i:02d}'
        # Narrow opaque spine; outboard roof lights keep the long gallery airy.
        band(cell+'_CeilingSpine',cell,'enamel',z0,z1,-2.2,2.2,-2.2,2.2,
             h0,h1,h0+.28,h1+.28)
        for side in (-1, 1):
            tag = cell + ('_Port' if side < 0 else '_Starboard')
            a0,b0 = sorted((side*2.2,side*(w0-.16)))
            a1,b1 = sorted((side*2.2,side*(w1-.16)))
            band(tag+'_RoofGlazing',cell,'glass',z0,z1,a0,b0,a1,b1,
                 h0+.04,h1+.04,h0+.12,h1+.12)
            a0,b0=sorted((side*(w0-.16),side*w0))
            a1,b1=sorted((side*(w1-.16),side*w1))
            band(tag+'_Eave',cell,'metal',z0,z1,a0,b0,a1,b1,h0-.16,h1-.16,h0+.28,h1+.28)
            band(tag+'_ViewGlass',cell,'glass',z0,z1,a0+.04,b0-.04,a1+.04,b1-.04,
                 106.94,106.94,h0-.16,h1-.16)
            band(tag+'_Sill',cell,'metal',z0,z1,a0,b0,a1,b1,106.5,106.5,106.94,106.94)
            # The sole plate receives the existing slab edge below walking level.
            # Its outward cantilever is explicit; engineering capacity is not inferred.
            pa0,pb0=sorted((side*3.82,side*w0))
            pa1,pb1=sorted((side*3.82,side*w1))
            band(tag+'_EdgeSole',cell,'metal',z0,z1,pa0,pb0,pa1,pb1,
                 106.30,106.30,106.5,106.5)
            cz=(z0+z1)/2;cw=(w0+w1)/2;ch=(h0+h1)/2
            x0,x1=sorted((side*(cw-.16),side*cw))
            box(tag+'_Mullion',cell,'metal',x0,x1,106.5,ch+.24,cz-.10,cz+.10)
        # Cassette ribs stay above the full 4 m protected air envelope.
        cz=(z0+z1)/2;cw=(w0+w1)/2;ch=(h0+h1)/2
        box(cell+'_RoofRib',cell,'metal',-cw,cw,ch-.16,ch+.24,cz-.10,cz+.10)
        if i % 3 == 1:
            box(cell+'_FixtureHousing',cell,'metal',-.60,.60,ch-.20,ch,cz-.25,cz+.25)
            box(cell+'_FixtureLens',cell,'lens',-.51,.51,ch-.22,ch-.20,cz-.17,cz+.17)
            LIGHTS.append(dict(id='G7R11_'+cell+'_Source',position=[0,ch-.24,cz],
                               housing=cell+'_FixtureHousing',lens=cell+'_FixtureLens',
                               housing_mesh='G7R11_'+cell+'_metal',lens_mesh='G7R11_'+cell+'_lens'))


def main():
    make_gallery('Fore',-1,181.0,111.0)
    make_gallery('Aft',1,194.0,113.88)
    sources = ['Game/data/generated/structural_meshes.json',
        'Game/data/architecture/GROUP7_COMPLETION.json',
        'Game/data/architecture/BRIDGE_PLATFORM_RUNTIME.json',
        'Game/data/architecture/UPPER_HORIZON_ENCLOSURE_RUNTIME.json']
    sources += ['Game/assets/models/G7_Completion_R009_G7C4_'+end+'_NeckLanding.glb'
                for end in ('Fore','Aft')]
    pins={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in sources}
    plan=dict(schema='astraea.group7.terminal-roof-links.v1',source_pins=pins,
        baseline='30b114f4beb2311a77586d64e566e7ced2d2b7f8',parts=PARTS,lights=LIGHTS,
        protected_route=dict(x=[-4,4],floor_y=106.5,air_top_y=110.5),
        new_room_ids=[],capacity_delta=0,existing_assets_modified=[],
        status='Authored candidate; actual-world interfaces and native/runtime verification pending',
        limits=['No pressure or primary structural capacity acceptance',
                'Existing slab edges receive explicit cantilevered sole plates',
                'No engine, visual, walking or performance acceptance inferred from this plan'])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(parts=len(PARTS),lights=len(LIGHTS),status=plan['status'])))


if __name__ == '__main__':
    main()
