# Windows retained-source preparation

MousyLaptop, 2026-10-25, source baseline
`6c52b7a8954af4ac2a33631942501cfcdc5f0eb8`.

The original preparer failed with `OSError(9, 'Bad file descriptor')` at
`os.fsync()` on its private staging candidate opened as `rb`. An isolated
Windows probe reproduced the failure with `rb` and succeeded with `r+b`.
The correction opens only that newly created staging inode with a writable
handle; it does not open existing project survivors for writing. Atomic
no-replace publication, hashes, conflict refusal and source pins are unchanged.

`python recovery/windows_preparation_20261025/test_missing_only.py` passed
on Windows: first publication, zero-write repeat, and preservation/refusal
of a deliberately mismatched survivor. Windows hard-link creation required
normal execution outside the restricted sandbox; no filesystem permissions
or credentials were changed.

The corrected preparer completed with `SOURCE_PREPARATION_PASS`: all 17,927
source-contract entries and 80 canonical repairs matched; 3,161 pinned missing
inputs were created and zero existing files overwritten. Manifest SHA256:
`919d3949654deb32d2389ca7b795a9de296fdc39ed330ec690bea6a6af88298e`.
This is source preparation evidence, not engine import, gameplay, visual or
Windows release acceptance. The older edited checkout and packages remain intact.
