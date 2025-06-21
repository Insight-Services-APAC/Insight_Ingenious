#!/usr/bin/env python3
"""
Business Analysis Ensemble Example

This example demonstrates a comprehensive business analysis workflow using
the Ingenious framework with hierarchical execution and specialized agents.

Features:
- Hierarchical execution with dependencies
- Domain-specific business analysis agents
- Financial and market analysis
- Strategic recommendation generation

Usage:
    python business-analysis.py "electric vehicle startup" "automotive"
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


class BusinessAnalysisEnsemble:
    """Comprehensive business analysis using specialized AI agents."""

    def __init__(self, azure_config: Dict[str, Any]):
        # Setup services
        self.openai_service = AzureOpenAIService(
            azure_endpoint=azure_config["openai_endpoint"],
            api_key=azure_config["openai_api_key"],
            api_version=azure_config.get("openai_api_version", "2024-06-01"),
            model=azure_config.get("openai_model", "gpt-4"),
        )

        self.storage_service = None
        if azure_config.get("storage_account_url"):
            self.storage_service = AzureBlobStorageService(
                account_url=azure_config["storage_account_url"],
                credential=azure_config.get("storage_credential", "mock-credential"),
            )

        self.ensemble_use_case = EnsembleManagementUseCase(
            llm_service=self.openai_service, storage_service=self.storage_service
        )

    async def create_business_analysis_ensemble(self) -> str:
        """Create a comprehensive business analysis ensemble."""

        # Stage 1: Market and Industry Analysis (Parallel)
        stage1_prompts = [
            {
                "name": "market_size_analyst",
                "content": """
                Analyze the market size and opportunity for {{ business_concept }} in the {{ industry }} industry.

                Provide analysis on:
                1. Total Addressable Market (TAM)
                2. Serviceable Addressable Market (SAM)
                3. Serviceable Obtainable Market (SOM)
                4. Market growth rate and trends
                5. Key market drivers and catalysts

                Business: {{ business_concept }}
                Industry: {{ industry }}
                Geographic focus: {{ geographic_scope }}

                Use specific data points and cite sources where possible.
                Format as a structured market analysis report.
                """,
                "role": "analyst",
                "priority": 1,
            },
            {
                "name": "competitive_landscape_analyst",
                "content": """
                Analyze the competitive landscape for {{ business_concept }} in the {{ industry }} industry.

                Provide analysis on:
                1. Direct competitors (top 5)
                2. Indirect competitors and substitutes
                3. Competitive positioning and differentiation
                4. Market share distribution
                5. Competitive advantages and barriers to entry
                6. Pricing strategies and models

                Business: {{ business_concept }}
                Industry: {{ industry }}

                Create a competitive matrix and positioning analysis.
                """,
                "role": "analyst",
                "priority": 1,
            },
            {
                "name": "regulatory_analyst",
                "content": """
                Analyze the regulatory environment for {{ business_concept }} in the {{ industry }} industry.

                Provide analysis on:
                1. Current regulatory requirements
                2. Upcoming regulatory changes
                3. Compliance costs and complexity
                4. Regulatory risks and opportunities
                5. Industry standards and certifications
                6. Government incentives or restrictions

                Business: {{ business_concept }}
                Industry: {{ industry }}
                Geographic focus: {{ geographic_scope }}

                Focus on regulatory impact on business viability.
                """,
                "role": "specialist",
                "priority": 1,
            },
        ]

        # Stage 2: Business Model Analysis (Depends on Stage 1)
        stage2_prompts = [
            {
                "name": "business_model_analyst",
                "content": """
                Design and analyze potential business models for {{ business_concept }}.

                Based on the market and competitive analysis:
                Market Analysis: {{ market_size_analyst }}
                Competitive Landscape: {{ competitive_landscape_analyst }}
                Regulatory Environment: {{ regulatory_analyst }}

                Analyze:
                1. Revenue model options (subscription, transaction, licensing, etc.)
                2. Cost structure and unit economics
                3. Customer acquisition and retention strategies
                4. Value proposition and differentiation
                5. Scalability and growth potential
                6. Partnership and ecosystem opportunities

                Recommend the most viable business model with justification.
                """,
                "role": "specialist",
                "priority": 2,
                "dependencies": [
                    "market_size_analyst",
                    "competitive_landscape_analyst",
                    "regulatory_analyst",
                ],
            },
            {
                "name": "financial_analyst",
                "content": """
                Create financial projections and analysis for {{ business_concept }}.

                Based on market and business model analysis:
                Market Analysis: {{ market_size_analyst }}
                Business Model: {{ business_model_analyst }}

                Provide:
                1. 5-year revenue projections
                2. Cost structure breakdown
                3. Break-even analysis
                4. Funding requirements and timeline
                5. Key financial metrics and ratios
                6. Sensitivity analysis for key assumptions
                7. Return on investment projections

                Include best-case, base-case, and worst-case scenarios.
                """,
                "role": "analyst",
                "priority": 2,
                "dependencies": ["market_size_analyst", "business_model_analyst"],
            },
        ]

        # Stage 3: Risk and Opportunity Assessment (Depends on Stage 2)
        stage3_prompts = [
            {
                "name": "risk_analyst",
                "content": """
                Conduct comprehensive risk assessment for {{ business_concept }}.

                Based on all previous analyses:
                Market: {{ market_size_analyst }}
                Competition: {{ competitive_landscape_analyst }}
                Regulation: {{ regulatory_analyst }}
                Business Model: {{ business_model_analyst }}
                Financials: {{ financial_analyst }}

                Analyze risks in:
                1. Market risks (demand, competition, disruption)
                2. Operational risks (execution, technology, talent)
                3. Financial risks (funding, cash flow, profitability)
                4. Regulatory risks (compliance, policy changes)
                5. Strategic risks (competitive response, market shifts)

                Rate each risk (High/Medium/Low) and provide mitigation strategies.
                """,
                "role": "critic",
                "priority": 3,
                "dependencies": [
                    "market_size_analyst",
                    "competitive_landscape_analyst",
                    "regulatory_analyst",
                    "business_model_analyst",
                    "financial_analyst",
                ],
            },
            {
                "name": "opportunity_analyst",
                "content": """
                Identify strategic opportunities for {{ business_concept }}.

                Based on comprehensive analysis:
                Market: {{ market_size_analyst }}
                Competition: {{ competitive_landscape_analyst }}
                Business Model: {{ business_model_analyst }}
                Financials: {{ financial_analyst }}

                Identify opportunities in:
                1. Market expansion (geographic, demographic, vertical)
                2. Product/service extensions
                3. Strategic partnerships and alliances
                4. Technology advantages and IP
                5. First-mover advantages
                6. Ecosystem positioning

                Prioritize opportunities by impact and feasibility.
                """,
                "role": "specialist",
                "priority": 3,
                "dependencies": [
                    "market_size_analyst",
                    "competitive_landscape_analyst",
                    "business_model_analyst",
                    "financial_analyst",
                ],
            },
        ]

        # Stage 4: Strategic Recommendations (Final synthesis)
        stage4_prompts = [
            {
                "name": "strategic_advisor",
                "content": """
                Provide strategic recommendations for {{ business_concept }} based on comprehensive analysis.

                Synthesize all analyses:
                Market Analysis: {{ market_size_analyst }}
                Competitive Analysis: {{ competitive_landscape_analyst }}
                Regulatory Analysis: {{ regulatory_analyst }}
                Business Model: {{ business_model_analyst }}
                Financial Projections: {{ financial_analyst }}
                Risk Assessment: {{ risk_analyst }}
                Opportunities: {{ opportunity_analyst }}

                Provide:
                1. Executive Summary (investment thesis)
                2. Strategic Recommendations (top 5)
                3. Implementation roadmap (18-month plan)
                4. Success metrics and KPIs
                5. Resource requirements
                6. Go/No-Go recommendation with rationale

                Present as an executive briefing for investors/stakeholders.
                """,
                "role": "synthesizer",
                "priority": 4,
                "dependencies": [
                    "market_size_analyst",
                    "competitive_landscape_analyst",
                    "regulatory_analyst",
                    "business_model_analyst",
                    "financial_analyst",
                    "risk_analyst",
                    "opportunity_analyst",
                ],
            }
        ]

        # Combine all prompts
        all_prompts = stage1_prompts + stage2_prompts + stage3_prompts + stage4_prompts

        # Create ensemble configuration
        config = await self.ensemble_use_case.create_ensemble_configuration(
            name="comprehensive_business_analysis",
            description="Multi-stage business analysis with market, financial, and strategic assessment",
            main_prompt_template="Conduct comprehensive business analysis for {{ business_concept }} in {{ industry }}",
            sub_prompt_templates=all_prompts,
            reduce_prompt_template="""
            COMPREHENSIVE BUSINESS ANALYSIS REPORT
            =====================================

            Business Concept: {{ business_concept }}
            Industry: {{ industry }}
            Analysis Date: {{ analysis_date }}

            EXECUTIVE SUMMARY & RECOMMENDATIONS:
            {{ strategic_advisor }}

            SUPPORTING ANALYSIS:

            Market Assessment:
            {{ market_size_analyst }}

            Competitive Landscape:
            {{ competitive_landscape_analyst }}

            Financial Projections:
            {{ financial_analyst }}

            Risk Assessment:
            {{ risk_analyst }}

            Strategic Opportunities:
            {{ opportunity_analyst }}

            CONCLUSION:
            This analysis provides a comprehensive view of the business opportunity,
            financial viability, and strategic considerations for decision-making.
            """,
            strategy="hierarchical",  # Sequential execution with dependencies
            max_concurrent_agents=3,  # Allow some parallelism within stages
            timeout_seconds=600,  # Longer timeout for complex analysis
            variables={
                "geographic_scope": "North America",
                "analysis_date": "2024",
                "timeframe": "5 years",
            },
        )

        return config.config_id

    async def analyze_business_opportunity(
        self,
        business_concept: str,
        industry: str,
        geographic_scope: str = "North America",
    ) -> Dict[str, Any]:
        """Conduct comprehensive business analysis."""

        print("🏢 Analyzing Business Opportunity")
        print(f"💡 Concept: {business_concept}")
        print(f"🏭 Industry: {industry}")
        print(f"🌍 Geographic Scope: {geographic_scope}")
        print("\n⚙️  Setting up comprehensive business analysis ensemble...")

        # Create ensemble
        config_id = await self.create_business_analysis_ensemble()

        print("🚀 Executing multi-stage business analysis...")
        print("   This comprehensive analysis may take 10-15 minutes...")
        print("   Stages: Market → Business Model → Risk/Opportunity → Strategy")

        # Execute ensemble
        result = await self.ensemble_use_case.execute_ensemble(
            config_id=config_id,
            variables={
                "business_concept": business_concept,
                "industry": industry,
                "geographic_scope": geographic_scope,
                "analysis_date": "2024",
            },
        )

        return self._process_business_results(result)

    def _process_business_results(self, result) -> Dict[str, Any]:
        """Process and format business analysis results."""

        print("\n" + "=" * 80)
        print("📊 BUSINESS ANALYSIS RESULTS")
        print("=" * 80)

        # Execution metrics
        print(f"\n⏱️  Total Analysis Time: {result.total_duration_seconds:.1f} seconds")
        print(f"✅ Analysis Success Rate: {result.success_rate:.1%}")
        print(f"🤖 Analysts Engaged: {len(result.agent_executions)}")

        # Stage-by-stage results
        stages = {
            1: [
                "market_size_analyst",
                "competitive_landscape_analyst",
                "regulatory_analyst",
            ],
            2: ["business_model_analyst", "financial_analyst"],
            3: ["risk_analyst", "opportunity_analyst"],
            4: ["strategic_advisor"],
        }

        print("\n📋 ANALYSIS BY STAGE:")
        print("-" * 50)

        for stage_num, agent_names in stages.items():
            print(f"\nSTAGE {stage_num}:")
            for agent_name in agent_names:
                agent_exec = next(
                    (
                        exec
                        for exec in result.agent_executions
                        if exec.template_id == agent_name
                    ),
                    None,
                )
                if agent_exec and agent_exec.is_successful:
                    print(f"  ✅ {agent_name.replace('_', ' ').title()}")
                    if (
                        hasattr(agent_exec, "duration_seconds")
                        and agent_exec.duration_seconds
                    ):
                        print(f"     Duration: {agent_exec.duration_seconds:.1f}s")
                else:
                    print(f"  ❌ {agent_name.replace('_', ' ').title()} - FAILED")

        # Key insights summary
        strategic_advisor = next(
            (
                exec
                for exec in result.agent_executions
                if exec.template_id == "strategic_advisor"
            ),
            None,
        )

        if strategic_advisor and strategic_advisor.is_successful:
            print("\n🎯 STRATEGIC RECOMMENDATIONS:")
            print("-" * 50)
            # Show first 500 characters of strategic recommendations
            preview = (
                strategic_advisor.response[:500] + "..."
                if len(strategic_advisor.response) > 500
                else strategic_advisor.response
            )
            print(preview)

        # Final report
        if result.final_result:
            print("\n📄 Access full report in the returned data structure")

        # Return structured results
        analysis_results = {}
        for execution in result.agent_executions:
            if execution.is_successful:
                analysis_results[execution.template_id] = execution.response

        return {
            "business_concept": result.variables.get("business_concept"),
            "industry": result.variables.get("industry"),
            "geographic_scope": result.variables.get("geographic_scope"),
            "analysis_date": result.variables.get("analysis_date"),
            "execution_metrics": {
                "success_rate": result.success_rate,
                "duration_seconds": result.total_duration_seconds,
                "agents_executed": len(result.agent_executions),
            },
            "stage_results": {
                "market_analysis": {
                    "market_size": analysis_results.get("market_size_analyst"),
                    "competitive_landscape": analysis_results.get(
                        "competitive_landscape_analyst"
                    ),
                    "regulatory_environment": analysis_results.get(
                        "regulatory_analyst"
                    ),
                },
                "business_model": {
                    "business_model": analysis_results.get("business_model_analyst"),
                    "financial_projections": analysis_results.get("financial_analyst"),
                },
                "risk_opportunity": {
                    "risk_assessment": analysis_results.get("risk_analyst"),
                    "opportunities": analysis_results.get("opportunity_analyst"),
                },
                "strategic_recommendations": analysis_results.get("strategic_advisor"),
            },
            "full_report": result.final_result,
            "execution_id": result.execution_id,
        }


async def main():
    """Main function for business analysis example."""

    if len(sys.argv) < 3:
        print(
            "Usage: python business-analysis.py <business_concept> <industry> [geographic_scope]"
        )
        print(
            "Example: python business-analysis.py 'AI-powered fitness app' 'health tech' 'North America'"
        )
        sys.exit(1)

    business_concept = sys.argv[1]
    industry = sys.argv[2]
    geographic_scope = sys.argv[3] if len(sys.argv) > 3 else "North America"

    # Azure configuration
    azure_config = {
        "openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "http://localhost:5001"),
        "openai_api_key": os.getenv("AZURE_OPENAI_API_KEY", "mock-key"),
        "openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01"),
        "openai_model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
        "storage_account_url": os.getenv("AZURE_STORAGE_ACCOUNT_URL"),
        "storage_credential": os.getenv("AZURE_STORAGE_CREDENTIAL"),
    }

    try:
        # Create analyzer and run analysis
        analyzer = BusinessAnalysisEnsemble(azure_config)
        result = await analyzer.analyze_business_opportunity(
            business_concept, industry, geographic_scope
        )

        # Save comprehensive results
        output_file = f"business_analysis_{business_concept.replace(' ', '_')}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n💾 Comprehensive analysis saved to: {output_file}")
        print("\n✨ Business analysis complete!")

        # Show investment thesis summary
        if result.get("stage_results", {}).get("strategic_recommendations"):
            print("\n🎯 INVESTMENT THESIS SUMMARY:")
            print("-" * 50)
            strategic_recs = result["stage_results"]["strategic_recommendations"]
            if strategic_recs and len(strategic_recs) > 200:
                # Extract first paragraph as summary
                summary = strategic_recs.split("\n\n")[0]
                print(summary)

    except Exception as e:
        print(f"\n❌ Error during business analysis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
