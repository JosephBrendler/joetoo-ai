# Iteration 7: retain before/after detail after the notice result

The Iteration 6 CLI already calls report_action (which calls handle_result) to
finish the notice-level verification announcement, then calls a separate
`j_msg "-${info}" -p "$_wr_status"` with the complete successful broker result.
This retains window identity and before/after desktop/geometry data. The installed
header wraps long detail to the terminal width. Failures remain at error severity.
No further production-code edit was needed for this clarification.

Added an installed-header regression confirming that the detail follows the
completed notice block, is hidden at ordinary verbosity, and is visible with
environment verbosity=6 or DEBUG=0 (the joetoo TRUE value). The environment forms
using $info/$TRUE require those variables to be defined in the invoking shell.
Existing -v/-q work before -m, e.g. `./joetoo-kwin -v -m 2`; trailing options are
still move operands. No grammar extension was made.

22 focused CLI tests passed, including real installed-header integration.
Bash syntax and whitespace checks passed. The full regression from Iteration 6
was not repeated because this iteration changes tests and evidence only.
The focused patch is relative to Iteration 6, whose source/evidence are preserved.
No native operations, staging, commit, push, deployment or protected writes.
