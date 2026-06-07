taf-gtdbtk 2.7.2-r1

TAFFISH tool app for GTDB-Tk 2.7.2. The default upstream command is gtdbtk.

Important database note:
  GTDB-Tk classification requires the official GTDB-Tk reference package.
  GTDB-Tk 2.7.2 is compatible with the R232 reference package. The reference
  data is about 100 GB and is not bundled. This image expects it at /refdata
  through GTDBTK_DATA_PATH=/refdata/. The wrapper can automatically mount a
  local database to /refdata when a standard path or override is present.

Usage:
  taf-gtdbtk --help
  taf-gtdbtk --version
  taf-gtdbtk --compile
  taf-gtdbtk [gtdbtk options...]
  taf-gtdbtk gtdbtk <subcommand> [args...]
  taf-gtdbtk helper-command [args...]
  taf-gtdbtk -- [option-leading gtdbtk args...]

Wrapper options:
  --help       Show this TAFFISH help text.
  --version    Show the TAFFISH package version.
  --compile    Print generated shell instead of running it.
  --           Pass following option-leading arguments to gtdbtk.

Show upstream help:
  taf-gtdbtk -- --help
  taf-gtdbtk -- --version
  taf-gtdbtk gtdbtk --help
  taf-gtdbtk gtdbtk classify_wf --help
  taf-gtdbtk gtdbtk de_novo_wf --help

Command mode:
  Use explicit command mode for GTDB-Tk subcommands:
    taf-gtdbtk gtdbtk classify_wf ...
    taf-gtdbtk gtdbtk de_novo_wf ...
    taf-gtdbtk gtdbtk check_install

  Avoid writing taf-gtdbtk classify_wf ... directly, because classify_wf is a
  GTDB-Tk subcommand, not a standalone executable in the container.

Prepare and mount reference data:
  The helper installs into the current working directory by default. Create and
  enter the host directory where the database should live, then run it.

  Personal setup:
    mkdir -p ~/.local/share/taffish/databases/gtdbtk
    cd ~/.local/share/taffish/databases/gtdbtk
    taf-gtdbtk gtdbtk-download-r232-db
    taf-gtdbtk gtdbtk check_install

  Administrator or shared-site setup:
    sudo mkdir -p /usr/local/share/taffish/databases/gtdbtk
    sudo chown "$(id -u):$(id -g)" /usr/local/share/taffish/databases/gtdbtk
    cd /usr/local/share/taffish/databases/gtdbtk
    taf-gtdbtk gtdbtk-download-r232-db
    sudo chmod -R a+rX /usr/local/share/taffish/databases/gtdbtk
    taf-gtdbtk gtdbtk check_install

  Helper options:
    taf-gtdbtk gtdbtk-download-r232-db --help

  The helper runs inside the container. The safest pattern is to cd into the
  host database root and run the helper without --db-root. If --db-root is
  used, choose a path already visible to the selected container backend.

  This helper downloads the fixed R232 full package, verifies MD5
  25a59e0352b1fd150c589f56559767d4, creates downloads/, extracts the archive,
  and creates r232 under the current database root. If r232 already exists,
  the helper leaves it unchanged unless --force is used.

  If rootful Docker leaves host files owned by root, fix ownership on the host
  after download:
    sudo chown -R "$(id -u):$(id -g)" <database-root>

  Equivalent manual setup:
    download gtdbtk_r232_data.tar.gz from the official R232 full_package URL,
    verify the MD5 above, extract it, and link the extracted release directory
    to one of the auto-discovery paths below.

Persistent reuse:
  Auto-mount priority:
    1. TAFFISH_GTDBTK_DATA_PATH, if it points to a directory.
    2. ~/.local/share/taffish/databases/gtdbtk/r232
    3. /usr/local/share/taffish/databases/gtdbtk/r232
    4. /opt/taffish/databases/gtdbtk/r232

  If a site already has R232 elsewhere, link it once:
    sudo mkdir -p /usr/local/share/taffish/databases/gtdbtk
    sudo ln -sfn /abs/path/gtdbtk-r232 /usr/local/share/taffish/databases/gtdbtk/r232
    taf-gtdbtk gtdbtk check_install

  For a one-off path, set:
    TAFFISH_GTDBTK_DATA_PATH=/abs/path/gtdbtk-r232 \
    taf-gtdbtk gtdbtk check_install

  Manual mount fallback:
    TAFFISH_GTDBTK_AUTO_MOUNT=0 \
    TAFFISH_DOCKER_RUN_ARGS="-v /abs/path/gtdbtk-r232:/refdata:ro" \
    taf-gtdbtk gtdbtk check_install
    Use TAFFISH_PODMAN_RUN_ARGS for Podman. For Apptainer, use
    TAFFISH_APPTAINER_RUN_ARGS="--bind /abs/path/gtdbtk-r232:/refdata"
    and APPTAINERENV_GTDBTK_DATA_PATH=/refdata/.

  Symlink note:
    auto-mount resolves symlinks to their physical target before binding. If
    that target is not readable or not allowed by Docker Desktop, Podman, or
    Apptainer, set TAFFISH_GTDBTK_DATA_PATH to a backend-visible real path or
    use manual backend args.

Classify genomes:
  taf-gtdbtk gtdbtk classify_wf \
    --genome_dir genomes/ \
    --out_dir gtdbtk-out \
    --cpus 16

Classify a batch file:
  taf-gtdbtk gtdbtk classify_wf \
    --batchfile genomes.tsv \
    --out_dir gtdbtk-out \
    --cpus 16

Memory-conscious pplacer settings:
  taf-gtdbtk gtdbtk classify_wf \
    --genome_dir genomes/ \
    --out_dir gtdbtk-out \
    --cpus 16 \
    --pplacer_cpus 1 \
    --scratch_dir scratch

Packaged commands:
  gtdbtk, gtdbtk-download-r232-db, gtdb_to_ncbi_majority_vote,
  gtdb_to_ncbi_majority_vote.py, prodigal, hmmsearch, hmmalign, hmmscan,
  hmmpress, hmmstat, pplacer, guppy, FastTree, FastTreeMP, skani, python3,
  bash, curl, wget, md5sum, gzip, tar, awk, sed, grep

Common outputs:
  gtdbtk.bac120.summary.tsv, gtdbtk.ar53.summary.tsv, marker outputs,
  alignments, trees, logs, and intermediate files depending on command and
  options. Use --prefix to change the gtdbtk output prefix.

Boundaries:
  The GTDB-Tk R232 reference package, input genomes, genome binning, CheckM2,
  CheckM, dRep, QUAST, BUSCO, and downstream reporting are not bundled.
  The packaged gtdbtk-download-r232-db helper downloads the R232 database only
  when the user runs it explicitly; it requires network access and persistent
  storage. Automatic discovery only mounts an already prepared local R232
  directory.
  Smoke tests are offline and only validate packaging, dependencies, helper
  commands, and the missing-reference-data boundary.

Platform:
  Native container platform is linux/amd64. Docker and Podman runs request
  --platform linux/amd64 from this app. On arm64 hosts this is emulation, not
  native arm64 support.

Docs:
  https://ecogenomics.github.io/GTDBTk/
  https://github.com/Ecogenomics/GTDBTk
