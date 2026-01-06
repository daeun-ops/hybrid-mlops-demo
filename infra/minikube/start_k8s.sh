#!/usr/bin/env bash
set -Eeuo pipefail

# ------------------------------------------------------------------------------
# start_minikube.sh
# - idempotent: re-run safe
# - configurable via env/flags
# - supports: start/stop/delete/status/dashboard/tunnel
# ------------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

log()  { printf '[%s] %s\n' "$SCRIPT_NAME" "$*" >&2; }
die()  { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"; }

usage() {
  cat <<'EOF'
Usage:
  ./start_minikube.sh <command> [options]

Commands:
  start        Start (or update) minikube cluster
  stop         Stop cluster
  delete       Delete cluster
  status       Show status
  dashboard    Open dashboard (or print URL with --url)
  tunnel       Run minikube tunnel (requires sudo on many setups)

Options (start):
  -p, --profile <name>        Minikube profile (default: hybrid-mlops)
  -d, --driver <driver>       Driver (default: docker)
  --cpus <n>                  CPUs (default: 4)
  --memory <mb>               Memory in MB (default: 8192)
  --disk <size>               Disk size (default: 40g)
  --k8s-version <version>     Kubernetes version (optional)
  --addons <a,b,c>            Extra addons to enable (optional)
  --no-default-addons         Do not enable default addons
  --docker-env                Configure shell to use minikube docker daemon (prints export commands)
  --wait <seconds>            Wait timeout for node readiness (default: 180)
  -h, --help                  Show help

Environment overrides (same meaning as flags):
  MK_PROFILE, MK_DRIVER, MK_CPUS, MK_MEMORY, MK_DISK, MK_K8S_VERSION, MK_ADDONS, MK_WAIT

Examples:
  ./start_minikube.sh start
  ./start_minikube.sh start -p demo --cpus 6 --memory 12288 --addons ingress,metrics-server
  eval "$(./start_minikube.sh start --docker-env)"
  ./start_minikube.sh dashboard --url
EOF
}

# -----------------------------
# Defaults
# -----------------------------
CMD="${1:-}"
shift || true

PROFILE="${MK_PROFILE:-hybrid-mlops}"
DRIVER="${MK_DRIVER:-docker}"
CPUS="${MK_CPUS:-4}"
MEMORY="${MK_MEMORY:-8192}"
DISK="${MK_DISK:-40g}"
K8S_VERSION="${MK_K8S_VERSION:-}"
MK_ADDONS="${MK_ADDONS:-}"
WAIT_SECS="${MK_WAIT:-180}"

# 프로젝트에서 흔히 쓰는 기본 애드온 (필요 없으면 빼도 됨)
# minikube는 addons, dashboard, ingress, tunnel 등 로컬 개발 편의 기능을 제공  [oai_citation:1‡GitHub](https://github.com/kubernetes/minikube?utm_source=chatgpt.com)
ADDONS_DEFAULT=("metrics-server" "ingress" "dashboard" "storage-provisioner" "default-storageclass")

NO_DEFAULT_ADDONS="0"
PRINT_DOCKER_ENV="0"
DASHBOARD_URL_ONLY="0"

# -----------------------------
# Parse args
# -----------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--profile) PROFILE="$2"; shift 2 ;;
    -d|--driver)  DRIVER="$2"; shift 2 ;;
    --cpus)       CPUS="$2"; shift 2 ;;
    --memory)     MEMORY="$2"; shift 2 ;;
    --disk)       DISK="$2"; shift 2 ;;
    --k8s-version) K8S_VERSION="$2"; shift 2 ;;
    --addons)     MK_ADDONS="$2"; shift 2 ;;
    --no-default-addons) NO_DEFAULT_ADDONS="1"; shift ;;
    --docker-env) PRINT_DOCKER_ENV="1"; shift ;;
    --wait)       WAIT_SECS="$2"; shift 2 ;;
    --url)        DASHBOARD_URL_ONLY="1"; shift ;;
    -h|--help)    usage; exit 0 ;;
    *)
      die "Unknown option: $1 (use --help)"
      ;;
  esac
done

# -----------------------------
# Helpers
# -----------------------------
csv_to_array() {
  local csv="${1:-}"
  [[ -z "$csv" ]] && return 0
  IFS=',' read -r -a _ARR <<<"$csv"
  for x in "${_ARR[@]}"; do
    x="$(echo "$x" | xargs)" # trim
    [[ -n "$x" ]] && echo "$x"
  done
}

wait_for_node_ready() {
  local timeout="$1"
  local start_ts now_ts elapsed
  start_ts="$(date +%s)"

  log "Waiting for node Ready (timeout=${timeout}s)..."
  while true; do
    if kubectl get nodes >/dev/null 2>&1; then
      # Ready 상태 확인
      if kubectl get nodes 2>/dev/null | awk 'NR>1 {print $2}' | grep -qE '^Ready'; then
        log "Node is Ready."
        return 0
      fi
    fi

    now_ts="$(date +%s)"
    elapsed=$((now_ts - start_ts))
    if (( elapsed >= timeout )); then
      kubectl get nodes || true
      die "Timed out waiting for node readiness."
    fi
    sleep 2
  done
}

enable_addons() {
  local -a addons=("$@")
  if [[ "${#addons[@]}" -eq 0 ]]; then
    log "No addons to enable."
    return 0
  fi

  # 현재 활성화된 addons 확인
  # (minikube addons list 는 환경/버전에 따라 출력 포맷이 조금씩 다를 수 있어, 안전하게 enable 재시도도 OK)
  for a in "${addons[@]}"; do
    log "Enabling addon: $a"
    minikube -p "$PROFILE" addons enable "$a" >/dev/null
  done
}

print_docker_env() {
  # 사용자가 eval로 받을 수 있게 export 스니펫 출력
  # 예: eval "$(./start_minikube.sh start --docker-env)"
  minikube -p "$PROFILE" docker-env --shell=bash
}

# -----------------------------
# Main
# -----------------------------
need minikube
need kubectl

case "$CMD" in
  start)
    log "Starting minikube profile='$PROFILE' driver='$DRIVER' cpus='$CPUS' memory='$MEMORY' disk='$DISK'"

    # start args
    args=(
      "-p" "$PROFILE"
      "--driver=$DRIVER"
      "--cpus=$CPUS"
      "--memory=$MEMORY"
      "--disk-size=$DISK"
    )

    if [[ -n "$K8S_VERSION" ]]; then
      args+=("--kubernetes-version=$K8S_VERSION")
    fi

    # Start (idempotent: if already exists, it will reconcile settings where possible)
    minikube start "${args[@]}"

    # Ensure kubectl points to this profile context
    minikube -p "$PROFILE" update-context

    # Addons
    addons_to_enable=()
    if [[ "$NO_DEFAULT_ADDONS" == "0" ]]; then
      addons_to_enable+=("${ADDONS_DEFAULT[@]}")
    fi
    while read -r extra; do
      addons_to_enable+=("$extra")
    done < <(csv_to_array "$MK_ADDONS")

    enable_addons "${addons_to_enable[@]}"

    # Wait for node ready
    wait_for_node_ready "$WAIT_SECS"

    log "Cluster is up."
    log "Context: $(kubectl config current-context)"

    if [[ "$PRINT_DOCKER_ENV" == "1" ]]; then
      print_docker_env
    else
      log "Tip: to build images into minikube docker: eval \"\$(minikube -p $PROFILE docker-env)\""
    fi
    ;;

  stop)
    log "Stopping minikube profile='$PROFILE'"
    minikube -p "$PROFILE" stop
    ;;

  delete)
    log "Deleting minikube profile='$PROFILE'"
    minikube -p "$PROFILE" delete
    ;;

  status)
    minikube -p "$PROFILE" status || true
    kubectl get nodes || true
    ;;

  dashboard)
    if [[ "$DASHBOARD_URL_ONLY" == "1" ]]; then
      minikube -p "$PROFILE" dashboard --url
    else
      minikube -p "$PROFILE" dashboard
    fi
    ;;

  tunnel)
    log "Starting minikube tunnel for profile='$PROFILE' (may require sudo)"
    minikube -p "$PROFILE" tunnel
    ;;

  ""|-h|--help)
    usage
    ;;

  *)
    die "Unknown command: '$CMD' (use --help)"
    ;;
esac
