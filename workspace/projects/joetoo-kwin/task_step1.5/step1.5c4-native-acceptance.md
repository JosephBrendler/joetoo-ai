# Step 1.5c.4 first-iteration native acceptance

Maintainer-operated on gmki91 X11 and q552u01 Wayland. All new native cases are
NOT TESTED by the agent. Record backend/session, candidate SHA, executable/package
versions, configuration, output, UUIDs and final result for each case.
Use the checkout CLI and its colocated helpers; the POC installer does not install
these new helpers. Keep the accepted compatible broker/resident running. Python3
must provide dbus-python (verified import only in the agent environment).

1. Record actual virtual desktop count and existing desktop IDs/assignments using
   KWin's /VirtualDesktopManager properties. Use a validated test plan whose maximum
   desktop R fits your configured desktop_limit. Sparse references must require R,
   not the number of entries. Verify reported current/required counts.
2. With enough existing desktops, confirm a small local-Dolphin plan: no desktop
   count/ID/assignment changes. Verify exact registered UUID/PID and frame/membership.
3. With a plan requiring extra desktops, decline: no desktops or applications added.
   Then approve: only missing desktops appended before the first application starts;
   existing IDs/order/assignments and displayed desktop remain undisturbed by creation.
4. During confirmation append a desktop manually; approve and verify only the remaining
   shortfall is created. Separately remove/reorder an original desktop while waiting:
   expect safe rejection, no application launch. A KWin/session change must also reject.
5. Test a required count beyond the actual system capacity with an explicit reviewed
   configuration ceiling: expect bounded no-progress/error, zero application launches,
   truthful failure and retained partial desktops. Do not automatically roll back.
6. Dolphin empty target opens HOME; explicit absolute directory, configuration-relative
   directory, directory with spaces and trailing slash resolve as documented. Missing
   directory, regular file, URL/control target reject the complete -o plan before
   confirmation. -c remains offline/descriptive. No expansion of literal ~/$()/variables
   inside a quoted configured target is performed by the path helper.
7. Leave an unrelated Dolphin window open, then run a mixed Dolphin/Konsole plan in
   both file-order permutations. Verify distinct new UUIDs and exact launched PID
   correlation; no adoption/repositioning of the preexisting window. If Dolphin
   delegates or creates ambiguous windows, expect conservative registration failure
   and stop; collect evidence without weakening ownership requirements.
8. Check repeated intended desktop/slot rejection after manually moving Dolphin.
   Check nonblocking competing -o while waiting at confirmation and while provisioning.
   Cancellation/completion must release the lock even with Dolphin/SSH windows alive.
9. Verify existing Konsole local/SSH, offline placeholder and original-Bash behavior.
   Preserve best-effort isolated placement failure and unresolved/ambiguous stopping.

This increment uses existing graphical_* rectangle calculation, not underlay stacking:
record geometry success independently of focus/Z-order. SFTP, VNC, VPN detection,
underlay focus and RDP are excluded. Any native step involving system limits or
session restart is a maintainer decision; existing headless tests cover those failure
paths without requiring disruption of a productive session.
