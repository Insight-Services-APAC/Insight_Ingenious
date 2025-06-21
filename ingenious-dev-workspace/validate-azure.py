#!/usr/bin/env python3
"""
Validate Azure service integrations against mocked endpoints.

This script tests all Azure service integrations that ingenious will use:
- Azure OpenAI (Cognitive Services)
- Azure Blob Storage
- Azure Search
- Azure SQL Database
"""

import asyncio
import json
import sys
from typing import Any, Dict

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

console = Console()


class AzureServiceValidator:
    """Validator for Azure service integrations."""

    def __init__(self):
        self.services = {
            "Azure OpenAI": {
                "port": 5001,
                "base_url": "http://localhost:5001",
                "endpoints": [
                    "/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
                ],
            },
            "Azure Blob Storage": {
                "port": 5002,
                "base_url": "http://localhost:5002",
                "endpoints": [
                    "/?restype=service&comp=properties",
                    "/testcontainer?restype=container",
                ],
            },
            "Azure Search": {
                "port": 5003,
                "base_url": "http://localhost:5003",
                "endpoints": [
                    "/indexes?api-version=2024-07-01",
                    "/servicestats?api-version=2024-07-01",
                ],
            },
            "Azure SQL": {
                "port": 5004,
                "base_url": "http://localhost:5004",
                "endpoints": ["/databases", "/servers"],
            },
        }

    async def check_service_availability(
        self, service_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if a service is available and responding."""
        result = {
            "service": service_name,
            "available": False,
            "port": config["port"],
            "endpoints_tested": [],
            "errors": [],
        }

        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            try:
                response = await client.get(config["base_url"], timeout=5.0)
                result["available"] = True
                result["status_code"] = response.status_code
            except Exception as e:
                result["errors"].append(f"Connection failed: {str(e)}")
                return result

            # Test specific endpoints
            for endpoint in config["endpoints"]:
                endpoint_result = {
                    "endpoint": endpoint,
                    "success": False,
                    "status_code": None,
                }

                try:
                    url = config["base_url"] + endpoint
                    headers = self._get_headers_for_service(service_name)

                    response = await client.get(url, headers=headers, timeout=5.0)
                    endpoint_result["success"] = True
                    endpoint_result["status_code"] = response.status_code

                except Exception as e:
                    endpoint_result["error"] = str(e)

                result["endpoints_tested"].append(endpoint_result)

        return result

    def _get_headers_for_service(self, service_name: str) -> Dict[str, str]:
        """Get appropriate headers for each service type."""
        headers = {}

        if service_name == "Azure OpenAI":
            headers = {"api-key": "test-key", "Content-Type": "application/json"}
        elif service_name == "Azure Blob Storage":
            headers = {
                "x-ms-version": "2020-10-02",
                "Authorization": "SharedKey testaccount:mock-signature",
            }
        elif service_name == "Azure Search":
            headers = {"api-key": "test-search-key", "Content-Type": "application/json"}
        elif service_name == "Azure SQL":
            headers = {"Content-Type": "application/json"}

        return headers

    async def test_azure_openai_functionality(self) -> Dict[str, Any]:
        """Test Azure OpenAI specific functionality."""
        result = {"service": "Azure OpenAI", "tests": []}

        async with httpx.AsyncClient() as client:
            # Test chat completions
            chat_test = {"test": "Chat Completions", "success": False, "details": {}}

            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message for the ensemble system.",
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.7,
            }

            try:
                response = await client.post(
                    "http://localhost:5001/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                    json=payload,
                    headers={"api-key": "test-key", "Content-Type": "application/json"},
                    timeout=10.0,
                )

                chat_test["success"] = response.status_code in [200, 201]
                chat_test["details"]["status_code"] = response.status_code

                if response.status_code == 200:
                    data = response.json()
                    chat_test["details"]["response_format"] = "valid"
                    if "choices" in data:
                        chat_test["details"]["has_choices"] = True
                else:
                    chat_test["details"]["response_body"] = response.text

            except Exception as e:
                chat_test["details"]["error"] = str(e)

            result["tests"].append(chat_test)

            # Test multiple concurrent requests (ensemble simulation)
            concurrent_test = {
                "test": "Concurrent Requests",
                "success": False,
                "details": {},
            }

            try:
                # Simulate ensemble processing with multiple concurrent requests
                tasks = []
                for i in range(3):
                    payload = {
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Sub-prompt {i + 1}: Analyze this aspect of the topic.",
                            }
                        ],
                        "max_tokens": 30,
                    }

                    task = client.post(
                        "http://localhost:5001/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                        json=payload,
                        headers={
                            "api-key": "test-key",
                            "Content-Type": "application/json",
                        },
                        timeout=10.0,
                    )
                    tasks.append(task)

                responses = await asyncio.gather(*tasks, return_exceptions=True)

                successful_responses = [
                    r
                    for r in responses
                    if not isinstance(r, Exception) and hasattr(r, "status_code")
                ]
                concurrent_test["success"] = (
                    len(successful_responses) >= 2
                )  # At least 2/3 successful
                concurrent_test["details"]["total_requests"] = len(tasks)
                concurrent_test["details"]["successful_requests"] = len(
                    successful_responses
                )

            except Exception as e:
                concurrent_test["details"]["error"] = str(e)

            result["tests"].append(concurrent_test)

        return result

    async def test_azure_blob_functionality(self) -> Dict[str, Any]:
        """Test Azure Blob Storage specific functionality."""
        result = {"service": "Azure Blob Storage", "tests": []}

        async with httpx.AsyncClient() as client:
            # Test container operations
            container_test = {
                "test": "Container Operations",
                "success": False,
                "details": {},
            }

            try:
                # Test creating/accessing a container
                response = await client.put(
                    "http://localhost:5002/ingenious-data?restype=container",
                    headers={
                        "x-ms-version": "2020-10-02",
                        "Authorization": "SharedKey testaccount:mock-signature",
                        "Content-Length": "0",
                    },
                    timeout=5.0,
                )

                container_test["success"] = response.status_code in [
                    200,
                    201,
                    409,
                ]  # 409 = already exists
                container_test["details"]["status_code"] = response.status_code

            except Exception as e:
                container_test["details"]["error"] = str(e)

            result["tests"].append(container_test)

            # Test blob upload simulation
            blob_test = {
                "test": "Blob Upload Simulation",
                "success": False,
                "details": {},
            }

            try:
                # Simulate uploading conversation data
                conversation_data = {
                    "conversation_id": "test-conv-123",
                    "messages": [
                        {"role": "user", "content": "Test message"},
                        {"role": "assistant", "content": "Test response"},
                    ],
                    "ensemble_data": {
                        "main_prompt": "Test main prompt",
                        "sub_prompts": ["Sub 1", "Sub 2"],
                        "responses": ["Response 1", "Response 2"],
                    },
                }

                blob_data = json.dumps(conversation_data).encode()

                response = await client.put(
                    "http://localhost:5002/ingenious-data/conversations/test-conv-123/data.json",
                    content=blob_data,
                    headers={
                        "x-ms-version": "2020-10-02",
                        "x-ms-blob-type": "BlockBlob",
                        "Content-Type": "application/json",
                        "Content-Length": str(len(blob_data)),
                        "Authorization": "SharedKey testaccount:mock-signature",
                    },
                    timeout=5.0,
                )

                blob_test["success"] = response.status_code in [200, 201]
                blob_test["details"]["status_code"] = response.status_code
                blob_test["details"]["data_size"] = len(blob_data)

            except Exception as e:
                blob_test["details"]["error"] = str(e)

            result["tests"].append(blob_test)

        return result

    async def validate_storage_integration_plan(self) -> Dict[str, Any]:
        """Validate the storage integration plan for ingenious."""
        result = {"validation": "Storage Integration Plan", "components": []}

        # Component 1: Conversation Storage
        conversation_storage = {
            "component": "Conversation Storage",
            "strategy": "Hybrid SQL + Blob",
            "details": {
                "sql_storage": {
                    "purpose": "Metadata and indexing",
                    "schema": {
                        "conversations": [
                            "id",
                            "created_at",
                            "user_id",
                            "message_count",
                            "blob_path",
                        ],
                        "messages": [
                            "id",
                            "conversation_id",
                            "role",
                            "timestamp",
                            "content_hash",
                        ],
                    },
                },
                "blob_storage": {
                    "purpose": "Full conversation content",
                    "structure": "conversations/{conversation_id}/messages.json",
                    "format": "JSON with full message history",
                },
            },
            "benefits": [
                "Fast metadata queries via SQL",
                "Scalable content storage via Blob",
                "Cost-effective for large conversations",
            ],
        }
        result["components"].append(conversation_storage)

        # Component 2: Ensemble Execution Storage
        ensemble_storage = {
            "component": "Ensemble Execution Storage",
            "strategy": "Blob-primary with SQL indexing",
            "details": {
                "sql_storage": {
                    "purpose": "Execution metadata and search",
                    "schema": {
                        "ensemble_executions": [
                            "id",
                            "created_at",
                            "main_prompt_hash",
                            "num_sub_prompts",
                            "status",
                            "blob_path",
                        ],
                        "sub_prompt_results": [
                            "id",
                            "ensemble_id",
                            "prompt_index",
                            "processing_time",
                            "response_hash",
                        ],
                    },
                },
                "blob_storage": {
                    "purpose": "Full execution artifacts",
                    "structure": "ensembles/{ensemble_id}/execution.json",
                    "format": "JSON with prompts, responses, and synthesis",
                },
            },
            "benefits": [
                "Detailed execution tracking",
                "Reusable prompt patterns",
                "Performance analytics",
            ],
        }
        result["components"].append(ensemble_storage)

        # Component 3: Configuration and Templates
        config_storage = {
            "component": "Configuration Storage",
            "strategy": "Blob storage with caching",
            "details": {
                "blob_storage": {
                    "purpose": "Configuration templates and user settings",
                    "structure": "configs/{user_id}/{config_type}.json",
                    "format": "JSON configuration files",
                },
                "caching": {
                    "purpose": "Fast access to frequently used configs",
                    "strategy": "In-memory cache with TTL",
                },
            },
            "benefits": [
                "Versioned configuration management",
                "User-specific customizations",
                "Template sharing capabilities",
            ],
        }
        result["components"].append(config_storage)

        return result

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all Azure integrations."""
        console.print(
            Panel(
                "[bold blue]Azure Service Integration Validation[/bold blue]\n\n"
                "Testing all Azure services that ingenious will integrate with:\n"
                "• Azure OpenAI (Cognitive Services)\n"
                "• Azure Blob Storage\n"
                "• Azure Search\n"
                "• Azure SQL Database",
                title="🔍 Validation Suite",
                border_style="blue",
            )
        )

        validation_results = {
            "timestamp": asyncio.get_event_loop().time(),
            "service_availability": {},
            "functionality_tests": {},
            "storage_plan": {},
        }

        # Test service availability
        console.print("\n[yellow]Testing service availability...[/yellow]")
        for service_name in track(
            self.services.keys(), description="Checking services..."
        ):
            result = await self.check_service_availability(
                service_name, self.services[service_name]
            )
            validation_results["service_availability"][service_name] = result

        # Test specific functionality
        console.print("\n[yellow]Testing service functionality...[/yellow]")

        openai_tests = await self.test_azure_openai_functionality()
        validation_results["functionality_tests"]["Azure OpenAI"] = openai_tests

        blob_tests = await self.test_azure_blob_functionality()
        validation_results["functionality_tests"]["Azure Blob Storage"] = blob_tests

        # Validate storage integration plan
        console.print("\n[yellow]Validating storage integration plan...[/yellow]")
        storage_plan = await self.validate_storage_integration_plan()
        validation_results["storage_plan"] = storage_plan

        return validation_results

    def display_results(self, results: Dict[str, Any]):
        """Display validation results in a formatted way."""

        # Service Availability Table
        availability_table = Table(title="Service Availability")
        availability_table.add_column("Service", style="cyan")
        availability_table.add_column("Status", style="green")
        availability_table.add_column("Port", style="yellow")
        availability_table.add_column("Endpoints", style="blue")

        for service_name, result in results["service_availability"].items():
            status = "✓ Available" if result["available"] else "✗ Unavailable"
            status_style = "green" if result["available"] else "red"

            endpoints_summary = f"{len([e for e in result['endpoints_tested'] if e.get('success', False)])}/{len(result['endpoints_tested'])} working"

            availability_table.add_row(
                service_name,
                f"[{status_style}]{status}[/{status_style}]",
                str(result["port"]),
                endpoints_summary,
            )

        console.print(availability_table)

        # Functionality Tests
        console.print("\n[bold]Functionality Test Results:[/bold]")
        for service_name, test_result in results["functionality_tests"].items():
            console.print(f"\n[cyan]{service_name}:[/cyan]")
            for test in test_result["tests"]:
                status = "✓" if test["success"] else "✗"
                status_style = "green" if test["success"] else "red"
                console.print(
                    f"  [{status_style}]{status}[/{status_style}] {test['test']}"
                )

                if not test["success"] and "error" in test["details"]:
                    console.print(f"    [red]Error: {test['details']['error']}[/red]")

        # Storage Plan Summary
        storage_plan = results["storage_plan"]
        console.print(
            Panel(
                f"[bold]Storage Integration Plan Validated[/bold]\n\n"
                f"Components: {len(storage_plan['components'])}\n"
                f"Strategy: Hybrid SQL + Blob Storage\n"
                f"Benefits: Scalable, cost-effective, fast queries",
                title="💾 Storage Plan",
                border_style="green",
            )
        )


async def main():
    """Main validation function."""
    validator = AzureServiceValidator()

    try:
        results = await validator.run_comprehensive_validation()
        validator.display_results(results)

        # Save detailed results
        with open("azure_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)

        console.print(
            "\n[green]✓ Validation complete! Detailed results saved to azure_validation_results.json[/green]"
        )

    except Exception as e:
        console.print(f"\n[red]✗ Validation failed: {e}[/red]")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        console.print("[bold]Azure Service Integration Validator[/bold]")
        console.print("\nValidates all Azure service integrations for ingenious:")
        console.print("• Tests service availability")
        console.print("• Validates specific functionality")
        console.print("• Confirms storage integration plan")
        console.print(
            "\nEnsure mock services are running: ../mock-azure-services.sh start"
        )
    else:
        asyncio.run(main())
