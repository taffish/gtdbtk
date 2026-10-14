gtdbtk 2.8.0-r1

Purpose:
  Classify bacterial and archaeal genomes against an external GTDB R232 reference.

Usage:
  taf-gtdbtk gtdbtk classify_wf --genome_dir genomes --out_dir results --extension fna --cpus 8
  taf-gtdbtk -- --help

Common tasks:
  taf-gtdbtk gtdbtk check_install
  taf-gtdbtk gtdbtk identify --genome_dir genomes --out_dir markers --extension fna --cpus 8
  taf-gtdbtk gtdbtk de_novo_wf --help
  taf-gtdbtk gtdb_to_ncbi_majority_vote --help

Required inputs:
  Genome FASTA files (no whitespace in genome paths) and the R232 reference package.
  Run in a host working directory with writable output and scratch paths.
  Allow roughly 170 GiB installation space; classification may need 100-140 GB RAM.

Common options:
  --extension fna       Match your genome filename extension.
  --cpus 8              CPU threads.
  --scratch_dir scratch Persistent host-bound pplacer workspace.
  --out_dir results    Output directory; avoid resuming across upstream versions.

Key outputs:
  Bacterial/archaeal summary TSVs, marker/ANI results, trees, logs and stage JSON.

Install reference once (choose ONE backend):
  mkdir -p "$HOME/.local/share/taffish/databases/gtdbtk"
  chmod 0755 "$HOME/.local/share/taffish/databases/gtdbtk"
  cd "$HOME/.local/share/taffish/databases/gtdbtk"
  Docker:    TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk-download-r232-db --db-root .
  Podman:    TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk-download-r232-db --db-root .
  Apptainer: TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk-download-r232-db --db-root .
  Final directory is ./r232. Existing databases are verified, never overwritten.
  Use --dry-run to inspect the plan; --source-archive FILE imports the fixed archive.
  Retry a transfer with the same command; checksum-failure recovery is in README.

Choose reference:
  export TAFFISH_GTDBTK_DATA_PATH=/data/gtdb/r232
  Otherwise searches personal ~/.local/share/taffish/databases/gtdbtk/r232,
  then /usr/local/share/taffish/databases/gtdbtk/r232 and /opt/taffish/databases/gtdbtk/r232.
  Prepared references mount read-only. Administrator-installed shared data are reusable.
  TAFFISH_GTDBTK_AUTO_MOUNT=0 disables discovery; invalid explicit paths fail closed.
  Legacy databases without an inventory use the manual bind below; no re-download needed.

Backend-specific use:
  Docker:    TAFFISH_CONTAINER_BACKEND=docker taf-gtdbtk gtdbtk classify_wf --help
  Podman:    TAFFISH_CONTAINER_BACKEND=podman taf-gtdbtk gtdbtk classify_wf --help
  Apptainer: TAFFISH_CONTAINER_BACKEND=apptainer taf-gtdbtk gtdbtk classify_wf --help
  Native linux/amd64 only. Docker/Podman request amd64 automatically.
  ARM Docker/Podman need emulation; ARM-native Apptainer is unsupported (use amd64 Linux).

Manual reference bind (change /data/gtdb/r232 to your host path):
  export TAFFISH_GTDBTK_AUTO_MOUNT=0
  Docker:    TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS='--volume="/data/gtdb/r232:/refdata:ro"' taf-gtdbtk gtdbtk check_install
  Podman:    TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS='--volume="/data/gtdb/r232:/refdata:ro"' taf-gtdbtk gtdbtk check_install
  Apptainer: TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS='--bind="/data/gtdb/r232:/refdata:ro"' taf-gtdbtk gtdbtk check_install
  Keep the same bind for classification. Use quoted manual binds for paths with spaces.

Full integrity audit after installation:
  From the installation parent, use your selected backend:
  taf-gtdbtk gtdbtk-download-r232-db --db-root . --verify
  For a shared auto-mounted reference: taf-gtdbtk gtdbtk-download-r232-db --verify-path /refdata

Immediate notes:
  Missing database errors are expected until R232 is supplied; analysis does not fetch it.
  A tiny smoke test is not complete R232 classification validation.
  Explicit subcommands need "taf-gtdbtk gtdbtk classify_wf", not "taf-gtdbtk classify_wf".

More help:
  taf-gtdbtk gtdbtk-download-r232-db --help
  https://github.com/taffish/gtdbtk

Wrapper options:
  taf-gtdbtk --help       Show this TAFFISH help.
  taf-gtdbtk --version    Show wrapper version.
  taf-gtdbtk --compile    Print generated shell.
  taf-gtdbtk -- --version Show upstream runtime version.
