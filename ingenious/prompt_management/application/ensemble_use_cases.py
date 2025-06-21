"""
Use cases for managing prompt ensembles and orchestrating their execution.

This module provides high-level business logic for creating, managing,
and executing prompt ensembles with comprehensive error handling and monitoring.
"""

import logging
from typing import Any, Dict, List, Optional

from ingenious.external_integrations.domain.services import ILLMService
from ingenious.external_integrations.infrastructure.blob_storage_service import (
    AzureBlobStorageService,
)
from ingenious.prompt_management.application.ensemble_service import (
    EnsembleOrchestrationService,
)
from ingenious.prompt_management.domain.ensemble import (
    AgentRole,
    EnsembleConfiguration,
    EnsemblePromptTemplate,
    EnsembleResult,
    EnsembleStrategy,
)
from ingenious.shared.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)


class EnsembleManagementUseCase:
    """Use case for managing prompt ensemble configurations and executions."""

    def __init__(
        self,
        llm_service: ILLMService,
        storage_service: AzureBlobStorageService,
    ):
        self.llm_service = llm_service
        self.storage_service = storage_service
        self.orchestration_service = EnsembleOrchestrationService(llm_service)

    async def create_ensemble_configuration(
        self,
        name: str,
        description: str,
        main_prompt_template: str,
        sub_prompt_templates: List[Dict[str, Any]],
        reduce_prompt_template: str,
        strategy: str = "parallel",
        max_concurrent_agents: int = 5,
        timeout_seconds: int = 300,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create and validate a new ensemble configuration."""
        logger.info(f"Creating ensemble configuration: {name}")

        # Validate strategy
        try:
            ensemble_strategy = EnsembleStrategy(strategy)
        except ValueError:
            raise ValidationError(f"Invalid strategy: {strategy}")

        # Parse and validate sub-prompt templates
        parsed_templates = []
        for template_data in sub_prompt_templates:
            try:
                # Validate required fields
                if "name" not in template_data or "content" not in template_data:
                    raise ValidationError(
                        "Templates must have 'name' and 'content' fields"
                    )

                # Parse role
                role = template_data.get("role", "specialist")
                try:
                    agent_role = AgentRole(role)
                except ValueError:
                    raise ValidationError(f"Invalid agent role: {role}")

                template = EnsemblePromptTemplate(
                    name=template_data["name"],
                    content=template_data["content"],
                    role=agent_role,
                    priority=template_data.get("priority", 1),
                    dependencies=template_data.get("dependencies", []),
                    variables=template_data.get("variables", {}),
                )
                parsed_templates.append(template)

            except Exception as e:
                raise ValidationError(
                    f"Invalid template '{template_data.get('name', 'unknown')}': {e}"
                )

        # Validate template dependencies for hierarchical strategy
        if ensemble_strategy == EnsembleStrategy.HIERARCHICAL:
            self._validate_template_dependencies(parsed_templates)

        # Create configuration
        config = EnsembleConfiguration(
            name=name,
            description=description,
            strategy=ensemble_strategy,
            main_prompt_template=main_prompt_template,
            sub_prompt_templates=parsed_templates,
            reduce_prompt_template=reduce_prompt_template,
            max_concurrent_agents=max_concurrent_agents,
            timeout_seconds=timeout_seconds,
            variables=variables or {},
        )

        # Store configuration
        await self.storage_service.store_configuration(config)

        logger.info(f"Created ensemble configuration: {config.config_id}")
        return config

    def _validate_template_dependencies(
        self, templates: List[EnsemblePromptTemplate]
    ) -> None:
        """Validate template dependencies for hierarchical execution."""
        template_ids = {t.template_id for t in templates}

        for template in templates:
            for dep_id in template.dependencies:
                if dep_id not in template_ids:
                    raise ValidationError(
                        f"Template '{template.name}' depends on non-existent template ID: {dep_id}"
                    )

            # Check for circular dependencies (basic check)
            if template.template_id in template.dependencies:
                raise ValidationError(
                    f"Template '{template.name}' cannot depend on itself"
                )

    async def execute_ensemble(
        self,
        config_id: str,
        input_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        store_results: bool = True,
    ) -> EnsembleResult:
        """Execute a prompt ensemble and optionally store the results."""
        logger.info(f"Executing ensemble: {config_id}")

        # Load configuration
        config = await self.storage_service.load_configuration(config_id)
        if not config:
            raise BusinessLogicError(f"Configuration not found: {config_id}")

        try:
            # Execute ensemble
            result = await self.orchestration_service.execute_ensemble(
                config, input_data, user_context
            )

            # Store results if requested
            if store_results:
                await self.storage_service.store_result(result)
                logger.info(f"Stored ensemble result: {result.execution_id}")

            return result

        except Exception as e:
            logger.exception(f"Ensemble execution failed: {e}")
            raise BusinessLogicError(f"Ensemble execution failed: {e}")

    async def get_ensemble_configuration(
        self, config_id: str
    ) -> Optional[EnsembleConfiguration]:
        """Retrieve an ensemble configuration by ID."""
        return await self.storage_service.load_configuration(config_id)

    async def list_ensemble_configurations(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List available ensemble configurations."""
        return await self.storage_service.list_configurations(prefix, limit)

    async def get_ensemble_result(self, execution_id: str) -> Optional[EnsembleResult]:
        """Retrieve an ensemble result by execution ID."""
        return await self.storage_service.load_result(execution_id)

    async def list_ensemble_executions(
        self,
        config_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List ensemble executions with optional filtering."""
        return await self.storage_service.list_executions(config_id, status, limit)

    async def create_predefined_ensemble(
        self,
        ensemble_type: str,
        name: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create a predefined ensemble configuration for common use cases."""
        logger.info(f"Creating predefined ensemble: {ensemble_type}")

        if ensemble_type == "multi_perspective_analysis":
            return await self._create_multi_perspective_analysis(
                name, description, variables
            )
        elif ensemble_type == "document_review":
            return await self._create_document_review_ensemble(
                name, description, variables
            )
        elif ensemble_type == "code_review":
            return await self._create_code_review_ensemble(name, description, variables)
        elif ensemble_type == "research_synthesis":
            return await self._create_research_synthesis_ensemble(
                name, description, variables
            )
        else:
            raise ValidationError(f"Unknown predefined ensemble type: {ensemble_type}")

    async def _create_multi_perspective_analysis(
        self,
        name: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create a multi-perspective analysis ensemble."""
        sub_templates = [
            {
                "name": "analytical_perspective",
                "content": """
                Analyze the following content from an analytical perspective:

                Content: {{ content }}

                Focus on:
                - Logical structure and reasoning
                - Data and evidence presented
                - Methodology and approach
                - Strengths and weaknesses in analysis

                Provide a detailed analytical assessment.
                """,
                "role": "analyzer",
                "priority": 1,
            },
            {
                "name": "critical_perspective",
                "content": """
                Critically evaluate the following content:

                Content: {{ content }}

                Focus on:
                - Potential biases and assumptions
                - Missing information or perspectives
                - Alternative interpretations
                - Limitations and risks

                Provide a constructive critical evaluation.
                """,
                "role": "critic",
                "priority": 1,
            },
            {
                "name": "practical_perspective",
                "content": """
                Evaluate the following content from a practical implementation perspective:

                Content: {{ content }}

                Focus on:
                - Feasibility and practicality
                - Resource requirements
                - Implementation challenges
                - Real-world applications

                Provide practical insights and recommendations.
                """,
                "role": "specialist",
                "priority": 1,
            },
        ]

        reduce_template = """
        Synthesize the following perspectives into a comprehensive analysis:

        {% for role, response in agent_responses.items() %}
        **{{ role.title() }} Perspective:**
        {{ response }}

        {% endfor %}

        Based on these {{ successful_count }} perspectives, provide:
        1. Key insights and common themes
        2. Areas of consensus and disagreement
        3. Balanced recommendations
        4. Next steps or areas for further investigation

        Create a well-structured, comprehensive analysis that incorporates all valuable insights.
        """

        return await self.create_ensemble_configuration(
            name=name,
            description=description,
            main_prompt_template="Analyze the following content: {{ content }}",
            sub_prompt_templates=sub_templates,
            reduce_prompt_template=reduce_template,
            strategy="parallel",
            variables=variables,
        )

    async def _create_document_review_ensemble(
        self,
        name: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create a document review ensemble."""
        sub_templates = [
            {
                "name": "content_reviewer",
                "content": """
                Review the following document for content quality:

                Document: {{ document }}

                Evaluate:
                - Clarity and coherence
                - Completeness of information
                - Accuracy and factual correctness
                - Logical flow and organization

                Provide specific feedback and suggestions for improvement.
                """,
                "role": "reviewer",
                "priority": 1,
            },
            {
                "name": "style_editor",
                "content": """
                Review the following document for style and language:

                Document: {{ document }}

                Evaluate:
                - Writing style and tone
                - Grammar and syntax
                - Readability and accessibility
                - Consistency in terminology

                Provide editing suggestions and style improvements.
                """,
                "role": "specialist",
                "priority": 1,
            },
            {
                "name": "structure_analyst",
                "content": """
                Analyze the structure and organization of the following document:

                Document: {{ document }}

                Evaluate:
                - Document structure and hierarchy
                - Section organization and flow
                - Use of headings and formatting
                - Overall presentation

                Suggest structural improvements and reorganization.
                """,
                "role": "analyzer",
                "priority": 1,
            },
        ]

        reduce_template = """
        Compile a comprehensive document review based on the following expert feedback:

        {% for role, response in agent_responses.items() %}
        **{{ role.title() }} Review:**
        {{ response }}

        {% endfor %}

        Provide:
        1. Summary of key issues identified
        2. Prioritized list of improvements
        3. Specific action items for revision
        4. Overall assessment and recommendations

        Structure the feedback to be actionable and constructive.
        """

        return await self.create_ensemble_configuration(
            name=name,
            description=description,
            main_prompt_template="Review the following document: {{ document }}",
            sub_prompt_templates=sub_templates,
            reduce_prompt_template=reduce_template,
            strategy="parallel",
            variables=variables,
        )

    async def _create_code_review_ensemble(
        self,
        name: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create a code review ensemble."""
        sub_templates = [
            {
                "name": "security_reviewer",
                "content": """
                Review the following code for security vulnerabilities:

                Code: {{ code }}
                Language: {{ language | default('Unknown') }}

                Check for:
                - Common security vulnerabilities
                - Input validation issues
                - Authentication and authorization flaws
                - Data exposure risks

                Provide specific security recommendations.
                """,
                "role": "specialist",
                "priority": 1,
            },
            {
                "name": "performance_analyst",
                "content": """
                Analyze the following code for performance optimization:

                Code: {{ code }}
                Language: {{ language | default('Unknown') }}

                Evaluate:
                - Algorithm efficiency and complexity
                - Resource usage patterns
                - Potential bottlenecks
                - Optimization opportunities

                Suggest performance improvements.
                """,
                "role": "analyzer",
                "priority": 1,
            },
            {
                "name": "maintainability_reviewer",
                "content": """
                Review the following code for maintainability and best practices:

                Code: {{ code }}
                Language: {{ language | default('Unknown') }}

                Assess:
                - Code clarity and readability
                - Adherence to best practices
                - Documentation and comments
                - Modularity and reusability

                Provide maintainability recommendations.
                """,
                "role": "reviewer",
                "priority": 1,
            },
        ]

        reduce_template = """
        Compile a comprehensive code review based on expert analysis:

        {% for role, response in agent_responses.items() %}
        **{{ role.title() }} Analysis:**
        {{ response }}

        {% endfor %}

        Provide:
        1. Critical issues requiring immediate attention
        2. Improvement suggestions by category
        3. Best practices recommendations
        4. Overall code quality assessment

        Prioritize feedback for maximum impact on code quality.
        """

        return await self.create_ensemble_configuration(
            name=name,
            description=description,
            main_prompt_template="Review the following code: {{ code }}",
            sub_prompt_templates=sub_templates,
            reduce_prompt_template=reduce_template,
            strategy="parallel",
            variables=variables,
        )

    async def _create_research_synthesis_ensemble(
        self,
        name: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> EnsembleConfiguration:
        """Create a research synthesis ensemble."""
        sub_templates = [
            {
                "name": "literature_reviewer",
                "content": """
                Review and analyze the provided research literature:

                Research Topic: {{ topic }}
                Sources: {{ sources }}

                Focus on:
                - Key findings and methodologies
                - Research gaps and limitations
                - Theoretical frameworks used
                - Consensus and disagreements in literature

                Provide a comprehensive literature analysis.
                """,
                "role": "reviewer",
                "priority": 1,
            },
            {
                "name": "methodology_analyst",
                "content": """
                Analyze research methodologies in the provided sources:

                Research Topic: {{ topic }}
                Sources: {{ sources }}

                Evaluate:
                - Research design and approaches
                - Data collection and analysis methods
                - Validity and reliability of studies
                - Methodological strengths and weaknesses

                Provide methodological insights and recommendations.
                """,
                "role": "analyzer",
                "priority": 1,
            },
            {
                "name": "synthesis_specialist",
                "content": """
                Synthesize findings from the research sources:

                Research Topic: {{ topic }}
                Sources: {{ sources }}

                Create:
                - Integration of key findings
                - Identification of patterns and themes
                - Resolution of conflicting evidence
                - Implications for theory and practice

                Provide a coherent research synthesis.
                """,
                "role": "synthesizer",
                "priority": 2,
                "dependencies": [],  # Will be set based on other templates
            },
        ]

        reduce_template = """
        Create a comprehensive research synthesis report based on expert analysis:

        {% for role, response in agent_responses.items() %}
        **{{ role.title() }} Analysis:**
        {{ response }}

        {% endfor %}

        Compile into a structured research synthesis including:
        1. Executive summary of key findings
        2. Methodological considerations
        3. Synthesized results and implications
        4. Research gaps and future directions
        5. Practical applications and recommendations

        Present as a coherent, scholarly synthesis suitable for academic or professional use.
        """

        return await self.create_ensemble_configuration(
            name=name,
            description=description,
            main_prompt_template="Synthesize research on: {{ topic }}",
            sub_prompt_templates=sub_templates,
            reduce_prompt_template=reduce_template,
            strategy="sequential",  # Sequential to allow synthesis to build on reviews
            variables=variables,
        )
