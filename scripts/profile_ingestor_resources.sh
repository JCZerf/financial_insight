#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/data/logs"
mkdir -p "${LOG_DIR}"

RUN_ID="$(date +%Y%m%d_%H%M%S)"
CONTAINER_NAME="ingestor_profile_${RUN_ID}"
STATS_FILE="${LOG_DIR}/docker_stats_${RUN_ID}.csv"

echo "Iniciando diagnostico do ingestor..."
echo "Container: ${CONTAINER_NAME}"
echo "CSV de metricas: ${STATS_FILE}"

cd "${PROJECT_ROOT}"

docker compose up -d postgres >/dev/null

CONTAINER_ID="$(
  docker compose run -d --name "${CONTAINER_NAME}" ingestor \
    python3 fundamentus_fii_ingestor/main.py "$@"
)"

echo "container_id=${CONTAINER_ID}"
echo "timestamp,cpu_percent,mem_usage,mem_percent,pids" >"${STATS_FILE}"

while docker ps -q --filter "id=${CONTAINER_ID}" | grep -q .; do
  TS="$(date -Iseconds)"
  STATS_LINE="$(
    docker stats --no-stream \
      --format '{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.PIDs}}' \
      "${CONTAINER_ID}" 2>/dev/null || true
  )"
  if [[ -n "${STATS_LINE}" ]]; then
    echo "${TS},${STATS_LINE}" >>"${STATS_FILE}"
  fi
  sleep 1
done

EXIT_CODE="$(docker inspect "${CONTAINER_ID}" --format '{{.State.ExitCode}}')"
OOM_KILLED="$(docker inspect "${CONTAINER_ID}" --format '{{.State.OOMKilled}}')"
ERROR_TEXT="$(docker inspect "${CONTAINER_ID}" --format '{{.State.Error}}')"

MAX_MEM_PERC="$(
  awk -F',' 'NR>1 {gsub("%","",$4); if (($4+0)>max) max=$4+0} END {printf "%.2f", max+0}' "${STATS_FILE}"
)"
MAX_CPU_PERC="$(
  awk -F',' 'NR>1 {gsub("%","",$2); if (($2+0)>max) max=$2+0} END {printf "%.2f", max+0}' "${STATS_FILE}"
)"

echo
echo "Resumo do teste:"
echo "- ExitCode: ${EXIT_CODE}"
echo "- OOMKilled: ${OOM_KILLED}"
echo "- Max CPU (%): ${MAX_CPU_PERC}"
echo "- Max Mem (%): ${MAX_MEM_PERC}"
echo "- Erro do runtime: ${ERROR_TEXT:-<vazio>}"
echo "- CSV completo: ${STATS_FILE}"

if [[ "${OOM_KILLED}" == "true" ]]; then
  echo
  echo "Diagnostico: o container foi morto por falta de memoria (OOM)."
fi

docker logs "${CONTAINER_ID}" --tail 80 || true
docker rm "${CONTAINER_ID}" >/dev/null 2>&1 || true
