# taf-gtdbtk

`taf-gtdbtk` packages GTDB-Tk `2.7.2`, a toolkit for assigning objective
taxonomic classifications to bacterial and archaeal genomes using the Genome
Taxonomy Database. It is commonly used for MAGs, SAGs, isolate genomes, and
microbial phylogenomics after assembly and genome-bin quality control.

This image packages the GTDB-Tk runtime and required software dependencies,
including Prodigal, HMMER, pplacer, FastTree, skani, DendroPy, NumPy, tqdm,
and pydantic. It intentionally does **not** bundle the GTDB-Tk reference data.

## Package Identity

- name: `gtdbtk`
- command: `taf-gtdbtk`
- TAFFISH version: `2.7.2-r1`
- kind: `tool`
- container: `ghcr.io/taffish/gtdbtk:2.7.2-r1`
- native platform: `linux/amd64`
- upstream: GTDB-Tk `2.7.2`
- upstream runtime version: `gtdbtk --version` prints `gtdbtk: version 2.7.2 Copyright 2017 Pierre-Alain Chaumeil, Aaron Mussig and Donovan Parks`
- compatible reference data: GTDB-Tk reference package `R232`

## Installation

```sh
taf install gtdbtk
```

Then run:

```sh
taf-gtdbtk --help
taf-gtdbtk -- --help
taf-gtdbtk gtdbtk --help
```

## Database Boundary

Real GTDB-Tk classification requires the official GTDB-Tk reference package.
GTDB-Tk `2.7.2` is compatible with GTDB-Tk reference data `R232`. The reference
package is about 100 GB and is versioned scientific data, so it belongs in a
persistent project or site database directory instead of the TAFFISH runtime
image.

Inside this container, the default reference path is:

```text
/refdata/
```

GTDB-Tk reads this path through:

```text
GTDBTK_DATA_PATH=/refdata/
```

Download and unpack the database in a persistent host directory using the
official GTDB-Tk documentation. The fixed full R232 package is available as
`gtdbtk_r232_data.tar.gz`; after extraction, mount the unarchived directory
into the container at `/refdata`.

### Container helper for R232 database setup

The image provides a database helper command. By default, it installs into the
current working directory. This is deliberate: TAFFISH maps the user's current
working directory into Docker/Podman containers, so a download started from a
host directory is written back to that same host directory.

The helper creates `downloads/`, stores the fixed R232 full package there,
verifies the official MD5 checksum, extracts the archive, and creates `r232`
as the stable database link.

Personal one-time setup:

```sh
mkdir -p ~/.local/share/taffish/databases/gtdbtk
cd ~/.local/share/taffish/databases/gtdbtk
taf-gtdbtk gtdbtk-download-r232-db
taf-gtdbtk gtdbtk check_install
```

This creates:

```text
~/.local/share/taffish/databases/gtdbtk/r232
```

Future `taf-gtdbtk` runs automatically reuse that path and do not need extra
database arguments.

Administrator or shared-site setup:

```sh
sudo mkdir -p /usr/local/share/taffish/databases/gtdbtk
sudo chown "$(id -u):$(id -g)" /usr/local/share/taffish/databases/gtdbtk
cd /usr/local/share/taffish/databases/gtdbtk
taf-gtdbtk gtdbtk-download-r232-db
sudo chmod -R a+rX /usr/local/share/taffish/databases/gtdbtk
taf-gtdbtk gtdbtk check_install
```

This creates:

```text
/usr/local/share/taffish/databases/gtdbtk/r232
```

The wrapper can auto-mount this shared path for all users when the container
backend is allowed to read it. `/opt/taffish/databases/gtdbtk/r232` is also
checked as an optional site path.

The `chown` command above temporarily hands the empty site directory to the
current admin user for the download step. On managed systems, adjust
ownership/group to local policy after the download and keep read/execute
permissions for users who will run GTDB-Tk.

Use another working directory explicitly:

```sh
mkdir -p /data/db/gtdbtk
cd /data/db/gtdbtk
taf-gtdbtk gtdbtk-download-r232-db
TAFFISH_GTDBTK_DATA_PATH="$PWD/r232" taf-gtdbtk gtdbtk check_install
```

For paths outside the documented auto-discovery locations, use
`TAFFISH_GTDBTK_DATA_PATH` or manual backend bind arguments.

The helper runs inside the container. Arbitrary host absolute paths are not
mounted just because they are passed to `--db-root`; the safest pattern is to
`cd` into the host database root and run the helper without `--db-root`. If
you use `--db-root`, keep it under the current working directory, under `HOME`,
or under another path that the selected container backend already exposes.

Show helper options:

```sh
taf-gtdbtk gtdbtk-download-r232-db --help
```

If `DBROOT/r232` already exists, the helper exits without changing the existing
database. Use `--force` only when you deliberately want to download and extract
again.

On rootful Docker/Linux installations, files written by the container may be
owned by root on the host. If that happens, fix the prepared database root after
the download:

```sh
sudo chown -R "$(id -u):$(id -g)" ~/.local/share/taffish/databases/gtdbtk
```

Use the corresponding site path for a shared database. Rootless Podman and
Docker Desktop may map ownership differently, so follow the local backend and
site policy.

### Manual R232 database setup

If you do not want to run the helper command, the equivalent manual setup is:

```sh
DBROOT="${HOME}/.local/share/taffish/databases/gtdbtk"
mkdir -p "${DBROOT}/downloads"
cd "${DBROOT}/downloads"

curl -L -o gtdbtk_r232_data.tar.gz \
  https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r232_data.tar.gz

printf '25a59e0352b1fd150c589f56559767d4  gtdbtk_r232_data.tar.gz\n' | md5sum -c -

tar -xzf gtdbtk_r232_data.tar.gz -C "${DBROOT}"
```

On macOS, if `md5sum` is unavailable, use `md5 -q gtdbtk_r232_data.tar.gz` and
compare it with the R232 MD5 value above. If the primary mirror is slow or
unavailable, the official documentation also lists this GTDB mirror:

```text
https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/auxillary_files/gtdbtk_package/full_package/gtdbtk_data.tar.gz
```

After extraction, find the created R232 release directory and point the default
TAFFISH path at it:

```sh
find "${DBROOT}" -maxdepth 2 -type d -name 'release*' -print
ln -sfn "${DBROOT}/<extracted-r232-directory>" "${DBROOT}/r232"
taf-gtdbtk gtdbtk check_install
```

Replace `<extracted-r232-directory>` with the directory created by `tar`. The
symlink is only a convenience; a site database directory such as
`/data/db/gtdbtk/release232` or `/srv/db/gtdbtk/r232` is equally valid.

### Automatic database discovery

For day-to-day use, this app can automatically mount a local GTDB-Tk database
to `/refdata`.

Priority:

1. If `TAFFISH_GTDBTK_DATA_PATH` is set and points to a directory, that
   directory is mounted read-only to `/refdata`.
2. Otherwise, the first existing auto-discovery path is mounted read-only to
   `/refdata`:

```text
~/.local/share/taffish/databases/gtdbtk/r232
/usr/local/share/taffish/databases/gtdbtk/r232
/opt/taffish/databases/gtdbtk/r232
```

This means you can prepare a stable user-level or site-level database location
once:

```sh
mkdir -p ~/.local/share/taffish/databases/gtdbtk
ln -s /abs/path/gtdbtk-r232 ~/.local/share/taffish/databases/gtdbtk/r232
taf-gtdbtk gtdbtk check_install
```

For a shared site link:

```sh
sudo mkdir -p /usr/local/share/taffish/databases/gtdbtk
sudo ln -sfn /abs/path/gtdbtk-r232 /usr/local/share/taffish/databases/gtdbtk/r232
taf-gtdbtk gtdbtk check_install
```

The automatic mount follows the directory to its physical path before passing
it to Docker, Podman, or Apptainer. This makes a symlink at the default location
usable as long as the container backend is allowed to read the resolved target.
If the symlink points to a path that Docker Desktop file sharing, Podman, or
Apptainer cannot bind/read, automatic discovery can still fail. In that case,
set `TAFFISH_GTDBTK_DATA_PATH` to the real accessible path or use explicit
backend run args.

Use a one-off custom database path:

```sh
TAFFISH_GTDBTK_DATA_PATH=/abs/path/gtdbtk-r232 \
taf-gtdbtk gtdbtk check_install
```

Disable automatic mounting if you want to provide all backend runtime arguments
yourself:

```sh
TAFFISH_GTDBTK_AUTO_MOUNT=0 \
TAFFISH_DOCKER_RUN_ARGS="-v /abs/path/gtdbtk-r232:/refdata:ro" \
taf-gtdbtk gtdbtk check_install
```

Avoid whitespace in automatically discovered database paths. If a site path is
unusual, use manual backend run args so you can quote and control it directly.

### Manual backend mounts

Manual mounts are still useful on clusters, shared servers, or sites with
special storage policy.

For Docker:

```sh
TAFFISH_CONTAINER_BACKEND=docker \
TAFFISH_DOCKER_RUN_ARGS="-v /abs/path/gtdbtk-r232:/refdata:ro" \
taf-gtdbtk gtdbtk check_install
```

For Podman:

```sh
TAFFISH_CONTAINER_BACKEND=podman \
TAFFISH_PODMAN_RUN_ARGS="-v /abs/path/gtdbtk-r232:/refdata:ro" \
taf-gtdbtk gtdbtk check_install
```

For Apptainer, bind the database directory and provide the environment variable
if your runtime does not preserve the image default:

```sh
TAFFISH_CONTAINER_BACKEND=apptainer \
TAFFISH_APPTAINER_RUN_ARGS="--bind /abs/path/gtdbtk-r232:/refdata" \
APPTAINERENV_GTDBTK_DATA_PATH=/refdata/ \
taf-gtdbtk gtdbtk check_install
```

## Common Usage

Classify genomes in a directory:

```sh
taf-gtdbtk gtdbtk classify_wf \
  --genome_dir genomes/ \
  --out_dir gtdbtk-out \
  --cpus 16
```

Classify a batch file:

```sh
taf-gtdbtk gtdbtk classify_wf \
  --batchfile genomes.tsv \
  --out_dir gtdbtk-out \
  --cpus 16
```

Use scratch storage to reduce pplacer memory pressure:

```sh
mkdir -p scratch gtdbtk-out
taf-gtdbtk gtdbtk classify_wf \
  --genome_dir genomes/ \
  --out_dir gtdbtk-out \
  --cpus 16 \
  --pplacer_cpus 1 \
  --scratch_dir "$PWD/scratch"
```

Run the upstream test after mounting a real database:

```sh
taf-gtdbtk gtdbtk test --out_dir gtdbtk-test --cpus 4
```

## Wrapper and Command Mode

`taf-gtdbtk --help` shows the TAFFISH help in `docs/help.md`.

Use `--` for option-leading upstream calls:

```sh
taf-gtdbtk -- --help
taf-gtdbtk -- --version
```

Use explicit command mode for GTDB-Tk subcommands:

```sh
taf-gtdbtk gtdbtk classify_wf --help
taf-gtdbtk gtdbtk de_novo_wf --help
taf-gtdbtk gtdbtk check_install
```

Do not write `taf-gtdbtk classify_wf ...` directly. With TAFFISH command mode,
`classify_wf` would be treated as a container executable, while GTDB-Tk expects
`classify_wf` to be a subcommand of `gtdbtk`.

## Packaged Commands

The image includes:

- `gtdbtk`
- `gtdbtk-download-r232-db`
- `gtdb_to_ncbi_majority_vote` and `gtdb_to_ncbi_majority_vote.py`
- `prodigal`
- HMMER tools such as `hmmsearch`, `hmmalign`, `hmmscan`, `hmmpress`, `hmmstat`
- `pplacer` and `guppy`
- `FastTree` and `FastTreeMP`
- `skani`
- `python3`, `bash`, `curl`, `wget`, `md5sum`, `gzip`, `tar`, `awk`, `sed`, `grep`

The upstream Docker image ships a broken `gtdb_to_ncbi_majority_vote` console
script entry point. This TAFFISH image keeps the original Python script and
replaces the console wrapper so the helper command works.

## Outputs

`classify_wf` writes GTDB-Tk output under the requested `--out_dir`, including
domain summary tables such as:

- `gtdbtk.bac120.summary.tsv`
- `gtdbtk.ar53.summary.tsv`
- marker, alignment, tree, and log files depending on inputs and options

Use `--prefix` if you want output files to use a prefix other than `gtdbtk`.

## Platform and Resources

This app is native `linux/amd64` only. The official upstream Docker image for
GTDB-Tk `2.7.2` publishes an amd64 manifest. The `src/main.taf` wrapper embeds
Docker/Podman `--platform linux/amd64` runtime args so arm64 hosts can run the
image through amd64 emulation when Docker or Podman supports it. This is not
native arm64 support.

GTDB-Tk is resource intensive. The official documentation lists approximate
requirements of about 100 GB RAM for archaeal classification, about 140 GB RAM
for bacterial classification, and much more for `--full_tree`. The reference
data is about 100 GB. Large runs should be scheduled on a server or HPC node
with sufficient memory, CPU, scratch space, and I/O bandwidth.

## Boundaries

This app is a GTDB-Tk runtime, not a metagenome assembly, binning, dereplication,
or genome-quality workflow. It does not run MEGAHIT, MetaBAT2, CheckM2, CheckM,
dRep, QUAST, BUSCO, or downstream abundance/statistical analysis.

The GTDB-Tk reference package is not bundled. The packaged
`gtdbtk-download-r232-db` helper downloads the R232 database only when the user
runs it explicitly; it requires network access and persistent storage. Offline
classification requires that the compatible R232 reference data has already
been downloaded, unpacked, and made available through automatic discovery,
`TAFFISH_GTDBTK_DATA_PATH`, or a manual backend mount to `/refdata`.

Smoke tests are intentionally offline. They check the runtime version,
subcommand help, Python imports, key dependency versions, the fixed majority
vote helper, and the missing-reference-data boundary. They do not validate
biological classification accuracy on the production R232 database.

## Upstream and Citation

- upstream repository: https://github.com/Ecogenomics/GTDBTk
- upstream documentation: https://ecogenomics.github.io/GTDBTk/
- upstream release/tag: https://github.com/Ecogenomics/GTDBTk/tree/2.7.2
- GTDB-Tk reference data docs: https://ecogenomics.github.io/GTDBTk/installing/index.html#gtdb-tk-reference-data
- publication: Chaumeil et al. 2022, Bioinformatics
- DOI: `10.1093/bioinformatics/btac672`
- publication: Chaumeil et al. 2019, Bioinformatics
- DOI: `10.1093/bioinformatics/btz848`

The TAFFISH app files are Apache-2.0. Upstream GTDB-Tk is GPL-3.0-or-later;
the upstream license applies to the packaged GTDB-Tk runtime and dependencies.
