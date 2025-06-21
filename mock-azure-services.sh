#!/usr/bin/env bash

# Original Azure specs that need transformation
AZURE_SPECS=(
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-06-01/inference.yaml"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/storage/data-plane/Microsoft.BlobStorage/stable/2025-11-05/blob.json"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/search/data-plane/Azure.Search/stable/2024-07-01/searchindex.json"
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/sql/resource-manager/Microsoft.Sql/stable/2021-11-01/Databases.json"
)

# Transformed spec file names
SPEC_FILES=(
  "./specs/azure-openai-transformed.json"
  "./specs/azure-blob-transformed.json"
  "./specs/azure-search-transformed.json"
  "./specs/azure-sql-transformed.json"
)

PORTS=(5001 5002 5003 5004)
PIDS=()

prepare_specs() {
  echo "Preparing Azure specs for Prism..."
  mkdir -p ./specs

  for i in "${!AZURE_SPECS[@]}"; do
    source_url="${AZURE_SPECS[$i]}"
    output_file="${SPEC_FILES[$i]}"

    # Skip if transformed spec already exists and is recent
    if [[ -f "$output_file" && $(find "$output_file" -mtime -1) ]]; then
      echo "- Using cached spec: $output_file"
      continue
    fi

    echo "- Transforming: $source_url"
    echo "  -> $output_file"

    if ! python3 transform-azure-spec.py "$source_url" "$output_file"; then
      echo "  ERROR: Failed to transform spec"
      return 1
    fi
  done
  echo "All specs prepared!"
  echo
}

start_mocks() {
  # First prepare all specs
  if ! prepare_specs; then
    echo "Failed to prepare specs. Exiting."
    exit 1
  fi

  echo "Starting mock servers..."
  for i in "${!SPEC_FILES[@]}"; do
    spec_file="${SPEC_FILES[$i]}"
    port="${PORTS[$i]}"

    if [[ ! -f "$spec_file" ]]; then
      echo "ERROR: Spec file not found: $spec_file"
      continue
    fi

    echo "- Spinning up Prism mock for:"
    echo "    Spec: $spec_file"
    echo "    Port: $port"
    prism mock "$spec_file" --port "$port" &
    pid=$!
    PIDS+=("$pid")
    echo "    -> PID $pid"
  done
  echo
  echo "All mocks started. To stop them, run:"
  echo "  $0 stop"
  echo
  echo "Mock endpoints:"
  echo "  Azure OpenAI:    http://localhost:5001"
  echo "  Azure Blob:      http://localhost:5002"
  echo "  Azure Search:    http://localhost:5003"
  echo "  Azure SQL:       http://localhost:5004"
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

clean_specs() {
  echo "Cleaning transformed specs..."
  rm -rf ./specs
  echo "Cleaned!"
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
  clean)
    clean_specs
    ;;
  prepare)
    prepare_specs
    ;;
  *)
    cat <<USAGE
Usage: $0 {start|stop|restart|clean|prepare}
 start    Prepare specs and spin up all Prism mock servers (ports 5001–5004)
 stop     Kill all running mock-server processes
 restart  stop, then start again
 clean    Remove all transformed spec files
 prepare  Download and transform Azure specs without starting servers

Mock endpoints when running:
 Azure OpenAI:    http://localhost:5001
 Azure Blob:      http://localhost:5002
 Azure Search:    http://localhost:5003
 Azure SQL:       http://localhost:5004
USAGE
    exit 1
    ;;
esac
