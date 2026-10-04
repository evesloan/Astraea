# Astraea canonical species

Updated 1 October 2026 following the user's explicit replacement roster. This is the current species authority for design, architecture, population, needs, cleaning, dialogue and future story work. It supersedes the previous eight-species roster. The six species are **Koblins, Mantelids, Humans, Baelins, Munkos and Mindos**.

## Confirmed traits

| Species | User-confirmed character and needs |
|---|---|
| Koblins | Small goblinoids; pesky, troublesome and the cheapest of the bunch. Large families; most are cruising space for the first time. No extraordinary needs. |
| Mantelids | Sophisticated insectoids who largely keep to themselves, enjoying the quiet of their cocoons. They make little mess apart from their molting process, which is extremely gruesome. |
| Humans | As expected. |
| Baelins | Beluga-like humanoids with soft gelatinous cartilage instead of bones. They produce gooey, oily trails requiring special cleaners, enjoy baths and require aquatic accommodations. |
| Munkos | Odd four-armed humanoids with an extreme appetite. Respectful enough. |
| Mindos | Artificially intelligent species running on synthetic hardware. Most would consider them robots, but they have recently received rights and acknowledgment as sentient. |

Preserve these traits rather than replacing them with generic personality variation. Individual personalities can exist within them. Humans are explicitly included. Small Koblins are not automatically children; Munko appetite does not imply rudeness; Mindo rights and sentience are established rather than a future question.

## Binding implications and open design

- **Accommodation:** Baelin aquatic compatibility is a hard requirement for represented passengers and crew. Mantelids use quiet cocoons. Koblins have no extraordinary needs. Numeric environmental settings, body dimensions and hardware interfaces are unassigned.
- **Households:** Koblin large families need persistent relationships beyond an individual cabin. Linking adjoining existing three-berth units is a proposal. Do not invent extra beds, a household-size distribution or a species population split.
- **Food and rest:** Munkos have an extreme appetite, but quantity, diet and cadence are undecided. Mindos are synthetic; no charging system, ports, fuel, synthetic food, biological hunger or sleep routine has been approved. A legacy shared meal timer is not new biological canon.
- **Cleaning:** Baelin trails require special cleaners; names, ingredients, dose, prices and treatment stages are open. Mantelid molting is extremely gruesome, overriding the old harmless-only restriction for species residue. Frequency, depiction, privacy, care method and presentation options remain to be designed. Do not sanitize the molt into harmless dust or infer an infection/medical game from it.
- **Dialogue and lore:** Retain first-cruise Koblin experience, Mantelid reserve, Baelin bath enjoyment, respectful Munko appetite, ordinary Humans and Mindo personhood. Specific cultures, accents, political events, legal mechanisms and personal stories are not established. SunCorp and its Dyson-sphere setting remain; no relationship to Mindo rights is invented.
- **Art and animation:** Create original low-poly CRT-dithered bodies for all six species. Check actual body envelopes, Baelin soft-cartilage support, Mantelid cocoon/molt states and Munko four-arm contact. Existing rigs cannot certify these by name alone.

## Capacity and implementation boundary

The accommodation ledger remains **1,000 passenger units and 2,000 passenger berths**, with **400 separate crew berths including the player**. It still comprises 300 standard doubles, 300 family triples, 300 specialty singles and 100 specialty doubles. No demographic allocation is fixed.

The current runtime still contains eight legacy rig/profile indices pending a safe migration. Existing eight habitat/rest families can remain useful **physical room types**, not eight canonical species. Preserve stable room, bed, person, party and incident IDs and current ownership; separate `species_id` from legacy rig and support-profile identifiers. Do not blindly rename an eight-entry array into the new six-name roster, assign species modulo six or claim migrated saves without checks.

Runtime conversion, new assets and specialized mechanics are pending, not delivered by a documentation edit. Historical test logs, screenshots and source references retain their original meanings and do not establish support for the new species. The current priority remains the fully realized ship and autonomous guest/staff life before exact gameplay, questline and storyline development.

## Acceptance

Review all six canonical identities in the real main build. Verify Baelin aquatic homes and cleaner distinction, Mantelid quiet and gruesome-molt specification, Munko four-arm support and appetite service, large Koblin household continuity, and Mindo personhood without invented biology. Preserve exact capacity and persistent state. Clearly label proposed numeric values and unresolved migration choices; do not report legacy eight-rig evidence as six-species acceptance.
