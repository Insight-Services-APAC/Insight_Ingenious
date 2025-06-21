#!/usr/bin/env bash

SPECS=(
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-06-01/inference.yaml"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Microsoft.BlobStorage/preview/2020-10-02/blob.json"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/search/data-plane/Azure.Search/stable/2024-07-01/searchindex.json"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/sql/resource-manager/Microsoft.Sql/stable/2021-11-01/Databases.json"
)
PORTS=(5001 5002 5003 5004)
PIDS=()

start_mocks() {
  echo "Starting mock servers..."
  for i in "${!SPECS[@]}"; do
    spec="${SPECS[$i]}"
    port="${PORTS[$i]}"
    echo "- Spinning up Prism mock for:"
    echo "    Spec: $spec"
    echo "    Port: $port"
    prism mock "$spec" --port "$port" &
    pid=$!
    PIDS+=("$pid")
    echo "    -> PID $pid"
  done
  echo
  echo "All mocks started. To stop them, run:"
  echo "  $0 stop"
}

stop_mocks() {
  echo
  echo "Stopping mock servers..."
  for pid in "${PIDS[@]}"; do
    if kill -0 "$pid" &>/dev/null; then
      kill "$pid"
      echo "- Killed PID $pid"
    else
      echo "- PID $pid already stopped"
    fi
  done
  trap - INT TERM EXIT
  echo "All mocks stopped."
}

case "${1:-}" in
  start)
    start_mocks
    ;;
  stop)
    stop_mocks
    ;;
  restart)
    stop_mocks
    start_mocks
    ;;
  *)
    cat <<USAGE
Usage: $0 {start|stop|restart}
 start    Spin up all Prism mock servers (ports 5001–5004)
 stop     Kill all running mock-server processes
 restart  stop, then start again
USAGE
    exit 1
    ;;
esac
