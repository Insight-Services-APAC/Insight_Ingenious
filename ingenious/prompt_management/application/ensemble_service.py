"""
Ensemble orchestration service for managing prompt ensemble executions.

This service coordinates the execution of multiple AI agents in various patterns
(parallel, sequential, hierarchical) and handles aggregation of results.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from jinja2 import BaseLoader, Environment

from ingenious.external_integrations.domain.services import ILLMService
from ingenious.prompt_management.domain.ensemble import (
    AgentExecution,
    EnsembleConfiguration,
    EnsembleExecution,
    EnsembleResult,
    EnsembleStrategy,
)

logger = logging.getLogger(__name__)


class EnsembleOrchestrationService:
    """Service for orchestrating prompt ensemble executions."""

    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service
        self.jinja_env = Environment(loader=BaseLoader())

    async def execute_ensemble(
        self,
        config: EnsembleConfiguration,
        input_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> EnsembleResult:
        """Execute a complete prompt ensemble."""
        logger.info(f"Starting ensemble execution: {config.name}")

        # Create execution record
        execution = EnsembleExecution(
            config_id=config.config_id,
            input_data=input_data,
        )

        try:
            # Generate sub-prompts from templates
            sub_prompts = await self._generate_sub_prompts(
                config, input_data, user_context
            )

            # Execute agents based on strategy
            if config.strategy == EnsembleStrategy.PARALLEL:
                agent_executions = await self._execute_parallel(
                    sub_prompts, config.max_concurrent_agents
                )
            elif config.strategy == EnsembleStrategy.SEQUENTIAL:
                agent_executions = await self._execute_sequential(sub_prompts)
            elif config.strategy == EnsembleStrategy.HIERARCHICAL:
                agent_executions = await self._execute_hierarchical(sub_prompts, config)
            else:
                raise ValueError(f"Unsupported strategy: {config.strategy}")

            # Add executions to ensemble
            for agent_exec in agent_executions:
                execution.add_agent_execution(agent_exec)

            # Aggregate results using reduce prompt
            final_response = await self._aggregate_results(
                config.reduce_prompt_template,
                agent_executions,
                input_data,
                user_context,
            )

            execution.final_response = final_response
            execution.completed_at = datetime.utcnow()
            execution.status = "completed"

            logger.info(f"Ensemble execution completed: {execution.execution_id}")

            return EnsembleResult.from_execution(execution, config)

        except Exception as e:
            logger.exception(f"Ensemble execution failed: {e}")
            execution.error = str(e)
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            raise

    async def _generate_sub_prompts(
        self,
        config: EnsembleConfiguration,
        input_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate sub-prompts from templates."""
        logger.debug("Generating sub-prompts from templates")

        # Combine all available variables
        template_vars = {
            **config.variables,
            **input_data,
            **(user_context or {}),
        }

        sub_prompts = []
        for template in config.sub_prompt_templates:
            try:
                # Merge template-specific variables
                vars_for_template = {
                    **template_vars,
                    **template.variables,
                }

                # Render the template
                jinja_template = self.jinja_env.from_string(template.content)
                rendered_prompt = jinja_template.render(**vars_for_template)

                sub_prompts.append(
                    {
                        "template_id": template.template_id,
                        "role": template.role,
                        "prompt": rendered_prompt,
                        "priority": template.priority,
                        "dependencies": template.dependencies,
                    }
                )

            except Exception as e:
                logger.warning(f"Failed to render template {template.name}: {e}")
                continue

        # Sort by priority (lower number = higher priority)
        sub_prompts.sort(key=lambda x: x["priority"])

        logger.debug(f"Generated {len(sub_prompts)} sub-prompts")
        return sub_prompts

    async def _execute_parallel(
        self,
        sub_prompts: List[Dict[str, Any]],
        max_concurrent: int,
    ) -> List[AgentExecution]:
        """Execute sub-prompts in parallel with concurrency control."""
        logger.debug(
            f"Executing {len(sub_prompts)} prompts in parallel (max {max_concurrent})"
        )

        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []

        for sub_prompt in sub_prompts:
            task = self._execute_single_agent(sub_prompt, semaphore)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed executions
        executions = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                execution = AgentExecution(
                    agent_role=sub_prompts[i]["role"],
                    template_id=sub_prompts[i]["template_id"],
                    prompt=sub_prompts[i]["prompt"],
                    error=str(result),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
            else:
                execution = result
            executions.append(execution)

        return executions

    async def _execute_sequential(
        self,
        sub_prompts: List[Dict[str, Any]],
    ) -> List[AgentExecution]:
        """Execute sub-prompts sequentially in priority order."""
        logger.debug(f"Executing {len(sub_prompts)} prompts sequentially")

        executions = []
        for sub_prompt in sub_prompts:
            execution = await self._execute_single_agent(sub_prompt)
            executions.append(execution)

        return executions

    async def _execute_hierarchical(
        self,
        sub_prompts: List[Dict[str, Any]],
        config: EnsembleConfiguration,
    ) -> List[AgentExecution]:
        """Execute sub-prompts in hierarchical order based on dependencies."""
        logger.debug(f"Executing {len(sub_prompts)} prompts hierarchically")

        # Build dependency graph
        prompt_map = {p["template_id"]: p for p in sub_prompts}
        completed = {}
        executions = []

        async def execute_with_dependencies(
            prompt_data: Dict[str, Any],
        ) -> AgentExecution:
            template_id = prompt_data["template_id"]

            # Wait for dependencies to complete
            for dep_id in prompt_data["dependencies"]:
                if dep_id in prompt_map and dep_id not in completed:
                    dep_execution = await execute_with_dependencies(prompt_map[dep_id])
                    if dep_execution not in executions:
                        executions.append(dep_execution)
                    completed[dep_id] = dep_execution

            # Execute this prompt
            if template_id not in completed:
                execution = await self._execute_single_agent(prompt_data)
                completed[template_id] = execution
                return execution

            return completed[template_id]

        # Execute all prompts with dependency resolution
        for prompt_data in sub_prompts:
            if prompt_data["template_id"] not in completed:
                execution = await execute_with_dependencies(prompt_data)
                if execution not in executions:
                    executions.append(execution)

        return executions

    async def _execute_single_agent(
        self,
        sub_prompt: Dict[str, Any],
        semaphore: Optional[asyncio.Semaphore] = None,
    ) -> AgentExecution:
        """Execute a single agent with the given prompt."""
        execution = AgentExecution(
            agent_role=sub_prompt["role"],
            template_id=sub_prompt["template_id"],
            prompt=sub_prompt["prompt"],
            started_at=datetime.utcnow(),
        )

        try:
            if semaphore:
                async with semaphore:
                    response = await self._call_llm(sub_prompt["prompt"])
            else:
                response = await self._call_llm(sub_prompt["prompt"])

            execution.response = (
                response.content if hasattr(response, "content") else str(response)
            )
            execution.completed_at = datetime.utcnow()

            # Extract token usage if available
            if hasattr(response, "usage"):
                execution.token_usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }

        except Exception as e:
            logger.exception(
                f"Agent execution failed for role {sub_prompt['role']}: {e}"
            )
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()

        return execution

    async def _call_llm(self, prompt: str) -> Any:
        """Call the LLM service with the given prompt."""
        messages = [{"role": "user", "content": prompt}]
        return await self.llm_service.generate_response(messages)

    async def _aggregate_results(
        self,
        reduce_template: str,
        agent_executions: List[AgentExecution],
        input_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Aggregate results from agent executions using reduce template."""
        logger.debug("Aggregating results from agent executions")

        # Prepare variables for reduce template
        successful_executions = [
            exec for exec in agent_executions if exec.is_successful
        ]

        agent_responses = {
            exec.agent_role: exec.response
            for exec in successful_executions
            if exec.response
        }

        template_vars = {
            **input_data,
            **(user_context or {}),
            "agent_responses": agent_responses,
            "successful_count": len(successful_executions),
            "total_count": len(agent_executions),
        }

        # Render and execute reduce template
        try:
            jinja_template = self.jinja_env.from_string(reduce_template)
            reduce_prompt = jinja_template.render(**template_vars)

            response = await self._call_llm(reduce_prompt)
            return response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            logger.exception(f"Failed to aggregate results: {e}")
            # Fallback: simple concatenation
            return "\n\n".join(
                [
                    f"**{exec.agent_role}**: {exec.response}"
                    for exec in successful_executions
                    if exec.response
                ]
            )
