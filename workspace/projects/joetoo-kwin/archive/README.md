# Historical joetoo-kwin proof-of-concept archive

These six directories are preserved **without modifying their source files**.
Only their paths change. They remain available for regression evidence and
design provenance, not as the active implementation:

- `joetoo-kwin-poc-0/` — initial resident script and move tests
- `joetoo-kwin-poc-1/` — early bridge/launch protocol tests
- `joetoo-kwin-launch-poc/` — launch and broker demonstrations
- `joetoo-kwin-plan-poc/` — declarative layout planning demonstration
- `joetoo-kwin-ssh-nc-poc/` — earlier SSH connection experiments
- `joetoo-kwin-ssh-rcfile-poc/` — SSH rcfile handoff/return tests

The active OpenRC-supervision development directory is
`../step1.2a-candidate/`. The separately merged Step 1 artifact remains
in `../step1-candidate/` until its accepted components are promoted and that
candidate can be archived in a separately reviewed change.

Going forward: keep only the active developmental candidate in the project
root; after promotion of accepted components to the appropriate root-level
locations, move the former candidate into this archive in a reviewed change.
