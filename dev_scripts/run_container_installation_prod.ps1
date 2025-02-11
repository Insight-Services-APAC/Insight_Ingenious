# Add parameters
param (
    [string]$image_name = "localhost/ingen_prod_python",
    [string]$container_name = "ingen_prod_python",
    [string]$dockerfile_path = "./docker/production_images/linux_with_chat_summariser.dockerfile"
)

# Build the Python wheel package using pyproject.toml
Write-Output "Building the Python wheel package using pyproject.toml..."
python -m pip install --upgrade build
python -m build --outdir ./dist
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the wheel package."
    exit 1
}


# Build the Podman image
Write-Output "Start Podman and Building the Podman image..."
podman machine start
podman build -f $dockerfile_path -t $image_name ./
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Podman image."
    exit 1
}

# Run the PowerShell script to start the container
Write-Output "Running the PowerShell script to start the container..."
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    .\run_image_in_podman.ps1 -container_name $container_name -image_name $image_name
} else {
    Write-Output "Error: PowerShell (pwsh) is not installed or not available in the path."
    exit 1
}

# Get the container ID
$container_id = podman ps -q --filter "ancestor=$image_name"
if (-not $container_id) {
    Write-Output "Error: No running container found for the image $image_name."
    exit 1
}
Write-Output "Container ID: $container_id"



# Set the external path and run the Chainlit command
Write-Output "Running Chainlit with the specified extension path..."
podman exec -it $container_id bash -c "ingen_cli chainlit"
if ($LASTEXITCODE -ne 0) {
    Write-Output "Chainlit command execution failed."
    exit 1
}

# SSH into the container
Write-Output "SSH into the container..."
podman exec -it $container_id bash
if ($LASTEXITCODE -ne 0) {
    Write-Output "Exited SSH into the container."
    exit 1
}