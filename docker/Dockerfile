ARG GTDBTK_BASE_PLATFORM=linux/amd64
FROM --platform=${GTDBTK_BASE_PLATFORM} docker.io/ecogenomic/gtdbtk:2.7.2@sha256:78ebc71b8de215fab505ed2b960f08df4923980d9acfcd0088996df483652cb0

LABEL maintainer="taffish@163.com"

USER root

ENV GTDBTK_DATA_PATH=/refdata/

ENTRYPOINT []
CMD []
SHELL ["/bin/sh", "-c"]

COPY docker/gtdbtk-download-r232-db /usr/local/bin/gtdbtk-download-r232-db

RUN set -eux; \
    chmod 0755 /usr/local/bin/gtdbtk-download-r232-db; \
    printf '%s\n' \
      '#!/bin/sh' \
      'exec /usr/local/bin/gtdb_to_ncbi_majority_vote.py "$@"' \
      > /usr/local/bin/gtdb_to_ncbi_majority_vote; \
    chmod 0755 /usr/local/bin/gtdb_to_ncbi_majority_vote

RUN set -eux; \
    gtdbtk --version 2>&1 | grep -Fx "gtdbtk: version 2.7.2 Copyright 2017 Pierre-Alain Chaumeil, Aaron Mussig and Donovan Parks" >/dev/null; \
    gtdbtk --help 2>&1 | grep -F "GTDB-Tk v2.7.2" >/dev/null; \
    gtdbtk classify_wf --help 2>&1 | grep -F "usage: gtdbtk classify_wf" >/dev/null; \
    gtdbtk de_novo_wf --help 2>&1 | grep -F "usage: gtdbtk de_novo_wf" >/dev/null; \
    gtdbtk identify --help 2>&1 | grep -F "usage: gtdbtk identify" >/dev/null; \
    gtdbtk align --help 2>&1 | grep -F "usage: gtdbtk align" >/dev/null; \
    gtdbtk check_install --help 2>&1 | grep -F "GTDB-Tk version package to test for compatibility" >/dev/null; \
    gtdbtk test --help 2>&1 | grep -F "usage: gtdbtk test" >/dev/null; \
    python3 -c 'import gtdbtk, dendropy, numpy, tqdm, pydantic; assert gtdbtk.__version__ == "2.7.2"'; \
    gtdb_to_ncbi_majority_vote --help 2>&1 | grep -F "GTDB to NCBI Majority Vote v0.2.1" >/dev/null; \
    gtdb_to_ncbi_majority_vote.py --help 2>&1 | grep -F "Translate GTDB to NCBI classification via majority vote" >/dev/null; \
    gtdbtk-download-r232-db --help 2>&1 | grep -F "Download and install the GTDB-Tk R232 reference package" >/dev/null; \
    tmp=/tmp/taf-gtdbtk-r232-db; \
    rm -rf "${tmp}"; \
    mkdir -p "${tmp}"; \
    (cd "${tmp}" && gtdbtk-download-r232-db --dry-run 2>&1 | grep -F "Download directory: ${tmp}/downloads" >/dev/null); \
    mkdir -p "${tmp}/existing/r232"; \
    gtdbtk-download-r232-db --db-root "${tmp}/existing" 2>&1 | grep -F "Existing DBROOT/r232 directory found: ${tmp}/existing/r232" >/dev/null; \
    gtdbtk-download-r232-db --dry-run --db-root /tmp/taf-gtdbtk-r232-db-explicit 2>&1 | grep -F "Expected MD5: 25a59e0352b1fd150c589f56559767d4" >/dev/null; \
    rm -rf "${tmp}"; \
    prodigal -v 2>&1 | grep -F "Prodigal V2.6.3" >/dev/null; \
    hmmsearch -h 2>&1 | grep -F "# HMMER 3.3.2" >/dev/null; \
    hmmalign -h 2>&1 | grep -F "# HMMER 3.3.2" >/dev/null; \
    pplacer --version 2>&1 | grep -Fx "v1.1.alpha19-0-g807f6f3" >/dev/null; \
    guppy --version 2>&1 | grep -Fx "v1.1.alpha19-0-g807f6f3" >/dev/null; \
    FastTree 2>&1 | grep -F "FastTree Version 2.1.11" >/dev/null; \
    FastTreeMP 2>&1 | grep -F "FastTree Version 2.1.11" >/dev/null; \
    skani -V 2>&1 | grep -Fx "skani 0.3.1" >/dev/null

RUN set -eux; \
    tmp=/tmp/taf-gtdbtk-no-db; \
    rm -rf "${tmp}"; \
    mkdir -p "${tmp}/genomes"; \
    printf '>tiny\nATGAAATAA\n' > "${tmp}/genomes/tiny.fna"; \
    if gtdbtk classify_wf --genome_dir "${tmp}/genomes" --out_dir "${tmp}/out" --cpus 1 >"${tmp}/run.log" 2>&1; then \
      cat "${tmp}/run.log" >&2; \
      exit 1; \
    fi; \
    grep -F "The GTDB-Tk reference data does not exist or is corrupted." "${tmp}/run.log" >/dev/null; \
    grep -F "GTDBTK_DATA_PATH=/refdata/" "${tmp}/run.log" >/dev/null; \
    test ! -e "${tmp}/out/gtdbtk.bac120.summary.tsv"; \
    rm -rf "${tmp}"

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=gtdbtk
