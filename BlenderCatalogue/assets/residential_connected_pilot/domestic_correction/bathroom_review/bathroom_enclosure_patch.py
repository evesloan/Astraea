"""Additive SOURCE-ONLY prototype correction; never edits a retained asset.

Parent integration: call apply_bathroom_enclosure(ns) immediately after the
retained template has been executed in build_family.author_shell(). Export the
fresh prototype revision in the normal source pipeline. Keep Game adoption held.
Design review: master chapters 6, 21, 32 and inspected intimate/premium reference
pixels support finished opaque privacy thresholds; see REFERENCE_INSPECTION.md.
"""

def apply_bathroom_enclosure(ns):
    bpy, wall, extrusion, datum = (ns[k] for k in ('bpy', 'wall', 'extrusion', 'datum'))
    required = ('SUI_BathPrivacyReturn', 'SUI_BathInnerForward', 'SUI_BathInnerRear',
                'SUI_BathDoorHeader', 'SUI_BathCeiling', 'DATUM_bath_entry',
                'DATUM_bath_vanity', 'DATUM_bath_wc', 'DATUM_bath_shower')
    assert all(bpy.data.objects.get(name) is not None for name in required), 'Retained bathroom geometry contract changed'
    additions = ('SUI_BathEntryCornerClosure', 'SUI_BathDoorHeadStop', 'DATUM_bath_door')
    assert all(bpy.data.objects.get(name) is None for name in additions), 'Apply bathroom correction exactly once'

    # Close the 40 mm slot between entry-jamb endpoint x=-.80 and bath-wall
    # west face x=-.76. The short return overlaps both existing solids, keeps
    # the original wall/entry-door identities, and is behind the sliding leaves.
    wall('SUI_BathEntryCornerClosure', (-.84, .18), (-.70, .18),
         0, 2.60, 2.60, 'ivory_enamel', .12)

    # Match the retained recessed side stops on the non-swing side. This masks
    # the 30 mm header gap AND the leaf's 40 mm top chamfers. The 5 mm planar
    # separation from the closed leaf is preserved throughout its inward swing.
    extrusion('SUI_BathDoorHeadStop',
              [(-.755, 2.36), (-.735, 2.36), (-.735, 3.44), (-.755, 3.44)],
              2.10, 2.25, 'warm_walnut')

    # bath_entry remains an approach datum 50 mm outside the wall center.
    # A dedicated door datum prevents later binding the actual leaf to that
    # approach marker. Retained AST-DOR-001 stays a separate operable component.
    datum('bath_door', (-.70, 2.90, 0))
    return {
        'revision': 'bath_enclosure_source_correction_001',
        'door_asset': 'AST-DOR-001',
        'door_source_xyz': [-.70, 2.90, 0],
        'door_source_yaw_radians': 1.5707963267948966,
        'shared_runtime_controller': 'guest_privacy_door.gd',
        'runtime_verified': False,
        'source_only': True,
        'new_geometry': list(additions[:2]),
        'intentional_leaf_floor_undercut_m': .025,
        'bath_door_head_stop_nominal_leaf_clearance_m': .005,
        'fixed_room_ids_preserved': ['D13-13017', 'D13-13041'],
    }
