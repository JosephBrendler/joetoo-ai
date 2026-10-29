#!/usr/bin/env python3
"""Generate a reviewable joetoo-kwin documentation patch without editing the checkout.

Run from joetoo-ai root:
  python3 /path/to/joetoo-kwin-doc-review.py --output /tmp/joetoo-kwin-doc-review.patch
  git apply --check /tmp/joetoo-kwin-doc-review.patch
  git apply /tmp/joetoo-kwin-doc-review.patch  # only after maintainer approves
The script uses a temporary Git repository only to calculate a genuine unified diff.
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

P = Path("workspace/projects/joetoo-kwin")
BASE_FILES = [
    P / "ARCHITECTURE.md",
    P / "README.md",
    P / "STEP1_3B_PROBE.md",
    P / "archive" / "README.md",
]

NEW_README = """\
# joetoo-kwin

Development workspace for replacing the joetoo X11 `xdotool_*` window workflows
with KWin-compatible tools on both X11 and Wayland. These are candidate sources
in `joetoo-ai`, not installed Gentoo packages. See [ARCHITECTURE.md](ARCHITECTURE.md)
for version 1 requirements, design contracts, and acceptance gates.

## Current status

**Completed through Step 1.3b** (October 2026). Current sources can observe
KWin window identities and lifecycles, recover observational inventory after a
broker restart, and diagnose direct-PID launch-to-window correlation. They do
**not** provide a managed-window ownership registry, a multiwindow `-o`
launcher, or safe managed-window close operations.

**Next: Step 1.4 — in-memory multiwindow registry**, in four agreed increments:

| Increment | Intended outcome |
| --- | --- |
| 1.4a | Review the proposed record/identity model and create headless contract tests; approve design changes before implementing them |
| 1.4b | Implement multiwindow registration and observational state updates, without class-only adoption |
| 1.4c | Expose read-only managed-window list, detail, and broker status |
| 1.4d | Validate a 37-window mock, then native X11 and Wayland scenarios |

The detailed registry schema, eligibility rules, and new D-Bus method names
remain **design questions**, not approved implementation contracts.

## Development and validation platforms

The native validation reported below was conducted on Gentoo Linux with KDE
Plasma 6.7.5, OpenRC, and user-session KWin. These are test environments,
not permanent hardware or minimum-version requirements.

| Host | Relevant platform | KWin backend |
| --- | --- | --- |
| `gmki91` | GMKtec NucBox M3 PLUS, Intel i9-12900HK, x86_64 | X11 |
| `q552u01` | ASUS Q552UB, Intel i7-6500U, x86_64 | Wayland |

Both used 1920×1080 displays for the recorded development tests. Kernel,
theme, transient memory/battery use, and other fastfetch details are deliberately
not maintained here.

## Completed proof-of-concept and milestone evidence

| Step | Maintainer-reported result | Reference |
| --- | --- | --- |
| 0 / early POCs | KWin positioning, independent Konsole, interactive SSH `bash --rcfile`, unreachable-target placeholder, original-shell return and process exit behavior demonstrated | [Historical POCs](archive/README.md) |
| 1.2a–1.2b | OpenRC user-service and resident KWin JavaScript start/restart and reconnection validated; broker restart did not terminate existing Konsole/SSH clients | [Native validation](archive/step1.2a-candidate/NATIVE_VALIDATION.md) |
| 1.3a–1.3a.2 | KWin UUID/geometry/lifecycle observation and automatic inventory synchronization on both backends, without implied ownership | [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16) |
| 1.3b.1–1.3b.2 | Diagnostic exact-PID correlation, class-candidate reporting, and conservative ambiguous/timeout behavior on both backends | [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) |

**Step 1.3b detail:** Konsole (`--separate`) and Dolphin (`--new-window`)
produced exact-PID `MATCHED` results on X11 and Wayland. Existing-profile
Chrome launches delegated to a running browser and correctly returned `TIMEOUT`
with a class-only candidate, not ownership. Unique Chrome `--user-data-dir`
launches matched their KWin PID and UUID on both backends, at the cost of an
isolated browser profile. Both machines passed 74 Python and 4 JavaScript
regression tests. This establishes useful diagnostics, **not** production-grade
ownership for arbitrary delegated applications. See the
[archived Step 1.3b notes](archive/STEP1_3B_PROBE.md) for the original experiment
instructions and protocol details.

## Active development files and checks

- `libexec/joetoo-kwind` — Python session D-Bus broker and observational data.
- `joetoo-kwin-resident.js` — KWin resident observation/placement interface.
- `joetoo-kwin` — current Bash client for active-window movement and legacy
  single-launch POC. The richer Step 1 planner is still archived.
- `tools/joetoo-kwin-correlation-probe` — read-only launch correlation probe.
- `user-init.d/`, `conf.d/`, `user-conf.d/`, `poc-user-conf.d/` — OpenRC
  service and executable configuration.
- `tools/joetoo-kwind-install-poc` — user-owned POC installation/checking tool.
- `tests/` — headless regression tests; `archive/` — historical references.

Run these checks from `workspace/projects/joetoo-kwin/`:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_step1_3a.js
bash -n joetoo-kwin tools/joetoo-kwin-correlation-probe
./tools/joetoo-kwind-install-poc --check
```

The POC user service can be inspected in a local Plasma session with
`rc-service -U joetoo-kwind status`. Installing/updating the POC or running
window-launching experiments are separate, explicit maintainer operations.

## Design and development references

- [Architecture and version 1 requirements](ARCHITECTURE.md) — authoritative
  product design; proposed schema and open questions remain subject to review.
- [Project AGENTS.md](AGENTS.md) — AI collaboration and documentation policy.
- [Archive index](archive/README.md) — original POCs, candidate designs and
  historical testing instructions.
- [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16) and
  [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) — signed
  implementation history and milestone-level test evidence.

Do not treat historical examples or evidence as newly accepted design
requirements. Architectural choices are discussed with the maintainer before
they are incorporated into `ARCHITECTURE.md`.
"""

def section_replace(s: str, start: str, end: str, replacement: str) -> str:
    a = s.find(start)
    b = s.find(end, a + len(start))
    if a < 0 or b < 0:
        raise ValueError(f"Section delimiters missing: {start!r}, {end!r}")
    return s[:a] + replacement + s[b:]

def once(s: str, original: str, replacement: str) -> str:
    n=s.count(original)
    if n != 1:
        raise ValueError(f"Expected 1 occurrence, found {n}: {original[:100]!r}")
    return s.replace(original, replacement, 1)

def update_architecture(s: str) -> str:
    s=once(s, "# joetoo-kwin — architecture and version 1 development contract",
           "# joetoo-kwin — architecture and version 1 requirements")
    s=once(s, "It distinguishes **accepted\nrequirements**, **implemented POC evidence**, **proposed contracts requiring\nvalidation**, and **open decisions**. Acceptance of this document does not establish\nthat a proposed interface or behavior works on Gentoo.",
           "It distinguishes **accepted requirements**, **proposed design contracts**,\nand **open questions**. A proposed interface is not evidence that it has been\nimplemented or tested; development status and native results belong in the\n[project README](README.md).")
    s=section_replace(s, "## 1. Purpose and release boundary\n", "## 2. Development platforms\n",
        """## 1. Purpose and release boundary

Replace the legacy X11 `xdotool_open_windows`, `xdotool_close_windows`, and
`xdotool_sizemove_this_window` workflows with `joetoo-kwin`, operating under
KDE Plasma/KWin on **X11 and Wayland**. Support the maintainer's normal
interactive shell workflow, a declarative multi-desktop session layout,
independently manageable SSH and graphical windows, and conservative window
closure.

Version 1 requires an OpenRC-supervised `joetoo-kwind` management daemon and
reliable initialization/reconnection of resident KWin JavaScript. Intermediate
0.x prototypes are permitted; neither requirement is deferred past version 1.

""")
    s=section_replace(s, "## 2. Development platforms\n", "## 3. Components and ownership\n",
        """## 2. Supported development environment

Development and validation must address both KWin/X11 and KWin/Wayland under
Gentoo Linux, KDE Plasma, and an OpenRC user session. The specific host
platforms and observed test outcomes are recorded in the
[project README](README.md), not maintained as architectural requirements.

""")
    s=once(s,
        "| Configuration/profile | `/etc/joetoo-kwin/joetoo-kwin.conf` | Selected *desired* layout (symlink to profile under `configs/`) | Store ephemeral PIDs or KWin UUIDs |\n",
        "| Configuration/profile | `/etc/joetoo-kwin/joetoo-kwin.conf` | Selected *desired* layout (symlink to profile under `configs/`) | Store ephemeral PIDs or KWin UUIDs |\n\n"
        "**D-Bus compatibility:** The established service name `org.joetoo.KWinBridge`,\n"
        "object path `/org/joetoo/KWinBridge`, and existing method signatures are\n"
        "compatibility contracts. Renaming executables must not silently change them.\n")
    s=once(s, "**Synchrnization of current window inventory:**", "**Synchronization of current window inventory:**")
    s=once(s, "| Field | Type | Meaning |\n| desktop | integer |",
           "| Field | Type | Meaning |\n| --- | --- | --- |\n| desktop | integer |")
    s=once(s,
      "Maintainer note: project data structures and schema are \"under development\" and expected to evolve as development and DT experience dictate.  Any changes must be approved by maintainer, and the change decision is to be documented in the project README.md\"\n",
      "The schema is provisional and will be refined during Step 1.4; the structures\nbelow are design candidates rather than implemented Python interfaces.\n")
    s=once(s,"### 7.1 Working state and private runtime JSON (accepted direction)",
           "### 8.1 Working state and private runtime JSON (accepted direction)")
    s=once(s,"### 7.2 Durable last-known-good `.conf` (accepted direction)",
           "### 8.2 Durable last-known-good `.conf` (accepted direction)")
    s=once(s,
      "The current merged Step 1 candidate\nimplements only `-c`, `-f`, `-m` with **five** operands, and a deliberately\nunimplemented `-o`; the table above is a **target**, not a description of\ncurrent capabilities. Retire the POC `move` subcommand when `-m` coverage is\nvalidated; use `mw` as an alias/function and preserve `ow`/`cw` shorthands.",
      "This table is a **target**, not a description of currently implemented CLI\n"
      "capabilities. Retire the POC `move` subcommand when `-m` coverage is\n"
      "validated; use `mw` as an alias/function and preserve `ow`/`cw` shorthands.\n"
      "See the [project README](README.md) for the current implementation status.")
    s=once(s,
       "New candidate work is under `workspace/projects/joetoo-kwin/`; each substep\nuses the accepted baseline and the **branch-and-review** workflow described in\n`workspace/AGENTS.md`. Suggested names: `task/joetoo-kwin-step1.1-architecture`,\n`task/joetoo-kwin-step1.2a-openrc`, etc. Prepare a full diff and validation\nreport; seek explicit approval **before** commit, push and draft PR. Human\nmaintainer alone merges and integrates protected repositories.",
       "These gates describe intended deliverables and acceptance criteria.\n"
       "Current completion status and supporting evidence are recorded in the\n"
       "[project README](README.md); collaboration procedures are governed by\n"
       "`AGENTS.md` and the parent workspace instructions.")
    s=section_replace(s,
       "The outputs of Step 1.2a broker/OpenRC implementation and tests now reside in the project root.",
       "## 12. Open questions and explicit verification tasks\n",
       "")
    s=once(s,
       "- Can Konsole reliably expose a title like `joetoo_konsole_3.1` as the\n  **KWin-visible window caption**, with enough timing/uniqueness to aid\n  launch correlation? Which PID belongs to a Konsole window on each backend?",
       "- Can a per-launch Konsole title token such as `joetoo_konsole_3.1` be\n  made KWin-visible in time for correlation? A title alone is only a hint;\n  direct-PID Konsole correspondence has been tested on both backends.")
    s=once(s,
       "- What is the precise user-service OpenRC installation/session-startup\n  mechanism on the target Gentoo/OpenRC/elogind environment? What happens to\n  descendant/application process groups on service stop and restart?",
       "- What additional Plasma-readiness guarantees are needed at OpenRC\n  user-session startup? Broker stop/restart and client-process survival have\n  been validated in the POC scenarios.")
    s=once(s,
       "Resolve each experimentally and record **actual** tests/decisions in this\nfile or a linked, reviewed project record before promoting a proposal to an\naccepted design invariant.\n\n",
       "")
    s=s[:s.index("## 13. Inspected baseline and evidence\n")].rstrip()+"\n"
    return s

def run(cmd: list[str], cwd: Path) -> bytes:
    return subprocess.run(cmd,cwd=cwd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout

def create_patch(repo_root: Path, output: Path) -> None:
    files={}
    for path in BASE_FILES:
        file=repo_root/path
        if not file.is_file():
            raise FileNotFoundError(f"Expected checkout file missing: {file}")
        files[path]=file.read_bytes()
    # Prevent running the authoring tool against an unrecognized document revision.
    if not files[P/"ARCHITECTURE.md"].decode().startswith(
        "# joetoo-kwin — architecture and version 1 development contract\n"
    ):
        raise ValueError("Unexpected ARCHITECTURE.md baseline")
    with tempfile.TemporaryDirectory(prefix="joetoo-doc-review-") as temp:
        scratch=Path(temp)
        for path,data in files.items():
            dest=scratch/path
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
        run(["git","init","-q"],scratch)
        run(["git","config","user.name","Document review"],scratch)
        run(["git","config","user.email","review@example.invalid"],scratch)
        run(["git","add","-A"],scratch)
        run(["git","commit","-q","-m","Unmodified input documents"],scratch)

        arch=scratch/P/"ARCHITECTURE.md"
        arch.write_text(update_architecture(arch.read_text()))
        (scratch/P/"README.md").write_text(NEW_README)
        # Preserve Step 1.3b notes byte-for-byte; they are historical evidence.
        run(["git","mv",str(P/"STEP1_3B_PROBE.md"),
             str(P/"archive"/"STEP1_3B_PROBE.md")],scratch)
        archive_index=scratch/P/"archive"/"README.md"
        index=archive_index.read_text()
        index=once(index,
           "- `step1.2a-candidate/` — pre-promotion OpenRC/broker candidate, tests,\n  installer and native validation record",
           "- `step1.2a-candidate/` — pre-promotion OpenRC/broker candidate, tests,\n  installer and native validation record\n"
           "- `STEP1_3B_PROBE.md` — completed Step 1.3b experimental protocol,\n  diagnostic observations and original test instructions")
        archive_index.write_text(index)
        run(["git","add","-A"],scratch)
        diff=run(["git","diff","--cached","--binary","--find-renames=90%"],scratch)
        if not diff:
            raise RuntimeError("Empty draft")
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(diff)
        stat=run(["git","diff","--cached","--stat"],scratch)
        print(stat.decode(),end="")
        print("Draft generated:",output)
        print("Does not modify your source checkout.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,default=Path.cwd())
    parser.add_argument("--output",type=Path,default=Path("/tmp/joetoo-kwin-doc-review.patch"))
    args=parser.parse_args()
    # Accept either the repository root or any subdirectory within it.
    # Resolve the Git root before joining repository-relative document paths.
    supplied_dir = args.repo.resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=supplied_dir, capture_output=True, text=True, check=True)
    repo_root = Path(result.stdout.strip())
    create_patch(repo_root, args.output.resolve())
