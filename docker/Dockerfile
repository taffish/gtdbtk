# 官方 2.8.0 内容按不可变 digest 固定；上游暂未提供同名 tag，不跟随 latest。
# digest 保证内容身份，不保证 registry 永久保存。404/限流先诊断来源；不要跳过校验。
FROM --platform=linux/amd64 docker.io/ecogenomic/gtdbtk@sha256:6a5494765450f42e7a636d58dd84a0def26d56a89b049df8ef24956035e56052 AS prepared
USER root
SHELL ["/bin/sh", "-c"]

COPY docker/gtdbtk-download-r232-db docker/gtdbtk_resources.py docker/gtdbtk-smoke /usr/local/bin/
RUN set -eux; \
    chmod 0755 /usr/local/bin/gtdbtk-download-r232-db /usr/local/bin/gtdbtk-smoke; \
    printf '%s\n' '#!/bin/sh' 'exec /usr/local/bin/gtdb_to_ncbi_majority_vote.py "$@"' > /usr/local/bin/gtdb_to_ncbi_majority_vote; \
    chmod 0755 /usr/local/bin/gtdb_to_ncbi_majority_vote; \
    mkdir -p /usr/local/share/licenses/taffish-gtdbtk/build-origin; \
    find /root/.cargo /root/.rustup -type f \( -iname 'license*' -o -iname 'copying*' -o -iname 'notice*' -o -iname 'copyright*' \) \
      -exec cp --parents -t /usr/local/share/licenses/taffish-gtdbtk/build-origin '{}' +; \
    apt-get purge -y build-essential gcc gcc-12 g++ g++-12 cpp cpp-12 \
      binutils binutils-common binutils-x86-64-linux-gnu libc6-dev libc-dev-bin \
      linux-libc-dev libstdc++-12-dev libgcc-12-dev dpkg-dev make patch; \
    rm -rf /root/.cargo /root/.rustup /root/.cache /var/lib/apt/lists/*; \
    find /usr/local/lib -type d -name __pycache__ -prune -exec rm -rf '{}' +

# 官方镜像历史中有构建工具链；只移除明确的开发包，不 autoremove，保留运行库及其许可文本。
# 不重解 apt/pip 依赖；将来更新 digest 时重新核验 Python 源码、依赖、体积及离线三后端。
FROM scratch
COPY --from=prepared / /
COPY docker/licenses/ /usr/local/share/licenses/taffish-gtdbtk/
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=C.UTF-8 GTDBTK_DATA_PATH=/refdata/ PYTHONDONTWRITEBYTECODE=1 \
    TAFFISH_ENV=TAFFISH TAFFISH_NAME=gtdbtk
SHELL ["/bin/sh", "-c"]
ENTRYPOINT []
CMD []
WORKDIR /tmp
# 构建期仅稳定版本/import/help。真实 tiny 和外部资源恢复在 runtime 离线验证，不伪造完整数据库。
RUN gtdbtk-smoke identity && gtdbtk-smoke help
