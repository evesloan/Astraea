# Packed-resource count correction

Earlier handoff prose incorrectly stated 32 inherited packed context resources for the two thermal support natives. The authoritative SAVED_ENTRY_VERIFICATION.json reports 8+8=16 original resources across the retained thermal entry natives. Thermal support SAVED_NATIVE_VERIFICATION.json reports 8+9=17 inherited resources. The current thermal recovery SAVED_NATIVE_VERIFICATION.json reports 9+10=19 inherited resources. These are per-native resource instances, not a deduplicated project-wide image census.

Verification receipts, native bytes and their hashes are unchanged. Current prose is corrected; independently published historical documents remain retained with this correction.
