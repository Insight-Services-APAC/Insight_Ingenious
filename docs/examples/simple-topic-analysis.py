#!/usr/bin/env python3
"""
Simple Topic Analysis Example

This example demonstrates how to create and execute a basic prompt ensemble
that analyzes any topic from multiple perspectives using the Ingenious framework.

Features:
- Parallel execution strategy for speed
- Multiple specialized agent roles
- Template variables for flexibility
- Comprehensive result aggregation

Usage:
    python simple-topic-analysis.py "artificial intelligence in healthcare"
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict

# Configure environment
os.environ.setdefault("INGENIOUS_WORKING_DIR", ".")

try:
    from ingenious.external_integrations.infrastructure.blob_storage_service import (
        AzureBlobStorageService,
    )
    from ingenious.external_integrations.infrastructure.openai_service import (
        AzureOpenAIService,
    )
    from ingenious.prompt_management.application.ensemble_use_cases import (
        EnsembleManagementUseCase,
    )
except ImportError as e:
    print(f"Error: Failed to import Ingenious modules: {e}")
    print("Please install with: pip install insight-ingenious")
    sys.exit(1)


class SimpleTopicAnalyzer:
    """Simple topic analyzer using Ingenious ensemble."""

    def __init__(self, azure_config: Dict[str, Any]):
        # Setup Azure OpenAI service
        self.openai_service = AzureOpenAIService(
            azure_endpoint=azure_config["openai_endpoint"],
            api_key=azure_config["openai_api_key"],
            api_version=azure_config.get("openai_api_version", "2024-06-01"),
            model=azure_config.get("openai_model", "gpt-4"),
        )

        # Setup storage service (optional)
        self.storage_service = None
        if azure_config.get("storage_account_url"):
            self.storage_service = AzureBlobStorageService(
                account_url=azure_config["storage_account_url"],
                credential=azure_config.get("storage_credential", ""),
            )

        # Create ensemble use case
        self.ensemble_use_case = EnsembleManagementUseCase(
            llm_service=self.openai_service, storage_service=self.storage_service
        )

    async def create_analysis_ensemble(self) -> str:
        """Create a topic analysis ensemble configuration."""

        # Define sub-prompt templates
        sub_prompts = [
            {
                "name": "strengths_analyzer",
                "content": """
                Analyze the positive aspects and benefits of {{ topic }}.

                Focus on:
                - Key advantages and strengths
                - Potential benefits to stakeholders
                - Success factors and opportunities
                - Supporting evidence and examples

                Topic: {{ topic }}
                Analysis depth: {{ depth }}

                Provide a structured analysis with specific examples.
                """,
                "role": "analyzer",
                "priority": 1,
            },
            {
                "name": "challenges_critic",
                "content": """
                Critically examine the challenges and potential issues with {{ topic }}.

                Focus on:
                - Limitations and constraints
                - Potential risks and concerns
                - Implementation challenges
                - Areas needing improvement

                Topic: {{ topic }}
                Analysis depth: {{ depth }}

                Provide constructive criticism with specific examples.
                """,
                "role": "critic",
                "priority": 1,
            },
            {
                "name": "market_specialist",
                "content": """
                Analyze {{ topic }} from a market and industry perspective.

                Focus on:
                - Market size and trends
                - Industry adoption patterns
                - Competitive landscape
                - Economic implications

                Topic: {{ topic }}
                Analysis depth: {{ depth }}

                Provide market insights with data-driven analysis.
                """,
                "role": "specialist",
                "priority": 1,
            },
            {
                "name": "future_trends_specialist",
                "content": """
                Analyze future trends and implications for {{ topic }}.

                Focus on:
                - Emerging trends and developments
                - Future growth potential
                - Long-term implications
                - Predicted evolution

                Topic: {{ topic }}
                Analysis depth: {{ depth }}

                Provide forward-looking insights and predictions.
                """,
                "role": "specialist",
                "priority": 1,
            },
            {
                "name": "synthesis_agent",
                "content": """
                Synthesize all the analyses into a comprehensive overview.

                Based on the following analyses:

                Strengths & Benefits:
                {{ strengths_analyzer }}

                Challenges & Concerns:
                {{ challenges_critic }}

                Market Analysis:
                {{ market_specialist }}

                Future Trends:
                {{ future_trends_specialist }}

                Create a balanced synthesis that:
                1. Integrates all perspectives
                2. Identifies key themes and patterns
                3. Provides actionable insights
                4. Offers balanced recommendations

                Present as an executive summary with clear sections.
                """,
                "role": "synthesizer",
                "priority": 2,
                "dependencies": [
                    "strengths_analyzer",
                    "challenges_critic",
                    "market_specialist",
                    "future_trends_specialist",
                ],
            },
        ]

        # Create ensemble configuration
        config = await self.ensemble_use_case.create_ensemble_configuration(
            name="topic_analysis",
            description="Comprehensive multi-perspective topic analysis",
            main_prompt_template="Analyze {{ topic }} comprehensively from multiple angles with {{ depth }} depth.",
            sub_prompt_templates=sub_prompts,
            reduce_prompt_template="""
            Based on the comprehensive analysis below, provide a final executive summary:

            {{ synthesis_agent }}

            Final Summary Requirements:
            1. Key findings (3-5 bullet points)
            2. Overall assessment (positive/negative/neutral)
            3. Top 3 recommendations
            4. Confidence level in the analysis

            Keep the summary concise but comprehensive.
            """,
            strategy="parallel",  # Run independent analyses in parallel
            max_concurrent_agents=4,  # Allow 4 agents to run simultaneously
            timeout_seconds=300,
            variables={"depth": "detailed", "focus": "comprehensive"},
        )

        return config.config_id

    async def analyze_topic(
        self, topic: str, depth: str = "detailed"
    ) -> Dict[str, Any]:
        """Analyze a topic using the ensemble."""

        print(f"🔍 Analyzing topic: '{topic}'")
        print(f"📊 Analysis depth: {depth}")
        print("⚙️  Setting up ensemble...")

        # Create ensemble configuration
        config_id = await self.create_analysis_ensemble()

        print("🚀 Executing ensemble analysis...")
        print("   This may take a few minutes for comprehensive analysis...")

        # Execute ensemble
        result = await self.ensemble_use_case.execute_ensemble(
            config_id=config_id, variables={"topic": topic, "depth": depth}
        )

        # Process and display results
        return self._process_results(result)

    def _process_results(self, result) -> Dict[str, Any]:
        """Process and format ensemble results."""

        print("\n" + "=" * 60)
        print("📈 ANALYSIS RESULTS")
        print("=" * 60)

        # Execution metrics
        print(f"\n⏱️  Execution Time: {result.total_duration_seconds:.2f} seconds")
        print(f"✅ Success Rate: {result.success_rate:.1%}")
        print(f"🤖 Agents Executed: {len(result.agent_executions)}")

        if hasattr(result, "total_token_usage"):
            print(f"🔢 Total Tokens: {result.total_token_usage}")

        # Individual agent results
        print("\n📋 INDIVIDUAL AGENT INSIGHTS:")
        print("-" * 40)

        for execution in result.agent_executions:
            if execution.is_successful and execution.response:
                print(f"\n🔸 {execution.agent_role.value.title()} Analysis:")
                # Show first 300 characters as preview
                preview = (
                    execution.response[:300] + "..."
                    if len(execution.response) > 300
                    else execution.response
                )
                print(f"   {preview}")

                if (
                    hasattr(execution, "duration_seconds")
                    and execution.duration_seconds
                ):
                    print(f"   ⏱️ Duration: {execution.duration_seconds:.2f}s")
            else:
                print(f"\n❌ {execution.agent_role.value.title()} Analysis: FAILED")
                if execution.error:
                    print(f"   Error: {execution.error}")

        # Final synthesized result
        if result.final_result:
            print("\n🎯 FINAL SYNTHESIS:")
            print("-" * 40)
            print(result.final_result)

        # Return structured data
        return {
            "topic": result.variables.get("topic"),
            "success_rate": result.success_rate,
            "duration_seconds": result.total_duration_seconds,
            "agent_results": {
                exec.agent_role.value: exec.response
                for exec in result.agent_executions
                if exec.is_successful
            },
            "final_synthesis": result.final_result,
            "execution_id": result.execution_id,
        }


async def main():
    """Main function to run the topic analysis example."""

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python simple-topic-analysis.py <topic> [depth]")
        print("Example: python simple-topic-analysis.py 'renewable energy' detailed")
        sys.exit(1)

    topic = sys.argv[1]
    depth = sys.argv[2] if len(sys.argv) > 2 else "detailed"

    # Azure configuration (replace with your values)
    azure_config = {
        "openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "http://localhost:5001"),
        "openai_api_key": os.getenv("AZURE_OPENAI_API_KEY", "mock-key"),
        "openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01"),
        "openai_model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
        "storage_account_url": os.getenv("AZURE_STORAGE_ACCOUNT_URL"),
        "storage_credential": os.getenv("AZURE_STORAGE_CREDENTIAL"),
    }

    # Validate configuration
    if not azure_config["openai_endpoint"] or not azure_config["openai_api_key"]:
        print("❌ Error: Azure OpenAI configuration missing!")
        print("Set these environment variables:")
        print("  AZURE_OPENAI_ENDPOINT")
        print("  AZURE_OPENAI_API_KEY")
        print("  AZURE_OPENAI_MODEL (optional)")
        sys.exit(1)

    try:
        # Create analyzer and run analysis
        analyzer = SimpleTopicAnalyzer(azure_config)
        result = await analyzer.analyze_topic(topic, depth)

        # Optionally save results to file
        output_file = f"analysis_{topic.replace(' ', '_')}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_file}")
        print("\n✨ Analysis complete!")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
