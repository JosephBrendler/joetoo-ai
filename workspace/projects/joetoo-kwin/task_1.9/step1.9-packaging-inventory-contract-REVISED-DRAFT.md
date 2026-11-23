# Step 1.9 — joetoo-kwin 0.1.0 source-release and Gentoo packaging contract

**REVISED DRAFT — maintainer decisions incorporated, 2026-11-20**  
**Accepted development baseline:** `JosephBrendler/joetoo-ai`, `main` at `0ec0234e589ce2b42bbfcfb6ebcec0207b627d60` (PR #34).  
**Intended first Portage package:** **`dev-util/joetoo-kwin-0.1.0`**.  
**No code, repository, package, tarball, host, or live user configuration has been modified by this review.**

This supersedes the earlier *Step 1.9 — Version 1 packaging inventory and installation contract (DRAFT)*, retaining the full functional file inventory and incorporating later decisions on source-release metadata, the native C++ binary boundary, feature dependencies, and the Plasma 6.8 transition. “Approved” below means a decision **stated by the maintainer in the review**, subject to the indicated verification—not permission for an AI agent to write to either protected repository. `joetoo` and `joetoo-upstream` have advisory-only AI policies; their human maintainer carries out integration, `tarup`, ebuild execution and publication.

## 1. Release model — two phases, not direct joetoo-ai-to-host deployment

```text
joetoo-ai (accepted development baseline + Step 1.9 candidate corrections)
        |
        | Human review and integration, after config/source cleanup
        v
joetoo-upstream/dev-util/joetoo-kwin/
   complete sources, CMake/native sources, README/config documentation,
   COPYRIGHT.exceptions, LICENSES.package, attribution and release metadata
        |
        | Human runs tarup from joetoo-upstream/dev-util
        v
joetoo-upstream/dev-util/joetoo-kwin-0.1.0.tbz2
   internal root: joetoo-kwin/
   includes copied root LICENSE and LICENSES/<SPDX-ID>.txt texts
        |
        | Human builds/validates Portage metadata and install-image
        v
joetoo/dev-util/joetoo-kwin/joetoo-kwin-0.1.0.ebuild
   EAPI=8, inherit joetoo_license, joetoo_license_src_install
        |
        | Human review, merge/emerge and native install smoke tests
        v
production Gentoo systems (files owned by Portage, no HOME mutations)
```

### Phase 1 — source stabilization, human upstream integration and `tarup`

1. **Within `joetoo-ai` (reviewable candidate):** normalize and document the *existing* service-vs-launch config roles, repair working first-use examples and the `eselect` path instructions, resolve installed helper locations without source-tree regression, and build the complete source-release file manifest. Keep Step 1.7 behavior intact.
2. **Human integrates approved source into `joetoo-upstream/dev-util/joetoo-kwin/`**, retaining source permissions and references; do not copy the entire development/archive workspace blindly. Include native sources and build files, runtime helpers, templates, documentation and attributable licensing metadata. Decide whether tests are shipped as release sources (recommended: focused tests, not historical console transcripts).
3. Add **`COPYRIGHT.exceptions`** and **`LICENSES.package`** to the source directory. Audit all shipped source files' copyright headers and provenance; do not put a source file on the exception list merely to suppress an inconvenient error. Source files from Gentoo or other third parties require correct separate attribution/license handling.
4. Run `tarup` as the ordinary human user **from `~/joetoo-upstream/dev-util`**. Actual tool: [`dev-util/joetoolkit/devtools/tarup`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/joetoolkit/devtools/tarup). Its first-release version is 0.0.0 when no matching archive exists; thus `tarup joetoo-kwin -minor` creates **`joetoo-kwin-0.1.0.tbz2`**. This depends on *no preexisting matching release archive*; inspect the category directory first. `tarup` requires the current SPDX list over the network, performs copyright checks, stages licensing, and prompts before creating the archive. Do **not** execute it from `joetoo-ai` or run it as root.
5. Verify archive contents with `tar -tjf joetoo-kwin-0.1.0.tbz2`: all paths rooted at `joetoo-kwin/`; `LICENSE`, `LICENSES.package`, `COPYRIGHT.exceptions`, `LICENSES/*.txt` and every required source/document present. Verify `tarup` success and provenance/metadata before starting Phase 2. Keep the tarball in `joetoo-upstream/dev-util/`, not inside the ebuild directory.

**Project-root release metadata created for review:** `COPYRIGHT.exceptions` and `LICENSES.package` belong in the *curated* `joetoo-upstream/dev-util/joetoo-kwin/` source root, and are drafted in the `joetoo-ai` project root by this change. They remain **provisional** until the full curated-source audit: the former exempts its own metadata files and a comment-incompatible JSON plugin metadata file, and the latter currently lists `GPL-3.0-or-later`. Ordinary CMake/source/docs files without a valid copyright header require correction before `tarup`, not blanket exclusions. The `eselect` module's licensing is based on an actual source comparison, which found framework conventions but no substantial matching Gentoo-authored implementation sequence. Its GPL-3.0-or-later header is retained with a Gentoo API acknowledgment and AI-assistance disclosure.

**License mechanics verified in current source:** `tarup` reads **nonblank/non-comment SPDX IDs** from `LICENSES.package`, validates each identifier against the current SPDX list, copies the `joetoo-upstream/LICENSE` into the staged root, and copies `joetoo-upstream/LICENSES/<ID>.txt` into staged `joetoo-kwin/LICENSES/`. `COPYRIGHT.exceptions` contains **package-relative `./path` names** exempting valid non-copyright-bearing inputs from the script's per-file copyright check. `tarup` checks current ending copyright years and may prompt for a human correction/skip. The installed eclass does **not** read `LICENSES.package` itself: it copies the staged root `LICENSE` and all staged `LICENSES/` files into `/usr/share/licenses/${PN}/` and `/usr/share/licenses/${PN}/LICENSES/`. These licensing texts are selected from the **full distributed source**, not conditioned on USE flags.

**Example `LICENSES.package` content (provisional, not a completed provenance audit):**

```text
# SPDX texts required for the complete joetoo-kwin source archive.
# Replace the list only after reviewing every included source and any derivations.
GPL-3.0-or-later
# add GPL-2.0-or-later or other SPDX IDs only when source provenance requires them
```

Do not infer a final ebuild `LICENSE` field from this example. The maintained `joetoolkit` source's licensing metadata includes an additional `GPL-2.0-or-later` attribution for an adapted `eselect` component; **audit the joetoo-kwin selector's actual provenance** before choosing its final identifiers and Portage `LICENSE` expression. The `COPYRIGHT.exceptions` list must cover its own metadata files and any justified noncopyright material; normal source, code, `.md` manuals and `.conf` examples should have appropriate headers/comments.

**Specific `tarup` considerations:** it has a current hardcoded SPDX-list count ceiling and needs working network access to `spdx.org`; if those checks fail, address the actual tool/release blocker by the human maintainer rather than silently bypassing validation. The archive created by tarup has the *unversioned* internal top-level `joetoo-kwin/`, matching the package convention `S="${WORKDIR}/${PN}"`.

### Phase 2 — `joetoo` Portage package and production integration

- Human creates/maintains `joetoo/dev-util/joetoo-kwin/joetoo-kwin-0.1.0.ebuild` plus `Manifest`, `metadata.xml`, and any required `files/` assets. No production ebuild is claimed to exist yet.
- Follow the established source URI pattern: `https://raw.githubusercontent.com/JosephBrendler/joetoo-upstream/master/${CATEGORY}/${PN}-${PV}.tbz2` (after the archive is published). Set `S="${WORKDIR}/${PN}"`, `EAPI=8`, `inherit joetoo_license` (and applicable KDE/CMake/Python eclasses subject to final ebuild review).
- Include **`joetoo_license_src_install`** in the ebuild's real `src_install()` **after source unpack** so the image includes root `LICENSE` and every staged SPDX text. The two metadata files are release inputs, not substitutes for installed texts.
- Build/install the matching native KWin plugin(s) from the source archive, stage all runtime files, global/user service files and docs; preserve Portage config protection for installed `/etc` files.
- Keep `DEPEND`, `BDEPEND`, `RDEPEND`, `REQUIRED_USE`, `IUSE`, version/ABI relationships and keywording explicit and accurate. Do not copy `joetoolkit`'s blanket `BDEPEND="${RDEPEND}"` without assessing build-vs-runtime needs for native components.
- Validate metadata, manifest, `${D}`/`${ED}` installed-file tree, executable modes, native plugin paths, license payload and no HOME writes before maintainer-run `emerge` and native smoke tests. No service, KWin effect, profile or viewer is auto-enabled or started by a package hook.

**Mandatory Step 1.9 release gate: installed-image completeness and isolation.** Before accepting the first ebuild, compare its actual `${ED}` file tree against the source-to-destination contract in Section 2, including every required private runtime helper (for enabled features), its location, ownership, file type and mode. Reject missing or unexpected dependency files, not merely absent main executables. Validate broker sibling imports and CLI Bash/Python helper resolution with an isolated installed-tree fixture that excludes the `joetoo-ai` checkout and developer `PYTHONPATH`; explicitly exercise a `dolphin/sftp` restore intent so omission of `joetoo_kwin_sftp_target.py` is caught. Verify the selected KWin native effect(s), X11 protocol helper, service and config paths, docs/licensing and absence of installer writes into HOME. Only after installed-image checks pass should the maintainer run native X11/Wayland smoke tests from installed entry points. Neither the POC installer's `--check` nor source-tree unit tests satisfy this production gate.

Illustrative **structural** fragment (not a complete, ready-to-merge ebuild):

```bash
EAPI=8
inherit joetoo_license  # plus build eclass(es) chosen for the native KWin effect
S="${WORKDIR}/${PN}"
SRC_URI="https://raw.githubusercontent.com/JosephBrendler/joetoo-upstream/master/${CATEGORY}/${PN}-${PV}.tbz2"

src_install() {
    # Install CLI, private libexec, user OpenRC unit, docs and selected KWin effects.
    # The native build must use the appropriate compositor/plugin paths.
    joetoo_license_src_install
}
```

This fragment intentionally omits unresolved license/ABI/dependency details and is not a substitute for the final ebuild.

## 2. Source-to-installed-file manifest (accepted paths / proposed ownership)

**Maintainer decision:** use **`L=/usr/libexec/joetoo-kwin`** as the application-private runtime helper directory, with only necessary CLI and service path fixes. Root-owned application files and read-only templates are installed by Portage; no user HOME is populated. Paths below are target contracts to be verified in Phase 1 before the ebuild.

| Source in joetoo-kwin/ | Runtime role | Installed destination | Mode |
| --- | --- | --- | --- |
| `joetoo-kwin` | Public Bash CLI | `/usr/bin/joetoo-kwin` | 0755 |
| `libexec/joetoo-kwin-plan-functions` | Defaults, geometry, validation | `L/joetoo-kwin-plan-functions` | 0644 |
| `libexec/joetoo-kwin-launch-functions` | Launch orchestration | `L/joetoo-kwin-launch-functions` | 0644 |
| `libexec/joetoo-kwin-session.bashrc` | Original interactive Bash session | `L/joetoo-kwin-session.bashrc` | 0644 |
| `libexec/joetoo-kwind` | Session-bus broker | `L/joetoo-kwind` | 0755 |
| `libexec/joetoo_kwin_registry.py` | Managed registry | `L/joetoo_kwin_registry.py` | 0644 |
| `libexec/joetoo_kwin_managed_close.py` | Authenticated close frontend | `L/joetoo_kwin_managed_close.py` | 0644 |
| `libexec/joetoo_kwin_recovery.py` | Same-KWin-session checkpoint | `L/joetoo_kwin_recovery.py` | 0644 |
| `libexec/joetoo_kwin_persistence.py` | Last-good snapshots/history | `L/joetoo_kwin_persistence.py` | 0644 |
| `libexec/joetoo_kwin_rdp_launch.py`, `joetoo_kwin_rdp_target.py` | RDP identity/launch and validation | `L/` | 0644 |
| `libexec/joetoo_kwin_vnc_launch.py`, `joetoo_kwin_vnc_target.py`, `joetoo_kwin_vnc_identity.py` | VNC SSH/viewer supervisor and XCB identity | `L/` | 0644 |
| `libexec/joetoo_kwin_sftp_target.py`, `joetoo_kwin_sftp_advisory.py`, `joetoo_kwin_sftp_capability.py` | SFTP URI, advisory and KIO preflight | `L/` | 0644 |
| `libexec/joetoo_kwin_launch_resources.py`, `joetoo-kwin-exposure.py` | Desktop provisioning and geometry exposure | `L/` | 0644 |
| `joetoo-kwin-resident.js` | KWin JavaScript resident | `/usr/share/joetoo-kwin/joetoo-kwin-resident.js` | 0644 |
| `user-init.d/joetoo-kwind` | **User-mode** OpenRC unit | `/etc/user/init.d/joetoo-kwind` | 0755 |
| `conf.d/joetoo-kwind` | Global OpenRC service defaults | `/etc/conf.d/joetoo-kwind` | 0644, config-protected |
| `user-conf.d/joetoo-kwind` | Example of optional admin service override | Documentation example; optionally `/etc/user/conf.d/joetoo-kwind` only if approved | 0644 |
| `joetoo-kwin-per-run-template.conf` | **Short** editable launch-plan example | `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf` | 0644 |
| `joetoo-kwin-template.conf` | **Long**, annotated settings/plan reference | Documentation/examples, e.g. `/usr/share/doc/${PF}/examples/` | 0644 |
| `eselect/joetoo-kwin.eselect` | Always-installed user profile selector (optional to *use*) | `/usr/share/eselect/modules/joetoo-kwin.eselect` | 0644 |
| `docs/configuration-reference.md`, `docs/joetoo-kwin_user_manual.md` | Full configuration guide and user manual | `/usr/share/doc/${PF}/` | 0644 |
| Revised README files and functional `.conf` examples (Section 4) | Role-specific setup/migration guidance | `/usr/share/doc/${PF}/` and/or `/usr/share/joetoo-kwin/examples/` | 0644 |
| `tools/joetoo-kwind-configure-openrc-user` | Explicit, non-root rc_env_allow configuration helper | Install as an **opt-in** user command if retained after review | 0755 |
| `tools/joetoo-kwind-install-poc`, `poc-user-conf.d/joetoo-kwind` | Historical **development** home installer/override | Do not transfer to the curated first-release upstream tree; never run from ebuild | n/a |
| `COPYRIGHT.exceptions`, `LICENSES.package` | tarup source metadata; audit and SPDX text selectors | Curated upstream source root (not active runtime configuration) | Source-only metadata |

Current development installer covers **only fourteen user-owned files**; it omits plan, launch, `.bashrc` and SFTP/geometry helpers. Do not treat `tools/joetoo-kwind-install-poc --check` as complete production-package QA. The Python broker imports sibling modules relative to its own real directory, so they must remain together in `L`.

**Minimal source-path changes:** CLI currently uses `$(dirname -- "${BASH_SOURCE[0]}")/libexec` for `-c`, `-o`, `-L`, `-S`, `-r` and some `-d` paths. Define a single safe source-versus-installed helper resolution contract, used consistently, with no arbitrary untrusted path injection. Keep source-tree tests working. Change the user service's `JOETOO_KWIND_EXEC` default and `/etc/conf.d/joetoo-kwind` default **together** to `L/joetoo-kwind`. The resident's resource path is already absolute and suitable. The Python snapshot validator needs the installed `/usr/bin/joetoo-kwin` path when packaged.

## 3. Native C++ output, plugin compatibility and X11/XWayland distinctions

This contract relies on the authoritative, illustrated explanation in
[ARCHITECTURE §3](../ARCHITECTURE.md#3-components-and-ownership): there are
**two potential C++ plugin variants, and one separate protocol helper executable**.
Neither plugin is identical to the helper, nor is an object file (`adapter.o`
or `x11.o`) an installable effect.

| Source and SDK | Produced artifact | Required capability |
| --- | --- | --- |
| `adapter.cpp` built with KWin (`KWin::kwin`) | **Wayland** `joetoo_managed_close.so` | Required on `kwin_wayland` for authenticated `Inspect()`, same-session recovery identity, and managed close of **native Wayland and XWayland** clients |
| Same `adapter.cpp` separately built with KWinX11 (`KWinX11::kwin`) | **Legacy native-X11** `joetoo_managed_close.so` | Only useful to the old `kwin_x11` compositor, installed to a *different* plugin namespace |
| `x11.cpp` built against libxcb | Executable `joetoo-kwin-close-x11` | Used by either plugin for graceful X11-protocol `WM_DELETE_WINDOW`, **including XWayland** inside a Wayland desktop; does **not** require the KWinX11 SDK |

The Wayland plugin and X11 protocol helper are **always part of a complete
Wayland/XWayland-capable installation**. A legacy-X11 USE choice, if offered,
controls **only** the separately built native-X11 plugin. It must never remove
the XWayland helper, even on systems using `USE=vnc` and `USE=-x11`.

**Build is headless.** `emerge` compiles from on-disk KWin headers/CMake SDKs
and may run from SSH or a console, without an active graphics session. Loading
an effect later requires a running compatible KWin compositor and explicit
activation; packaging must never auto-load a plugin or start a compositor.

**Current source versus proposed release:**
`native/managed-close/CMakeLists.txt` still says `find_package(KWin 6.7.6 EXACT
REQUIRED)` (or `KWinX11 6.7.6 EXACT REQUIRED` in the legacy build). This is the
accepted 6.7.6 development baseline, **not an approved permanent ebuild pin**.
KWin effect factory IID includes an exact KWin plugin version identity and the
C++ API is version-sensitive. Investigate and test compiling the Wayland
variant against KWin 6.8+ before loosening CMake's `EXACT` requirement.
The ebuild must compile against installed compatible SDK versions—not choose a
backend using the current terminal's `DISPLAY` or session type.

**Runtime mismatch diagnosis:** record a plugin's built-against SDK/version,
compare it with the *running* KWin (e.g. D-Bus
`org.kde.KWin /KWin org.kde.KWin.supportInformation`), and warn when native
capability may be unavailable. KWin's loader plus the broker's authenticated
identity checks remain authoritative; unverifiable `Inspect()`/close actions
must fail closed. Say that **native Wayland/XWayland managed close and recovery
identity verification** may be affected, rather than implying only XWayland
close is lost. This does not impair KDE's ordinary window close buttons.
Check native-X11 build identity only if that variant is actually installed.

**Automatic rebuild is a separate constraint:** building from the current SDK
when `joetoo-kwin` is emerged does not guarantee that a *later same-subslot
KWin upgrade* causes Portage automatically to re-emerge it. Determine and test
a suitable rebuild maintenance hook or workflow. Do not promise a version-
agnostic binary or pin the entire application to obsolete 6.7.x forever.

**Legacy native X11 status:** Plasma 6.8 retires `kwin_x11`, **not XWayland**.
The maintainer previously preferred an off-by-default `x11` flag for the
legacy plugin, then raised the reasonable possibility of omitting it from the
first production release. **This one inclusion decision remains open.** If
included, build it using its independently matching 6.7.x KWinX11 SDK and
install it under `${KDE_INSTALL_PLUGINDIR}/kwin-x11/effects/plugins/`;
Wayland uses `${KDE_INSTALL_PLUGINDIR}/kwin/effects/plugins/`. The helper
installs once at `${KDE_INSTALL_LIBEXECDIR}/joetoo-kwin-close-x11`.
The code's compositor-binary check must remain intact.

## 4. Configuration architecture — verified implementation versus proposed cleanup

There are **two independent configuration trees**. The development POC override is a *sample of the third service layer*, not a fourth load layer. The `XDG_CONFIG_HOME` fallback is a directory choice, **not an additional independent user defaults layer**.

### A. OpenRC **service** configuration (three effective tiers)

```text
/etc/conf.d/joetoo-kwind                            (1) global defaults / loader
   sources, when present:
/etc/user/conf.d/joetoo-kwind                       (2) root-managed optional override
   then sources, when present:
${XDG_CONFIG_HOME:-$HOME/.config}/rc/conf.d/joetoo-kwind
                                                   (3) account-owned optional override
```

The actual user service `user-init.d/joetoo-kwind` re-sources `/etc/conf.d/joetoo-kwind` to impose the intended order, with a default executable fallback. The global file currently sets `JOETOO_KWIND_EXEC=/usr/libexec/joetoo-kwind` and `JOETOO_KWIND_RESIDENT_JS=/usr/share/joetoo-kwin/joetoo-kwin-resident.js`, and the later service overrides can replace these. It does **not** set planner recipes, layout geometry or default launch settings.

`poc-user-conf.d/joetoo-kwind` is a development-only example installed into **the same tier (3) path** by `tools/joetoo-kwind-install-poc`. It points the service at `~/.local/libexec/joetoo-kwind` and `~/.local/share/joetoo-kwin/joetoo-kwin-resident.js`; it must **not** become production's default per-user override. The optional `tools/joetoo-kwind-configure-openrc-user` separately adjusts the user OpenRC `rc_env_allow` setting, which is an OpenRC environment-control concern, not a new `joetoo-kwind` conf.d tier.

**Recommended production deployment:** install and config-protect the active `/etc/conf.d/joetoo-kwind` for default system command paths. Ship a *functional example* of `/etc/user/conf.d/joetoo-kwind` and a separate *functional example* of the account override in read-only shared examples; create neither active override automatically. Write concise role-specific README files. Avoid adding an extra active global override file unless the maintainer expressly chooses it.

### B. `joetoo-kwin` **launch** configuration (built-ins + two additive defaults + exactly one selected plan)

```text
built-in plan_defaults()                         lowest precedence
    |
/etc/joetoo-kwin/defaults.conf                  optional additive system defaults
    |
${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf
                                               optional additive user defaults
    |
ONE selected *per-run launch plan*:
    a) explicit -f FILE, otherwise
    b) ${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf,
       otherwise (only when absent)
    c) /etc/joetoo-kwin/joetoo-kwin.conf       system PLAN fallback
    |
supported CLI overrides, e.g. -v / -q           highest precedence
```

**Important corrections to the question:** `/etc/joetoo-kwin/joetoo-kwin.conf` is a **fallback plan**, not the global `defaults.conf` file. The XDG and `$HOME/.config` paths are **one user directory choice**, not two independently loaded layers; a relative `XDG_CONFIG_HOME` also falls back to `$HOME/.config`. Both defaults files are optional and additive (system then user), even with an explicit `-f` selected plan. Missing optional defaults are fine; existing unreadable, invalid or unsafe layers fail rather than being silently ignored. Plan and defaults files are **trusted Bash**, not sanitized key-value data. The app does not auto-detect screen dimensions; usable examples must specify them and recipes.

### C. What `eselect joetoo-kwin` actually does

`eselect/joetoo-kwin.eselect` is optional, per-user, and **does not introduce an additional launch-config layer**. The user manually creates valid files under:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/profiles/<name>.conf
```

`eselect joetoo-kwin set work.conf` creates (on first selection) or switches (only an existing **valid selector-managed symlink**) the selected plan:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf
    -> profiles/work.conf
```

Then the ordinary CLI's user plan selection reads that link. `-f FILE` overrides only which plan is selected, not the additive defaults. The selector never creates profiles, copies templates, executes a profile, overwrites a regular user plan or touches service settings. It validates user ownership/modes, profile syntax and symlink identity; switching an existing link requires GNU `mv --exchange --no-copy` and supported filesystem behavior.

**Why the current manual snippet fails as a development-install recipe:** the line `cp -n /usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf ...` is explicitly a **future packaged-resource path**. This path will not exist in an uninstalled `joetoo-ai` source checkout, and the POC installer does not install it. Also, if there is already a *regular* `~/.config/joetoo-kwin/joetoo-kwin.conf`, `eselect ... set` deliberately refuses to overwrite it. A third failure mode is absent/wrongly installed `joetoo-kwin.eselect` module or incompatible GNU `mv`. **Do not call the snippet universally broken** without the actual CLI error; change documentation to distinguish source-tree use and installed-package use, and document these preconditions.

Corrected **illustrative** source-tree path (execute only by the maintainer/user after examining and editing the plan):

```bash
project=~/joetoo-ai/workspace/projects/joetoo-kwin
config_root=${XDG_CONFIG_HOME:-$HOME/.config}
case $config_root in /*) ;; *) config_root=$HOME/.config ;; esac
config_dir=$config_root/joetoo-kwin
install -d -m 0700 -- "$config_dir/profiles"
cp -n -- "$project/joetoo-kwin-per-run-template.conf" "$config_dir/profiles/work.conf"
# Inspect/edit the *copy* and ensure your development eselect module is installed.
# If $config_dir/joetoo-kwin.conf is a regular file, preserve/migrate it first.
# Validate explicitly without switching the selection:
"$project/joetoo-kwin" -c -f "$config_dir/profiles/work.conf"
# After confirming the module and absence of a conflicting regular user plan:
eselect joetoo-kwin list
eselect joetoo-kwin set work.conf
eselect joetoo-kwin show
```

For **packaged** installation replace the `cp` source with `/usr/share/joetoo-kwin/joetoo-kwin-per-run-template.conf`, and use installed `joetoo-kwin -c`; no automatic HOME changes. Distinguish the following two existing source files correctly:

| Source | **Verified** current content | Recommended installed use |
| --- | --- | --- |
| `joetoo-kwin-per-run-template.conf` | **Short** practical example: display dimensions, an editable two-window desktop-3 plan and minimal RDP policy; optional SSH, SFTP, VNC, RDP recipe comments | Ship as primary user-copyable starter plan at `/usr/share/joetoo-kwin/` |
| `joetoo-kwin-template.conf` | **Long** annotated config: extensive timing, geometry, RDP/VNC/SFTP and close settings, plus plan examples | Ship as an annotated reference example in the versioned documentation/examples area (not auto-sourced) |

Proposed naming clarification: keep compatibility filenames for 0.1.0, but add explicit README labels **SHORT STARTER** versus **FULL ANNOTATED REFERENCE**. If the maintainer prefers renaming them later, preserve old names as references/aliases and update the guide in the same source transition; do not silently swap their content or make the full file active global defaults.

### D. Pre-upstream configuration cleanup and documentation deliverables

**Recommendation: yes, perform this before the `joetoo-upstream` transition**, because it avoids publishing ambiguous config paths in a release artifact. Keep it bounded to documentation, runnable examples and the required packaged-path corrections—not a new configuration loader architecture or rework of accepted precedence.

Every distinct shipped `.conf`/config role gets a concise paired **`README_xxx_conf.md`** (or a clearly linked section in an adjacent reference when semantics are identical). Suggested files, named by role to avoid confusing the two `joetoo-kwind` override paths:

| Configuration role | Paired documentation / example to author for 0.1.0 |
| --- | --- |
| `conf.d/joetoo-kwind` → `/etc/conf.d/joetoo-kwind` | `README_global_joetoo_kwind_conf.md` — actual defaults, root ownership, sourcing, protected upgrade |
| `user-conf.d/joetoo-kwind` → optional `/etc/user/conf.d/joetoo-kwind` | `README_system_user_joetoo_kwind_conf.md` — optional root override and order |
| `poc-user-conf.d/joetoo-kwind` → account `.config/rc/conf.d/...` | `README_account_joetoo_kwind_conf.md` — user override; explain POC-only source and migration |
| `/etc/joetoo-kwin/defaults.conf` | `README_system_defaults_conf.md` — sparse administrator defaults example, never whole manual |
| XDG user `joetoo-kwin/defaults.conf` | `README_user_defaults_conf.md` — sparse account defaults example, correctly resolved directory |
| system fallback/user/`-f` `joetoo-kwin.conf` | `README_joetoo_kwin_launch_conf.md` — single selected plan; precedence, minimal functional plan, source-vs-packaged paths |
| `profiles/*.conf` + selector-created active link | `README_eselect_profiles_conf.md` — explicit profile setup, safe switch and migration, install preconditions |
| short/long shipped `.conf` templates | `README_joetoo_kwin_templates_conf.md` — explain precisely which is short versus full and how to copy |

Each README needs: exact *source* and *installed* role/path; whether it is active or sample-only; load order; ownership/mode; behavior when absent; one functional commented example; safe upgrade/migration rule; and link to the full user manual/configuration guide. Pairing need not require eight redundant manuals: keep each brief (prefer a screenful) and cross-reference one authoritative configuration guide. Add appropriate copyright/SPDX metadata for `tarup`.

## 5. Approved USE policy and subordinate client dependencies

**Confirmed choices:** the package installs its `eselect` module
unconditionally, though using `eselect joetoo-kwin` remains optional for each
user. `rdp`, `vnc` and `sftp` default ON; SDL FreeRDP and TigerVNC are the
only implemented RDP/VNC clients at this release. Provide subordinate client
flags `sdl-freerdp` and `tigervnc` and the requested nested `REQUIRED_USE`
constraints so additional clients may be added *after they are implemented*.
Do **not** mandate FreeRDP's `openh264`: the individual user can elect that
flag using their own `/etc/portage/package.use/` configuration.

Illustrative feature-policy fragment (not a complete executable ebuild):

```bash
IUSE="+rdp +sdl-freerdp +vnc +tigervnc +sftp x11"
REQUIRED_USE="
    rdp? ( || ( sdl-freerdp ) )
    vnc? ( || ( tigervnc ) )
"
RDEPEND="
    app-admin/eselect
    rdp? ( sdl-freerdp? ( >=net-misc/freerdp-3.32.1[client,sdl] ) )
    vnc? ( tigervnc? ( net-misc/tigervnc[viewer] ) )
    sftp? ( kde-apps/kio-extras[sftp] )
    x11? ( kde-plasma/kwin-x11 )
"
# Complete base and build dependencies intentionally omitted.
# End of commands

```

`REQUIRED_USE` constrains **USE flags**, not individual dependency atoms:
`||` is *at least one*, not exactly one. With one implemented client per
protocol it is structurally redundant, but explicitly anticipates a later
choice without pretending KRDC or Remmina are supported today. With
`USE=-rdp`, the `sdl-freerdp` flag has no dependency effect, avoiding needless
reverse-implication constraints. The core nonoptional viewer-independent
Python validators may remain installed; capability preflight must fail safely
when the requested viewer dependency is absent.

**The `x11` line above is conditional on a still-open decision.** If native
`kwin_x11` support is omitted from 0.1.0, remove `x11` from IUSE/RDEPEND and
the legacy plugin build while **retaining the Wayland plugin and compiled X11
protocol helper for XWayland**. Do not interpret `USE=-x11` as disabling
TigerVNC viewers running as XWayland clients. Default-off `x11` was an earlier
maintainer preference, not final approval to keep it after the Plasma 6.8
retirement discussion.

A real ebuild must separately specify complete core `DEPEND`, `BDEPEND`,
`RDEPEND` (Bash, joetoo header, Python/GLib/D-Bus, qdbus6, jq, KWin native
SDK, ECM/CMake/Qt6/XCB, OpenRC, Konsole, SSH and verified utilities). Dolphin
local recipes must remain supported when `USE=-sftp`; `sftp` adds the KIO
SFTP worker, not Dolphin's underlying local-file capability.

## 6. Installation, upgrade, removal and package QA

- **No implicit user-state mutation:** install into `/usr` and selected root-owned `/etc` paths only; never create/edit user active plans, profiles, `~/.local`, the user's OpenRC `rc.conf`, `XDG_STATE_HOME` history, or runtime checkpoint. Never run `eselect`, development HOME installer, viewer or `rc-service -U ... start` in ebuild hooks.
- **Service separation:** `/etc/user/init.d/joetoo-kwind` is a non-root `rc-service -U` OpenRC unit, **not** `/etc/init.d/joetoo-kwind` and not a root service. Preserve current `rc_cgroup_cleanup=NO`; service stop/restart must not terminate Konsole/SSH/RDP/VNC children. No implicit start/stop/restart on merge/unmerge.
- **Migrations:** existing `~/.local/bin/joetoo-kwin` may shadow `/usr/bin`; existing account override from the POC may direct OpenRC to user `~/.local/libexec`; user active `joetoo-kwin.conf` may be a regular file and selector refuses to overwrite it. Provide explicit read-only diagnosis and opt-in instructions; never change a user config automatically.
- **Private state:** preserve existing mode-700 runtime directories, mode-600 snapshots and history across package operations; do not adopt stale UUIDs after a new compositor session.
- **`eselect` and documentation:** ship complete functional *examples*, short per-role README files, configuration-reference.md and user manual, and the always-installed (user-optional) selector; show exact source vs installed paths. If docs compressed by Portage, avoid broken paths and explain where to read them; optional explicit no-compress policy is a maintainer choice.
- **Native effect:** install matching binary plugin(s), never auto-load. Confirm exact SDK build, compositor version and namespace, helper binary location and lack of duplicate install conflicts. If incompatible, close commands must fail non-destructively and show an actionable warning when reliable evidence exists.
- **QA before any native run:** `tar -tjf`; licensing manifest; ebuild/pkgcheck/Manifest; `${D}`/`${ED}` staged file/mode/path audit; imports plus Bash/Python tests; CMake build for Wayland and (when x11 enabled) X11; inspect `IUSE` permutations and legacy POC interactions.
- **Native acceptance later, human-run:** minimal Wayland and X11 packaged-path smoke checks: CLI help and safe `-c` with reviewed config; broker `rc-service -U` start/status/stop; KWin resident inventory; disposable managed launch/close and one bounded `-S`/`-r` path, where appropriate. Preserve the existing accepted Step 1.7 evidence; do not rerun the entire historical RDP/VNC suite for packaging-only edits.

## 7. Settled decisions and remaining verification

| Area | Current contract and disposition |
| --- | --- |
| Release flow | **Settled:** human-curated `joetoo-ai` → `joetoo-upstream/dev-util/joetoo-kwin/` → `tarup` source tarball → `joetoo` EAPI-8 ebuild; `inherit joetoo_license` plus `joetoo_license_src_install` |
| Release name | **Settled:** `dev-util/joetoo-kwin-0.1.0`; first archive `joetoo-kwin-0.1.0.tbz2` via `tarup joetoo-kwin -minor` only if no earlier tarball exists |
| Paths | **Settled:** `/usr/bin/joetoo-kwin`, private `/usr/libexec/joetoo-kwin`, global OpenRC conf.d and user OpenRC unit; minimal path changes before transfer |
| `eselect` | **Settled:** always installed, never auto-run; keep GPL-3.0-or-later heading with Gentoo API acknowledgment and AI-assistance statement; no copied-Gentoo-code finding in the source comparison performed |
| Config and docs | **Settled:** clean per-role README examples and profile docs before source transfer; global service config active, root/user overrides shipped as examples only; user plan HOME never modified by Portage |
| Runtime clients | **Settled:** default-on `rdp`, `vnc`, `sftp`; subordinate `sdl-freerdp` and `tigervnc` groups; no required OpenH264; optional flags install dependencies but do not remove core validators |
| Native core | **Settled:** Wayland plugin **and** `joetoo-kwin-close-x11` helper always built for Wayland/XWayland support; never select compiler SDK from a running display |
| Native legacy X11 | **Still decide:** keep temporary off-by-default `USE=x11` for `kwin_x11` 6.7, or omit it from first production ebuild (neither choice changes XWayland support) |
| KWin upgrade | **Implementation/QA needed:** build against newer installed KWin SDK, run 6.8 compatibility tests, embed actual built-against identity, warn on runtime mismatch, implement/plan reliable re-emerge on same-subslot updates |
| Licensing | **Source audit needed:** provisional project-root `LICENSES.package`/`COPYRIGHT.exceptions` included in curated transfer, license texts furnished by `tarup` and installed through eclass; review all shipped headers and third-party attributions |
| Test/source contents | **Settled:** no historical task archives/POC installer or focused tests installed onto production; curated release may retain focused build/test sources deliberately but not blindly |

### Remaining choices, narrowly bounded

1. Is the legacy *native* `kwin_x11` 6.7 plugin still worth shipping behind
   off-by-default `USE=x11`, or should 0.1.0 omit that optional artifact?
2. Confirm exact source and ABI compatibility with KWin 6.8; select the
   reliable built-against metadata and later-update rebuild mechanism using
   actual test results, not a guessed API.
3. Complete the **final** curated-source file/license/header audit; the new
   metadata files are an accurate *starting point*, not an assertion that
   `tarup` already passes against the full development project.

**Next bounded joetoo-ai implementation:** revise source-vs-installed config
examples and their README companions, fix packaged CLI/service helper lookup,
then test native Wayland 6.8 compilation in a controlled environment. A
published `joetoo-upstream` release and `joetoo` ebuild remain human-maintained
under their repository AI policies.

## 8. Curated joetoo-upstream source-transfer manifest

**Destination root:** `joetoo-upstream/dev-util/joetoo-kwin/`. This is a
selection from the development project, **not** the entire joetoo-ai checkout.
Keep the source release complete enough for the human maintainer to inspect,
build and license it; production installations must not contain development
workspaces or historical evidence.

| Source in `joetoo-ai/workspace/projects/joetoo-kwin/` | In upstream tarball? | Installed in production? |
| --- | --- | --- |
| `joetoo-kwin`, required `libexec/` planner/broker/runtime helpers, `joetoo-kwin-resident.js` | Yes, full manifest §2 | Yes |
| `native/managed-close/{adapter.cpp,x11.cpp,channel.h,CMakeLists.txt,metadata.json}` | Yes | Selected compiled plugin(s) and **the executable helper** |
| `user-init.d/joetoo-kwind`, `conf.d/joetoo-kwind` | Yes | Yes, root-owned global paths |
| `user-conf.d/joetoo-kwind`, functional per-user override samples | Yes | Read-only examples; no active HOME file |
| `joetoo-kwin-per-run-template.conf`, `joetoo-kwin-template.conf`, config-role README companions | Yes | Shared starter/reference examples, docs |
| `eselect/joetoo-kwin.eselect` | Yes | **Always** |
| `docs/configuration-reference.md`, `docs/joetoo-kwin_user_manual.md`, native README | Yes | Yes, docs |
| **`LICENSES.package` and `COPYRIGHT.exceptions`** (new in project root) | **Yes, required by `tarup`** | Used during archive creation; eclass installs actual staged license texts |
| Focused, selected test sources useful for build verification | Optional curated subset | **No** |
| `archive/`, `task_1.9/`, historical native transcripts, `tools/joetoo-kwind-install-poc`, POC-only test tools, scratch build products | **No** | **No** |

The release metadata must be audited against the **actual curated** source
set. Ordinary source (including `native/managed-close/CMakeLists.txt`, which
currently lacks a typical copyright line) should gain correct copyright
headers rather than be added to `COPYRIGHT.exceptions` merely to suppress
validation. `metadata.json` cannot carry source comments and is justified as
an exception. Current `tarup` packages the complete curated directory and
stages `/LICENSE` plus `LICENSES/*.txt`; a generalized exclusion-file feature
is a possible future improvement, not required for 0.1.0.

## 9. Source references reviewed

- [joetoo-ai Step 1.9 HANDOFF](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/task_1.9/HANDOFF.md), [task README](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/task_1.9/README.md), [architecture](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/ARCHITECTURE.md).
- [CLI source: select_config/prepare_config_sources and source lookup](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/joetoo-kwin), [OpenRC user service](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/user-init.d/joetoo-kwind), [global service config](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/conf.d/joetoo-kwind), [POC override](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/poc-user-conf.d/joetoo-kwind).
- [Short per-run template](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/joetoo-kwin-per-run-template.conf), [long annotated template](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/joetoo-kwin-template.conf), [eselect module](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/eselect/joetoo-kwin.eselect), [configuration guide](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/docs/configuration-reference.md).
- [Native KWin CMake](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/native/managed-close/CMakeLists.txt) and [native README](https://github.com/JosephBrendler/joetoo-ai/blob/0ec0234e589ce2b42bbfcfb6ebcec0207b627d60/workspace/projects/joetoo-kwin/native/managed-close/README.md).
- [Actual tarup source](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/joetoolkit/devtools/tarup), [LICENSES.package example](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/joetoolkit/LICENSES.package), [COPYRIGHT.exceptions example](https://github.com/JosephBrendler/joetoo-upstream/blob/master/dev-util/joetoolkit/COPYRIGHT.exceptions), [joetoo_license.eclass](https://github.com/JosephBrendler/joetoo/blob/master/eclass/joetoo_license.eclass), [joetoolkit ebuild precedent](https://github.com/JosephBrendler/joetoo/blob/master/dev-util/joetoolkit/joetoolkit-1.0.18.ebuild).
- [Gentoo ebuild/REQUIRED_USE reference](https://devmanual.gentoo.org/eclass-reference/ebuild/index.html); [FreeRDP flags](https://packages.gentoo.org/packages/net-misc/freerdp), [KIO extras flags](https://packages.gentoo.org/packages/kde-apps/kio-extras), [QtTools qdbus](https://packages.gentoo.org/packages/dev-qt/qttools).
