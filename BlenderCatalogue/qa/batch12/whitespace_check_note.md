# Staged whitespace check

The full staged whitespace check reports only terminal blank lines in three preserved source-only stdout logs: assets/clinical_support/qa/source_only_build.log, source_only_check_sources.py.log and source_only_validate_glb.py.log. Their exact bytes are already bound by the independent rebuild receipts and remain unchanged. The source/document check excluding raw `.log` evidence passes. No production code or document whitespace error is being exempted.
