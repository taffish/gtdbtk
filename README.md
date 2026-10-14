# GTDB-Tk

`gtdbtk` packages upstream GTDB-Tk **2.8.0**, app release **2.8.0-r1**, for TAFFISH.
Command: `taf-gtdbtk`; kind: `tool`; packaging license: Apache-2.0.
Upstream: https://github.com/Ecogenomics/GTDBTk

## What This App Packages

The unmodified official Python implementation assigns bacterial and archaeal genomes
to GTDB taxonomy. This app pins the official OCI content by digest, includes its
runtime programs, fixes only the broken console launcher for the original
`gtdb_to_ncbi_majority_vote.py`, and adds a fixed-resource installer.
It does not bundle the large R232 reference package or download it during classification.

## Scope

Supported upstream commands include classify_wf, de_novo_wf, identify, align, classify,
infer, tree utilities, check_install and test. Invoke subcommands with the executable
name: `taf-gtdbtk gtdbtk classify_wf ...`, not `taf-gtdbtk classify_wf ...`.

The package has no local GUI. Official package entry points/extras and installation
guidance were inspected: KBase is an independent hosted integration, the GTDB website
is a public taxonomy browser, and iTOL is a separate downstream tree service.
`convert_to_itol` remains available; no replacement browser interface is invented.

## Container Contents

- GTDB-Tk 2.8.0, Python 3.11.17 and its official Python dependencies.
- Prodigal 2.6.3, HMMER 3.3.2 (including hmmbuild/hmmsearch/hmmalign/hmmpress),
  pplacer/guppy v1.1.alpha19, FastTree/FastTreeMP 2.1.11 and skani 0.3.2.
- Both majority-vote command names; curl/wget and standard shell/archive utilities.
- `gtdbtk-download-r232-db`: fixed R232 installation, offline import and full verification.
- `gtdbtk-smoke`: packaging probes; tiny fixtures are not a production reference.

## Usage

```sh
taf-gtdbtk -- --help
taf-gtdbtk gtdbtk classify_wf --genome_dir genomes --out_dir results \
  --extension fna --cpus 8 --scratch_dir scratch
taf-gtdbtk gtdbtk check_install
taf-gtdbtk gtdb_to_ncbi_majority_vote --help
```

Run in a host working directory containing the inputs and writable output/scratch
directories. Inputs and reference data should stay read-only; outputs go to the
explicit out_dir. Upstream rejects genome paths containing spaces: use simple paths.

## Backend Usage and Capability Matrix

| Capability | Docker | Podman | Apptainer |
| --- | --- | --- | --- |
| Classification after reference setup | `TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk classify_wf ...` | `TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk classify_wf ...` | `TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk classify_wf ...` |
| Install / verify | Same helper, host-bound working directory | Same helper, host-bound working directory | Same helper, host-bound working directory |
| Automatic reference discovery | Read-only /refdata volume | Read-only /refdata volume | Read-only /refdata bind |
| Native platform | linux/amd64 | linux/amd64 | linux/amd64 |

Docker/Podman automatically request linux/amd64. On an arm64 host this is emulation,
not native ARM support; an engine with working amd64 emulation is required.
The amd64 SIF is not supported natively on ARM Linux. Use an amd64 Linux host instead.
No GPU or service ports are needed. See Testing for measured coverage.

## Command Mode

Non-option-leading arguments use automatic command mode. `taf-gtdbtk python3 ...`
and `taf-gtdbtk gtdbtk classify ...` select an executable in the same container.
Wrapper `--help`/`--version` describe the app; `-- --help`/`-- --version`
reach upstream. `--compile` prints the generated invocation without running it.

## Inputs

| Input | Meaning | Notes |
| --- | --- | --- |
| Genome directory or batchfile | Nucleotide FASTA genomes | Explicit extension; no whitespace in genome paths |
| R232 reference | Fixed external reference package | Required even by several upstream tree commands |
| out_dir / scratch_dir | Persistent results / temporary pplacer workspace | Must be writable host-bound paths |

## Output Notes

Classification writes bacterial/archaeal summary TSVs, marker/ANI results, trees,
logs and stage JSON under out_dir. Version 2.8.0 also records unassigned ANI hits in
`classify/ani_screen/<prefix>.ani_screen_unassigned_hits.tsv.gz`.
It changes species assignment to the closest AF-qualified reference and its ANI
radius, with at most 50 related references. Do not mix stage directories from
different versions: older releases cannot resume 2.8.0 outputs; a pre-2.8 directory
may require ANI to run again. Results need normal scientific quality review.

## Resources, Databases, and Platform

Resource type: one independently fixed full R232/232.0 package, not a selectable
whole catalog. Official URL and MD5 are compiled into the helper:
https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r232_data.tar.gz
MD5: `25a59e0352b1fd150c589f56559767d4`; compressed size: 60,806,405,195 bytes.
Unpacked data are about 98 GB. The installer conservatively reserves 110 GiB for
extraction plus 1 GiB, in addition to a missing compressed cache. Plan roughly
170 GiB of available installation space and sufficient classification RAM (often
100–140 GB, depending on the workflow). The archive is retained for recovery.

Personal installation, with a separate command shown for each backend:

```sh
mkdir -p "$HOME/.local/share/taffish/databases/gtdbtk"
chmod 0755 "$HOME/.local/share/taffish/databases/gtdbtk"
cd "$HOME/.local/share/taffish/databases/gtdbtk"
TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk-download-r232-db --db-root .
# Alternatively:
TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk-download-r232-db --db-root .
TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk-download-r232-db --db-root .
```

Only run one installer, not all three. The physical parent must exist and not be
group/world writable. Container paths are not host installation paths: working in
the destination parent ensures the wrapper binds the actual host directory.
Use a non-symlink parent; macOS aliases such as /var may resolve to /private/var.

On rootful Docker, request your host UID for personally owned outputs:
`export TAFFISH_DOCKER_RUN_ARGS="--user $(id -u):$(id -g)"` before installation.
On rootless Podman, `export TAFFISH_PODMAN_RUN_ARGS='--userns keep-id'` preserves
your user identity. Apptainer normally keeps the invoking user. Do not change
ownership of shared databases merely to run an ordinary analysis.

For **administrator-once shared installation**, an administrator creates a physical
0755 parent such as `/usr/local/share/taffish/databases/gtdbtk`, enters it and invokes
one of the same backend commands using that administrator's installed wrapper and
configured engine. This is an explicit administrative operation, not a sudo feature
of the helper. Ordinary users must be able to traverse all parent directories.
The installed r232 directories are 0755 and files 0644, allowing read-only reuse.
The cache stays 0700 and lock 0600. Users run classification without downloading again.

Automatic selection (first existing candidate, fail closed if invalid):

1. Explicit `TAFFISH_GTDBTK_DATA_PATH` (exact r232 root).
2. `$HOME/.local/share/taffish/databases/gtdbtk/r232`.
3. `/usr/local/share/taffish/databases/gtdbtk/r232`.
4. `/opt/taffish/databases/gtdbtk/r232`.

`TAFFISH_GTDBTK_AUTO_MOUNT=0` disables this; 1 enables it. No database is silently
selected when an explicit path or higher-priority prepared resource is invalid.
Root symlinks are resolved to their physical target; links inside the resource
and group/world-writable resources are rejected. Bind paths with whitespace or
reserved characters need a manually quoted bind. Discovery checks the control
file checksums and file sizes, not every byte of a ~98 GB database on every run.
Use full SHA256 verification after storage transfer or suspected corruption.

```sh
cd "$HOME/.local/share/taffish/databases/gtdbtk"
TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk-download-r232-db --verify --db-root .
TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk-download-r232-db --verify --db-root .
TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk-download-r232-db --verify --db-root .
```

Existing official databases without the new inventory do not require re-download.
Disable automatic discovery, bind them explicitly and use upstream check_install:

```sh
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=docker \
  TAFFISH_DOCKER_RUN_ARGS='--volume="/data/gtdb/r232:/refdata:ro"' \
  taf-gtdbtk gtdbtk check_install
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=podman \
  TAFFISH_PODMAN_RUN_ARGS='--volume="/data/gtdb/r232:/refdata:ro"' \
  taf-gtdbtk gtdbtk check_install
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=apptainer \
  TAFFISH_APPTAINER_RUN_ARGS='--bind="/data/gtdb/r232:/refdata:ro"' \
  taf-gtdbtk gtdbtk check_install
```

The same manual binds work for classify_wf. They are optional site policies, not
required platform flags. The reference is always mounted read-only.

### Installation safety and recovery

The helper verifies fixed archive size and official MD5, records archive SHA256,
unpacks in a private staging directory, rejects traversal/links/devices, writes a
per-file SHA256 inventory and only then atomically publishes r232. A lock prevents
concurrent installation. Existing r232 must pass full verification; it is never
overwritten. There is no --force. Old directory-presence-only behavior is removed.

A failed HTTPS transfer preserves `.r232.cache/<fixed-md5>.part`; rerun the same
command to resume. Do not change the URL or checksum to bypass a mismatch.
A checksum failure keeps the partial for inspection: remove only that named file
after confirming it is corrupt, then retry. A verified cache is reused after an
extraction failure. Normal exceptions clean only the current private staging tree.
A killed process can leave `.r232.stage-*`; inspect ownership and ensure no installer
is active before removing the exact leftover directory. The final r232 remains
absent or untouched, never a partial success. flock is released by process exit.

For offline import, place the exact official archive in the bound working directory:

```sh
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk-download-r232-db --db-root . --source-archive gtdbtk_r232_data.tar.gz
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk-download-r232-db --db-root . --source-archive gtdbtk_r232_data.tar.gz
TAFFISH_GTDBTK_AUTO_MOUNT=0 TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk-download-r232-db --db-root . --source-archive gtdbtk_r232_data.tar.gz
```

Import enforces the same identity and does not accept arbitrary resources. Full
verification may take substantial time. Preserve an old installation and install
in another parent when recovery requires replacement, then explicitly switch.

## Boundaries

The official fixed image is amd64-only. Upstream scientific code and taxonomy are
not modified. GTDB data use CC-BY-SA-4.0 separately from software/package licenses;
preserve attribution and component notices. Normal analysis requires no download.
Upstream --version can attempt a short best-effort PyPI update lookup; it also works
offline. Source identity does not guarantee permanent registry or resource hosting.

## Troubleshooting

- Missing/corrupt reference: prepare R232, verify it, or use an explicit legacy bind.
- Empty r232: no longer accepted as an installed database. Preserve it for inspection.
- Wrong reference or permissions: do not fall back silently; correct the selected path.
- OOM or disk exhaustion: lower concurrency/use an adequately provisioned amd64 host.
- Installer cannot write: ensure --db-root is the actual writable host-bound parent.

## Testing

The unpublished 2.8.0-r1 candidate passed native amd64 validation on xjp:

- 185 independent fresh/offline probes: 31 individual existence checks, combined
  existence and five exact manifest tests, across Docker/Podman normal + read-only
  roots and an actual read-only Apptainer SIF from the same OCI image.
- 73 real-wrapper checks across all three backends: metadata, arguments, real tree
  and HMMER/FastTree tasks, actual host-bound tiny install/recovery/idempotence,
  discovery, override/disable, symlinks, corrupt/extra members, manual fallback,
  read-only reference protection and ordinary-user ownership.
- 16 discovery-order tests in translated private test paths. These do not prove
  real administrator deployment into system directories.
- 18 resource transaction unit tests and 17 unchanged official upstream regression
  tests. All 70 installed GTDB-Tk Python files match the official 2.8.0 source tag.
- Final image 356,599,184 bytes (official base 2,934,344,078 bytes). Build toolchains,
  developer headers and caches are removed; runtime libraries and license notices
  are retained. 372 collected notice/source-pointer files and 137 installed Debian
  copyright files remain. Build-time gates only cover stable identity/import/help.

Docker, Podman and Apptainer are PASS for this packaging scope; backend exception:
none. ARM-host amd64 emulation is not separately validated. No native arm64 image
is claimed. The wrapper's batch inventory checks avoid a subprocess per database
file; full hashes are deliberately an explicit verification task.

A metadata-only fixture is not a complete R232 database. Complete R232 download,
installation, check_install, production classification and genuine root/site
deployment remain not validated: this run deliberately did not acquire the ~98 GB
reference. Tiny tests and upstream unit tests do not prove production accuracy.

## License and Citation

TAFFISH packaging: Apache-2.0. GTDB-Tk: GPL-3.0-or-later. Bundled dependencies retain
their respective licenses and notices. GTDB resources: CC-BY-SA-4.0
(https://gtdb.ecogenomic.org/licenses).

Cite Chaumeil et al. (2022), DOI 10.1093/bioinformatics/btac672, and Chaumeil et al.
(2019), DOI 10.1093/bioinformatics/btz848, plus the GTDB release used.
