#!/usr/bin/env python3
"""
Interactive demo of the Prompt Ensemble Agent functionality.

This script demonstrates the core ingenious Prompt Ensemble Agent capabilities:
1. Accept a main prompt and generate N sub-prompts using Jinja templating
2. Process each sub-prompt via Azure Cognitive Services & Azure OpenAI
3. Aggregate and synthesize outputs using a configurable "reduce prompt"
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

import httpx
from jinja2 import Template
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.syntax import Syntax

console = Console()


class PromptEnsembleAgent:
    """Core Prompt Ensemble Agent implementation."""

    def __init__(self, azure_openai_endpoint: str = "http://localhost:5001"):
        self.azure_openai_endpoint = azure_openai_endpoint
        self.api_version = "2024-06-01"

    async def generate_sub_prompts(
        self, main_prompt: str, sub_prompt_template: str, aspects: List[str]
    ) -> List[str]:
        """Generate sub-prompts from the main prompt using Jinja templating."""
        template = Template(sub_prompt_template)

        sub_prompts = []
        for aspect in aspects:
            sub_prompt = template.render(
                main_prompt=main_prompt,
                aspect=aspect,
                topic=main_prompt,  # Also available as 'topic' for flexibility
            )
            sub_prompts.append(sub_prompt)

        return sub_prompts

    async def process_prompt_with_azure_openai(
        self, prompt: str, max_tokens: int = 150
    ) -> str:
        """Process a single prompt using Azure OpenAI."""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            try:
                response = await client.post(
                    f"{self.azure_openai_endpoint}/openai/deployments/gpt-4/chat/completions?api-version={self.api_version}",
                    json=payload,
                    headers={"api-key": "test-key", "Content-Type": "application/json"},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "No response")
                    )
                else:
                    # For demo purposes with mocks, return simulated response
                    return f"[MOCK RESPONSE] Analysis for: {prompt[:50]}..."

            except Exception as e:
                console.print(f"[red]Error processing prompt: {e}[/red]")
                return f"[ERROR] Failed to process: {prompt[:30]}..."

    async def process_sub_prompts_concurrently(
        self, sub_prompts: List[str]
    ) -> List[str]:
        """Process multiple sub-prompts concurrently."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Processing sub-prompts...", total=len(sub_prompts)
            )

            async def process_with_progress(prompt: str) -> str:
                result = await self.process_prompt_with_azure_openai(prompt)
                progress.advance(task)
                return result

            tasks = [process_with_progress(prompt) for prompt in sub_prompts]
            responses = await asyncio.gather(*tasks)

        return responses

    async def synthesize_responses(
        self, responses: List[str], reduce_prompt_template: str
    ) -> str:
        """Synthesize multiple responses using a reduce prompt."""
        template = Template(reduce_prompt_template)

        # Format responses for the reduce prompt
        formatted_responses = "\n\n".join(
            [f"Analysis {i + 1}: {response}" for i, response in enumerate(responses)]
        )

        reduce_prompt = template.render(
            responses=formatted_responses, num_responses=len(responses)
        )

        return await self.process_prompt_with_azure_openai(
            reduce_prompt, max_tokens=300
        )

    async def run_ensemble(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete ensemble process."""
        main_prompt = config["main_prompt"]
        sub_prompt_template = config["sub_prompt_template"]
        reduce_prompt_template = config["reduce_prompt_template"]
        aspects = config["aspects"]

        console.print(
            Panel(
                f"[bold blue]Main Prompt:[/bold blue]\n{main_prompt}",
                title="🎯 Starting Ensemble",
            )
        )

        # Step 1: Generate sub-prompts
        console.print("\n[yellow]Step 1: Generating sub-prompts...[/yellow]")
        sub_prompts = await self.generate_sub_prompts(
            main_prompt, sub_prompt_template, aspects
        )

        for i, prompt in enumerate(sub_prompts, 1):
            console.print(f"  [cyan]{i}.[/cyan] {prompt}")

        # Step 2: Process sub-prompts concurrently
        console.print(
            "\n[yellow]Step 2: Processing sub-prompts with Azure OpenAI...[/yellow]"
        )
        responses = await self.process_sub_prompts_concurrently(sub_prompts)

        # Step 3: Display individual responses
        console.print("\n[yellow]Step 3: Individual responses received:[/yellow]")
        for i, (prompt, response) in enumerate(zip(sub_prompts, responses), 1):
            console.print(
                Panel(
                    f"[bold]Prompt:[/bold] {prompt}\n\n[bold]Response:[/bold] {response}",
                    title=f"Response {i}",
                )
            )

        # Step 4: Synthesize final result
        console.print("\n[yellow]Step 4: Synthesizing final result...[/yellow]")
        final_result = await self.synthesize_responses(
            responses, reduce_prompt_template
        )

        console.print(
            Panel(
                final_result, title="🎉 Final Synthesized Result", border_style="green"
            )
        )

        return {
            "main_prompt": main_prompt,
            "sub_prompts": sub_prompts,
            "responses": responses,
            "final_result": final_result,
            "config": config,
        }


def get_predefined_configs() -> Dict[str, Dict[str, Any]]:
    """Get predefined ensemble configurations."""
    return {
        "1": {
            "name": "Technology Impact Analysis",
            "main_prompt": "Analyze the impact of artificial intelligence on modern society",
            "sub_prompt_template": "Examine the {{ aspect }} implications of {{ main_prompt }}. Provide specific examples and evidence.",
            "reduce_prompt_template": "Synthesize the following analyses into a comprehensive overview:\n\n{{ responses }}\n\nProvide a balanced conclusion that addresses all perspectives.",
            "aspects": ["economic", "social", "ethical", "technological"],
        },
        "2": {
            "name": "Business Strategy Analysis",
            "main_prompt": "Evaluate the strategy for entering the renewable energy market",
            "sub_prompt_template": "Analyze {{ main_prompt }} from a {{ aspect }} perspective. Include key considerations and recommendations.",
            "reduce_prompt_template": "Create an executive summary based on these strategic analyses:\n\n{{ responses }}\n\nProvide actionable recommendations and next steps.",
            "aspects": ["financial", "competitive", "regulatory", "operational"],
        },
        "3": {
            "name": "Research Topic Exploration",
            "main_prompt": "Explore the potential of quantum computing for drug discovery",
            "sub_prompt_template": "Investigate {{ main_prompt }} focusing on {{ aspect }} factors. Provide current state and future possibilities.",
            "reduce_prompt_template": "Compile these research findings into a coherent analysis:\n\n{{ responses }}\n\nIdentify key opportunities and challenges.",
            "aspects": [
                "technical feasibility",
                "current applications",
                "market potential",
                "scientific challenges",
            ],
        },
    }


async def interactive_demo():
    """Run an interactive demo of the Prompt Ensemble Agent."""
    console.print(
        Panel(
            "[bold blue]Welcome to the Ingenious Prompt Ensemble Agent Demo![/bold blue]\n\n"
            "This demo showcases the core ensemble functionality:\n"
            "• Generate sub-prompts using Jinja templating\n"
            "• Process prompts via Azure OpenAI (mocked)\n"
            "• Synthesize results with configurable reduce logic",
            title="🚀 Prompt Ensemble Agent",
            border_style="blue",
        )
    )

    agent = PromptEnsembleAgent()

    # Check if mock services are available
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:5001", timeout=5.0)
        console.print("[green]✓ Mock Azure OpenAI service detected[/green]")
    except Exception:
        console.print(
            "[yellow]⚠ Mock Azure OpenAI service not detected - using fallback responses[/yellow]"
        )

    console.print("\n[bold]Choose a demo configuration:[/bold]")

    configs = get_predefined_configs()
    for key, config in configs.items():
        console.print(f"  [cyan]{key}.[/cyan] {config['name']}")
    console.print("  [cyan]4.[/cyan] Custom configuration")

    choice = Prompt.ask(
        "\nSelect configuration", choices=["1", "2", "3", "4"], default="1"
    )

    if choice in configs:
        config = configs[choice]
        console.print(f"\n[green]Selected: {config['name']}[/green]")
    else:
        # Custom configuration
        console.print("\n[bold]Create custom configuration:[/bold]")
        main_prompt = Prompt.ask("Main prompt")
        sub_prompt_template = Prompt.ask(
            "Sub-prompt template (use {{ aspect }} and {{ main_prompt }})",
            default="Analyze {{ main_prompt }} from a {{ aspect }} perspective",
        )
        reduce_prompt_template = Prompt.ask(
            "Reduce prompt template (use {{ responses }})",
            default="Synthesize these analyses: {{ responses }}",
        )
        aspects_input = Prompt.ask(
            "Aspects (comma-separated)", default="technical,business,social,ethical"
        )
        aspects = [aspect.strip() for aspect in aspects_input.split(",")]

        config = {
            "name": "Custom Configuration",
            "main_prompt": main_prompt,
            "sub_prompt_template": sub_prompt_template,
            "reduce_prompt_template": reduce_prompt_template,
            "aspects": aspects,
        }

    # Display configuration
    config_json = json.dumps({k: v for k, v in config.items() if k != "name"}, indent=2)
    syntax = Syntax(config_json, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Configuration", border_style="yellow"))

    # Confirm and run
    if (
        Prompt.ask(
            "\nRun ensemble with this configuration?", choices=["y", "n"], default="y"
        )
        == "y"
    ):
        result = await agent.run_ensemble(config)

        # Save results
        console.print("\n[green]Ensemble completed successfully![/green]")
        if Prompt.ask("Save results to file?", choices=["y", "n"], default="n") == "y":
            filename = (
                f"ensemble_result_{config['name'].lower().replace(' ', '_')}.json"
            )
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Results saved to {filename}[/green]")


def cli_demo():
    """Command-line interface for the demo."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            console.print("[bold]Prompt Ensemble Agent Demo[/bold]")
            console.print("\nUsage:")
            console.print("  python demo-ensemble.py              # Interactive demo")
            console.print("  python demo-ensemble.py --help       # Show this help")
            return

    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    cli_demo()
