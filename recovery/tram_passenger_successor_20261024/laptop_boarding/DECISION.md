# Boarding prerequisite correction

The first selected-world run passed canonical owner/control checks and583837 actual shape queries across211 moving components. It did not pass boarding or measure motion/FPS. The focused exact retained assembly reproduced the stall with actual W input pressed and the player supported on the station floor; slide contacts were BoardingBarrier_CENTRAL/GateLeaf_LEFT_OUTER and LEFT_INNER.

Source boarding.gd sets phase boarding immediately after request_open(), while lift_gate.gd animates its leaves and stops motion when a character occupies its threshold. The test incorrectly used that phase as fully-open readiness. The corrected test waits for both station/car open_fraction>.999 before walking. Focused003 crosses onto the original vehicle floor with the original player, no changed contacts or safety logic. Production files and all mechanical holds remain unchanged by this test correction. Full selected-world recheck pending.
