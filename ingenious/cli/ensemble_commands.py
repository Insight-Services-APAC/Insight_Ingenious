"""
CLI commands for prompt ensemble management and execution.

This module provides command-line interface for creating, managing,
and executing prompt ensembles with the ingenious framework.
"""

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ingenious.external_integrations.infrastructure.blob_storage_service import (
    AzureBlobStorageService,
)
from ingenious.external_integrations.infrastructure.openai_service import (
    AzureOpenAIService,
)
from ingenious.prompt_management.application.ensemble_use_cases import (
    EnsembleManagementUseCase,
)

# Initialize CLI app
ensemble_app = typer.Typer(
    name="ensemble",
    help="Manage and execute prompt ensembles",
    rich_markup_mode="rich",
)

console = Console()


def setup_services() -> tuple[
    EnsembleManagementUseCase, AzureOpenAIService, AzureBlobStorageService
]:
    """Setup services for ensemble operations."""
    # This would typically be injected via dependency injection
    # For now, we'll use placeholder configuration

    # Azure OpenAI Service
    openai_service = AzureOpenAIService(
        azure_endpoint="https://localhost:5001",  # Mock endpoint
        api_key="mock-key",
        api_version="2024-06-01",
        model="gpt-4",
    )

    # Azure Blob Storage Service
    blob_service = AzureBlobStorageService(
        account_url="https://localhost:5002",  # Mock endpoint
        credential="mock-credential",
    )

    # Ensemble Management Use Case
    ensemble_use_case = EnsembleManagementUseCase(
        llm_service=openai_service,
        storage_service=blob_service,
    )

    return ensemble_use_case, openai_service, blob_service


@ensemble_app.command("create")
def create_ensemble(
    name: str = typer.Argument(..., help="Name of the ensemble configuration"),
    config_file: Path = typer.Option(
        None, "--config", "-c", help="JSON file with ensemble configuration"
    ),
    strategy: str = typer.Option(
        "parallel", help="Execution strategy: parallel, sequential, hierarchical"
    ),
    max_agents: int = typer.Option(5, help="Maximum concurrent agents"),
    timeout: int = typer.Option(300, help="Timeout in seconds"),
) -> None:
    """Create a new prompt ensemble configuration."""

    async def _create_ensemble():
        ensemble_use_case, _, _ = setup_services()

        if config_file and config_file.exists():
            # Load configuration from file
            with open(config_file, "r") as f:
                config_data = json.load(f)

            config = await ensemble_use_case.create_ensemble_configuration(
                name=name,
                description=config_data.get("description", ""),
                main_prompt_template=config_data["main_prompt_template"],
                sub_prompt_templates=config_data["sub_prompt_templates"],
                reduce_prompt_template=config_data["reduce_prompt_template"],
                strategy=strategy,
                max_concurrent_agents=max_agents,
                timeout_seconds=timeout,
                variables=config_data.get("variables", {}),
            )

            console.print(
                f"[green]✓[/green] Created ensemble configuration: {config.config_id}"
            )
            console.print(f"Name: {config.name}")
            console.print(f"Strategy: {config.strategy}")
            console.print(f"Sub-prompts: {len(config.sub_prompt_templates)}")
        else:
            console.print(
                "[red]Error:[/red] Configuration file not found or not provided"
            )
            raise typer.Exit(1)

    asyncio.run(_create_ensemble())


@ensemble_app.command("create-predefined")
def create_predefined_ensemble(
    ensemble_type: str = typer.Argument(..., help="Type of predefined ensemble"),
    name: str = typer.Argument(..., help="Name for the ensemble"),
    description: str = typer.Option("", help="Description of the ensemble"),
) -> None:
    """Create a predefined ensemble configuration."""

    valid_types = [
        "multi_perspective_analysis",
        "document_review",
        "code_review",
        "research_synthesis",
    ]

    if ensemble_type not in valid_types:
        console.print(
            f"[red]Error:[/red] Invalid ensemble type. Valid types: {', '.join(valid_types)}"
        )
        raise typer.Exit(1)

    async def _create_predefined():
        ensemble_use_case, _, _ = setup_services()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating predefined ensemble...", total=None)

            config = await ensemble_use_case.create_predefined_ensemble(
                ensemble_type=ensemble_type,
                name=name,
                description=description or f"Predefined {ensemble_type} ensemble",
            )

            progress.update(task, completed=True)

        console.print(
            f"[green]✓[/green] Created predefined ensemble: {config.config_id}"
        )
        console.print(f"Name: {config.name}")
        console.print(f"Type: {ensemble_type}")
        console.print(f"Strategy: {config.strategy}")
        console.print(f"Sub-prompts: {len(config.sub_prompt_templates)}")

    asyncio.run(_create_predefined())


@ensemble_app.command("execute")
def execute_ensemble(
    config_id: str = typer.Argument(..., help="Configuration ID to execute"),
    input_file: Path = typer.Option(
        None, "--input", "-i", help="JSON file with input data"
    ),
    input_text: str = typer.Option(None, "--text", "-t", help="Input text directly"),
    store_results: bool = typer.Option(True, help="Store execution results"),
    output_file: Path = typer.Option(
        None, "--output", "-o", help="Save results to file"
    ),
) -> None:
    """Execute a prompt ensemble."""

    async def _execute_ensemble():
        ensemble_use_case, _, _ = setup_services()

        # Prepare input data
        input_data = {}
        if input_file and input_file.exists():
            with open(input_file, "r") as f:
                input_data = json.load(f)
        elif input_text:
            input_data = {"content": input_text}
        else:
            console.print(
                "[red]Error:[/red] Must provide either --input file or --text"
            )
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Executing ensemble...", total=None)

            try:
                result = await ensemble_use_case.execute_ensemble(
                    config_id=config_id,
                    input_data=input_data,
                    store_results=store_results,
                )

                progress.update(task, completed=True)

                # Display results
                console.print("[green]✓[/green] Ensemble execution completed")
                console.print(f"Execution ID: {result.execution_id}")
                console.print(f"Config: {result.config_name}")

                # Show execution stats
                stats = result.execution_stats
                stats_table = Table(title="Execution Statistics")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="green")

                stats_table.add_row(
                    "Duration", f"{stats.get('total_duration_seconds', 0):.2f}s"
                )
                stats_table.add_row(
                    "Successful Agents", str(stats.get("successful_agents", 0))
                )
                stats_table.add_row("Failed Agents", str(stats.get("failed_agents", 0)))
                stats_table.add_row(
                    "Total Tokens", str(stats.get("total_tokens_used", 0))
                )

                console.print(stats_table)

                # Show final response
                console.print(
                    Panel(
                        result.final_response,
                        title="Final Response",
                        border_style="green",
                    )
                )

                # Save to file if requested
                if output_file:
                    output_data = {
                        "execution_id": result.execution_id,
                        "config_name": result.config_name,
                        "final_response": result.final_response,
                        "agent_responses": result.agent_responses,
                        "execution_stats": result.execution_stats,
                        "created_at": result.created_at.isoformat(),
                    }

                    with open(output_file, "w") as f:
                        json.dump(output_data, f, indent=2)

                    console.print(f"[green]✓[/green] Results saved to: {output_file}")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Error:[/red] Ensemble execution failed: {e}")
                raise typer.Exit(1)

    asyncio.run(_execute_ensemble())


@ensemble_app.command("list")
def list_ensembles(
    limit: int = typer.Option(10, help="Maximum number of configurations to list"),
    prefix: str = typer.Option(None, help="Filter by name prefix"),
) -> None:
    """List available ensemble configurations."""

    async def _list_ensembles():
        ensemble_use_case, _, _ = setup_services()

        configs = await ensemble_use_case.list_ensemble_configurations(
            prefix=prefix,
            limit=limit,
        )

        if not configs:
            console.print("[yellow]No ensemble configurations found[/yellow]")
            return

        table = Table(title="Ensemble Configurations")
        table.add_column("Config ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Strategy", style="magenta")
        table.add_column("Created", style="blue")
        table.add_column("Size", style="yellow")

        for config in configs:
            table.add_row(
                config["config_id"][:8] + "...",
                config["name"],
                config["strategy"],
                config.get("created_at", "Unknown")[:10],
                f"{config.get('size', 0)} bytes",
            )

        console.print(table)

    asyncio.run(_list_ensembles())


@ensemble_app.command("get")
def get_ensemble(
    config_id: str = typer.Argument(..., help="Configuration ID to retrieve"),
    show_templates: bool = typer.Option(
        False, "--templates", help="Show template details"
    ),
) -> None:
    """Get details of a specific ensemble configuration."""

    async def _get_ensemble():
        ensemble_use_case, _, _ = setup_services()

        config = await ensemble_use_case.get_ensemble_configuration(config_id)

        if not config:
            console.print(f"[red]Error:[/red] Configuration not found: {config_id}")
            raise typer.Exit(1)

        # Display configuration details
        console.print(f"[bold]Configuration: {config.name}[/bold]")
        console.print(f"ID: {config.config_id}")
        console.print(f"Description: {config.description or 'No description'}")
        console.print(f"Strategy: {config.strategy}")
        console.print(f"Max Agents: {config.max_concurrent_agents}")
        console.print(f"Timeout: {config.timeout_seconds}s")
        console.print(f"Sub-prompts: {len(config.sub_prompt_templates)}")
        console.print(f"Created: {config.created_at}")

        if show_templates:
            console.print("\n[bold]Sub-prompt Templates:[/bold]")
            for i, template in enumerate(config.sub_prompt_templates, 1):
                console.print(f"\n[cyan]{i}. {template.name}[/cyan]")
                console.print(f"   Role: {template.role}")
                console.print(f"   Priority: {template.priority}")
                if template.dependencies:
                    console.print(
                        f"   Dependencies: {', '.join(template.dependencies)}"
                    )
                console.print(f"   Content: {template.content[:100]}...")

    asyncio.run(_get_ensemble())


@ensemble_app.command("executions")
def list_executions(
    config_id: str = typer.Option(None, help="Filter by configuration ID"),
    status: str = typer.Option(None, help="Filter by status"),
    limit: int = typer.Option(10, help="Maximum number of executions to list"),
) -> None:
    """List ensemble executions."""

    async def _list_executions():
        ensemble_use_case, _, _ = setup_services()

        executions = await ensemble_use_case.list_ensemble_executions(
            config_id=config_id,
            status=status,
            limit=limit,
        )

        if not executions:
            console.print("[yellow]No executions found[/yellow]")
            return

        table = Table(title="Ensemble Executions")
        table.add_column("Execution ID", style="cyan", no_wrap=True)
        table.add_column("Config ID", style="green", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Started", style="blue")
        table.add_column("Agents", style="yellow")

        for execution in executions:
            table.add_row(
                execution["execution_id"][:8] + "...",
                execution["config_id"][:8] + "...",
                execution["status"],
                execution.get("started_at", "Unknown")[:16],
                execution.get("agent_count", "0"),
            )

        console.print(table)

    asyncio.run(_list_executions())


@ensemble_app.command("result")
def get_result(
    execution_id: str = typer.Argument(..., help="Execution ID to retrieve"),
    show_agents: bool = typer.Option(
        False, "--agents", help="Show individual agent responses"
    ),
    output_file: Path = typer.Option(None, "--output", "-o", help="Save to file"),
) -> None:
    """Get results of a specific ensemble execution."""

    async def _get_result():
        ensemble_use_case, _, _ = setup_services()

        result = await ensemble_use_case.get_ensemble_result(execution_id)

        if not result:
            console.print(f"[red]Error:[/red] Result not found: {execution_id}")
            raise typer.Exit(1)

        # Display result
        console.print("[bold]Execution Result[/bold]")
        console.print(f"Execution ID: {result.execution_id}")
        console.print(f"Config: {result.config_name}")
        console.print(f"Created: {result.created_at}")

        # Stats
        stats = result.execution_stats
        console.print("\n[bold]Statistics:[/bold]")
        console.print(f"Duration: {stats.get('total_duration_seconds', 0):.2f}s")
        console.print(f"Successful Agents: {stats.get('successful_agents', 0)}")
        console.print(f"Failed Agents: {stats.get('failed_agents', 0)}")
        console.print(f"Total Tokens: {stats.get('total_tokens_used', 0)}")

        # Final response
        console.print(
            Panel(result.final_response, title="Final Response", border_style="green")
        )

        # Individual agent responses
        if show_agents and result.agent_responses:
            console.print("\n[bold]Individual Agent Responses:[/bold]")
            for role, response in result.agent_responses.items():
                console.print(
                    Panel(response, title=f"Agent: {role}", border_style="blue")
                )

        # Save to file
        if output_file:
            output_data = {
                "execution_id": result.execution_id,
                "config_name": result.config_name,
                "final_response": result.final_response,
                "agent_responses": result.agent_responses,
                "execution_stats": result.execution_stats,
                "created_at": result.created_at.isoformat(),
            }

            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)

            console.print(f"[green]✓[/green] Result saved to: {output_file}")

    asyncio.run(_get_result())


@ensemble_app.command("sample-config")
def generate_sample_config(
    output_file: Path = typer.Argument(
        ..., help="Output file for sample configuration"
    ),
    ensemble_type: str = typer.Option("basic", help="Type of sample: basic, advanced"),
) -> None:
    """Generate a sample ensemble configuration file."""

    if ensemble_type == "basic":
        sample_config = {
            "description": "Basic multi-agent analysis ensemble",
            "main_prompt_template": "Analyze the following content: {{ content }}",
            "sub_prompt_templates": [
                {
                    "name": "analytical_review",
                    "content": "Provide an analytical review of: {{ content }}\n\nFocus on logical structure, evidence, and methodology.",
                    "role": "analyzer",
                    "priority": 1,
                    "dependencies": [],
                    "variables": {},
                },
                {
                    "name": "critical_evaluation",
                    "content": "Critically evaluate: {{ content }}\n\nIdentify assumptions, biases, and limitations.",
                    "role": "critic",
                    "priority": 1,
                    "dependencies": [],
                    "variables": {},
                },
            ],
            "reduce_prompt_template": "Synthesize the following analyses:\n\n{% for role, response in agent_responses.items() %}\n**{{ role }}:** {{ response }}\n\n{% endfor %}\n\nProvide a balanced, comprehensive summary.",
            "variables": {"analysis_depth": "detailed", "focus_area": "general"},
        }
    else:  # advanced
        sample_config = {
            "description": "Advanced hierarchical ensemble with dependencies",
            "main_prompt_template": "Conduct comprehensive analysis of: {{ content }}",
            "sub_prompt_templates": [
                {
                    "name": "initial_analysis",
                    "content": "Perform initial analysis of: {{ content }}\n\nIdentify key themes and topics.",
                    "role": "analyzer",
                    "priority": 1,
                    "dependencies": [],
                    "variables": {},
                },
                {
                    "name": "deep_dive_review",
                    "content": "Based on initial findings, conduct detailed review of: {{ content }}\n\nFocus on areas identified in initial analysis.",
                    "role": "specialist",
                    "priority": 2,
                    "dependencies": ["initial_analysis"],
                    "variables": {},
                },
                {
                    "name": "critical_synthesis",
                    "content": "Synthesize findings from analysis and review: {{ content }}\n\nCreate coherent conclusions.",
                    "role": "synthesizer",
                    "priority": 3,
                    "dependencies": ["initial_analysis", "deep_dive_review"],
                    "variables": {},
                },
            ],
            "reduce_prompt_template": "Create final synthesis from hierarchical analysis:\n\n{% for role, response in agent_responses.items() %}\n**{{ role }}:** {{ response }}\n\n{% endfor %}\n\nGenerate comprehensive final report with conclusions and recommendations.",
            "variables": {
                "analysis_depth": "comprehensive",
                "synthesis_style": "academic",
            },
        }

    with open(output_file, "w") as f:
        json.dump(sample_config, f, indent=2)

    console.print(f"[green]✓[/green] Sample configuration saved to: {output_file}")
    console.print(f"Type: {ensemble_type}")
    console.print(
        "Edit the file to customize the configuration, then use 'create' command to deploy it."
    )


if __name__ == "__main__":
    ensemble_app()
