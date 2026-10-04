# Cleaning cart and loose-product foundation

This is an initial physical interaction, not final handling or the completed housekeeping loop.

## Controls
- Aim at the actual cart handle, hold RMB and press E to take it
- The cart remains tethered when RMB is released, allowing the ordinary wider view while walking
- Hold RMB and press E again to release the current held object
- Cleaner bottles are individual rigid bodies and use the same focused E pickup/drop convention; raise the view to lift one clear of the tray
- Escape and opening the directory release held objects. Cart walking speed is2 m/s; ordinary walking remains3.1 m/s

The player controller and its existing focus/camera pipeline are extended rather than replaced. Explicit gameplay-input state is shared with the directory; OS pointer capture alone is not a reliable gameplay-state signal in headless tests. The focus blur remains unimplemented.

## Physical model
AST-HSK-005 is an editable Blender cart with open shelves, raised lips, bent handles, frame tubes and four rolling visual wheels. AST-HSK-006 is a loose capped bottle. The staff material library supplies paint, zinc and rubber values.

The cart is an 18 kg rigid body with a low custom centre of mass, compound chassis contacts and simplified spherical caster contacts. Wheels rotate visually; they are not individually jointed rigid bodies. No cart rotation axes are locked. Four 0.45 kg bottles remain separate physical objects, rather than being attached to the cart or player.

The shared tether applies bounded forces at the grip. Damping is relative to the moving hand target; damping against world velocity had made pushing unnecessarily sluggish. The cart has modest lateral rolling resistance. Excessive separation releases the tether. Holding an object never teleports or reparents it onto the camera.

The cart initially parks beside the D13 route at X 85.2, Z −37.3. Parking it inside the measured three-lane arrival had obstructed an existing approach, so it was moved outside that segment. Its stable rebuild identity is custodian_cart_001; four product IDs are distinct. These identities are not yet connected to save serialization.

## Verification scope
Focused checks cover settling with four loose bottles, precise handle selection, unfocused rejection, physical straight travel, load retention, release, individual bottle pickup/drop, directory pause and Escape release. Separate geometric checks use the actual compound cart plus an upper-tray load envelope at 235 poses: both suite entrances, turning space in the street and the D06 Canopy arrival.

Those geometric poses are not a dynamically driven turning test. Full turning feel, loaded lifts/trams, species use, inventory/restocking, product consumption, spills, saving, sound and final art remain unfinished. All 21 aggregate groups passed after integration. A graphical release check initially failed because injected key events were still buffered; flushing the test input and waiting for physics processing verifies the shared grab/release path in-engine. The capture now fails promptly on a rejected cart interaction. This does not certify final handling feel.

The temporary M directory includes the Canopy terrace, Night garden, both fitted suites and the cart starting bay. Its destinations scroll while the Close button remains visible. These are review/temporary travel entries, not completed physical transit.
