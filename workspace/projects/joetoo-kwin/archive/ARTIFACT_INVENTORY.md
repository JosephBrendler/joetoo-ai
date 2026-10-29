# joetoo-kwin: historical AI download inventory since Step 1.2

**Prepared:** October 28, 2026. **Status:** recovery index, not active source or instructions.  
**Meaning of available:** The exact named file exists in the current conversation's mounted environment and was verified before constructing the recovery ZIP. Files marked **historical reference only** are names recovered from earlier conversation context, *not* verified downloadable bytes in this session. This may not be an exhaustive account of every earlier attachment.

## A. Verified available original files (included in recovery ZIP)

| Step | Original filename | Notes |
| --- | --- | --- |
| 1.4c | `joetoo-kwin-step1.4c-review-bundle.zip` | Early review package; replaced by corrected bundle |
| 1.4c | `joetoo-kwin-step1.4c-corrected-review-bundle.zip` | Corrected package used in later review |
| 1.4c | `joetoo-kwin-step1.4c.patch` | Early version; do not apply to merged main |
| 1.4c | `joetoo-kwin-step1.4c-download.patch` | Earlier downloadable patch; superseded |
| 1.4c | `joetoo-kwin-step1.4c-corrected.patch` | Corrected proposal; historical only |
| 1.4c | `joetoo-kwin-step1.4c-validation.txt` | Prior isolated validation record |
| 1.4c | `step1.4c-isolated-test-results.txt` | Prior isolated validation record |
| 1.4d | `joetoo-kwin-step1.4d-review-bundle.zip` | Preliminary candidate patch + README/HANDOFF proposals |
| 1.4d | `joetoo-kwin-step1.4d-candidate.patch` | Preliminary candidate; superseded |
| 1.4d | `joetoo-kwin-step1.4d-README-update-proposal.md` | Historical README proposal; superseded by merged code and new handoff |
| 1.4d | `joetoo-kwin-step1.4d-managed-launch-review.zip` | Later managed-launch generator/tests package |
| 1.4d | `joetoo-kwin-managed-launch-files-NEW.zip` | Second copy/version of managed-launch package |
| 1.4d | `apply_step1_4d_managed.py` | Patch generator; also included in managed-launch bundle |
| 1.4d | `joetoo-kwin-managed-launch-generator.txt` | Byte-identical to `apply_step1_4d_managed.py`; alternate name |
| 1.4d | `step1.4d-async-placement-review.zip` | Latest asynchronous placement generator + handoff bundle |
| 1.4d | `make_step14d_async_patch.py` | Latest placement patch generator; merged result is PR #22 |
| 1.4d | `STEP1_4D_ASYNC_PLACEMENT_HANDOFF.md` | Associated review/validation instructions |

**Also generated later during workflow-policy discussion:** `joetoo_step14d_review_and_multiagent_drafts.zip` and contained `joetoo_CLOUD_AGENTS_proposal.md`, `joetoo_LOCAL_AGENTS_proposal.md`, `joetoo_workspace_role_routing_proposal.md`, `joetoo_kwin_step1_4d_review_validation_proposal.md`. These are available in the conversation but **not** included in the joetoo-kwin source/patch recovery archive because they are superseded policy proposals, not application implementation artifacts.

## B. Exact names recalled from prior conversations, NOT present as verified files in this session

These names can help locate the original downloads in historical chats or a filesystem backup. **No new download link is asserted** for any file in this section. Earlier files may have been superseded, and accepted code is already recoverable from Git commits/PRs.

| Step | Historical filenames (recovery not verified) |
| --- | --- |
| 1.3a.1 | `joetoo-kwin-step1.3a.1-review.patch`, `step1_3a1_review.zip`, `step1_3a1_review.txt` |
| 1.3a.2 | `joetoo-kwin-step1.3a.2-review.zip`, `joetoo-kwin-step1.3a.2-review.patch`, `joetoo-kwin-step1.3a.2-review-CORRECTED.zip`, `joetoo-kwin-step1.3a.2-review-CORRECTED.patch` |
| 1.3b.1 | `joetoo-kwin-step1.3b.1-correlation-probe-review.zip`, `joetoo-kwin-step1.3b.1-correlation-probe-review-FIXED.patch` (earlier patch names also referenced without independently verified exact bytes) |
| 1.3b.2 | `joetoo-kwin-step1.3b.2-class-candidates-review.zip`, `joetoo-kwin-step1.3b.2-class-candidates-INCREMENTAL.patch` |
| 1.4a | `joetoo-kwin-step1.4a.patch`, `joetoo-kwin-step1.4a-review.zip`, `joetoo-kwin-step1.4a-patch-only.zip`, `joetoo-kwin-step1.4a-diff.txt`, `joetoo-kwin-step1.4a-review-with-patch.zip` |
| 1.4b | `joetoo-kwin-step1.4b-review.zip`, `joetoo-kwin-step1.4b-REVIEW_NOTES.md`, `joetoo-kwin-step1.4b-premerge-fixes.zip` |
| 1.4d | `joetoo-kwin-step1.4d-HANDOFF.txt` is included **inside** recovered `joetoo-kwin-step1.4d-review-bundle.zip` (not a separately mounted file). |

Additional documentation-review scripts were generated in the same period (`joetoo-kwin-doc-review-bundle.zip`, `joetoo-kwin-doc-review.py`, `joetoo-kwin-doc-review-fixed.py`, `README-preview.md`); no current-session bytes of these have been verified. These are documentation artifacts and should not be conflated with approved source.

## C. Recommended archival handling

- Store *verified originals* under a separate historical area such as `archive/ai-downloads-post1.2/step1.4c/` and `step1.4d/`, retaining filenames and a copy of this manifest. **Do not run or reapply historical patch builders** against current `main`.
- Annotate superseded/failed revisions. Preserve for provenance, not as current installation instructions or agent-authoritative policy.
- Use merged PRs as the canonical record of accepted implementation: #16 (1.3a), #17 (1.3b), #19 (1.4a), #20 (1.4b), #21 (1.4c), #22 (1.4d). No need to reconstruct missing patches merely to recover merged source.
- Do not archive secrets, sensitive host logs, or transient machine-specific state. Review the public ZIP contents before committing to the public repo.
- Future task-scoped generated evidence, generators and notes should first go in `task_step1.5/`, separate from project-root production code; after closure the maintainer chooses which original artifacts merit retention in `archive/`.

## D. Maintainer decision
- Store *verified originals* under the existing archive as peers to former POC, candidate, and step directories
- Such arhives of prior steps following 1.2 will have the form `archive/step1.4c/` and `step1.4d/`
