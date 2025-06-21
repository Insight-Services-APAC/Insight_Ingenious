#!/usr/bin/env python3
"""
Performance benchmarking for the ingenious framework.

This script measures and analyzes performance characteristics:
- Prompt processing latency
- Concurrent request handling
- Memory usage patterns
- Azure service response times
"""

import asyncio
import json
import sys
import time
from statistics import mean, median, stdev
from typing import Any, Dict

import httpx
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class PerformanceBenchmark:
    """Performance benchmarking suite for ingenious."""

    def __init__(self):
        self.azure_openai_url = "http://localhost:5001"
        self.azure_blob_url = "http://localhost:5002"
        self.results = {}

    async def measure_prompt_processing_latency(
        self, num_requests: int = 10
    ) -> Dict[str, Any]:
        """Measure latency for individual prompt processing."""
        console.print(
            f"[yellow]Measuring prompt processing latency ({num_requests} requests)...[/yellow]"
        )

        latencies = []
        errors = 0

        async with httpx.AsyncClient() as client:
            for i in range(num_requests):
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Process this prompt for benchmark test {i + 1}",
                        }
                    ],
                    "max_tokens": 50,
                }

                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.azure_openai_url}/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                        json=payload,
                        headers={
                            "api-key": "test-key",
                            "Content-Type": "application/json",
                        },
                        timeout=30.0,
                    )
                    end_time = time.time()

                    if response.status_code == 200:
                        latencies.append(end_time - start_time)
                    else:
                        # For mock services, still measure latency
                        latencies.append(end_time - start_time)

                except Exception as e:
                    errors += 1
                    console.print(f"[red]Request {i + 1} failed: {e}[/red]")

        if latencies:
            return {
                "test": "Prompt Processing Latency",
                "num_requests": num_requests,
                "successful_requests": len(latencies),
                "errors": errors,
                "avg_latency_ms": mean(latencies) * 1000,
                "median_latency_ms": median(latencies) * 1000,
                "min_latency_ms": min(latencies) * 1000,
                "max_latency_ms": max(latencies) * 1000,
                "std_latency_ms": stdev(latencies) * 1000 if len(latencies) > 1 else 0,
                "latencies_ms": [latency * 1000 for latency in latencies],
            }
        else:
            return {
                "test": "Prompt Processing Latency",
                "error": "No successful requests",
                "errors": errors,
            }

    async def measure_concurrent_processing(
        self, concurrent_requests: int = 5, rounds: int = 3
    ) -> Dict[str, Any]:
        """Measure performance under concurrent load."""
        console.print(
            f"[yellow]Measuring concurrent processing ({concurrent_requests} concurrent, {rounds} rounds)...[/yellow]"
        )

        round_results = []

        for round_num in range(rounds):
            console.print(f"  Round {round_num + 1}/{rounds}")

            async with httpx.AsyncClient() as client:
                # Create concurrent requests
                tasks = []
                start_time = time.time()

                for i in range(concurrent_requests):
                    payload = {
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Concurrent request {i + 1} in round {round_num + 1}",
                            }
                        ],
                        "max_tokens": 30,
                    }

                    task = client.post(
                        f"{self.azure_openai_url}/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                        json=payload,
                        headers={
                            "api-key": "test-key",
                            "Content-Type": "application/json",
                        },
                        timeout=30.0,
                    )
                    tasks.append(task)

                # Execute all requests concurrently
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()

                # Analyze results
                successful = [
                    r
                    for r in responses
                    if not isinstance(r, Exception) and hasattr(r, "status_code")
                ]
                failed = [r for r in responses if isinstance(r, Exception)]

                round_result = {
                    "round": round_num + 1,
                    "total_time_ms": (end_time - start_time) * 1000,
                    "concurrent_requests": concurrent_requests,
                    "successful": len(successful),
                    "failed": len(failed),
                    "requests_per_second": concurrent_requests
                    / (end_time - start_time),
                    "avg_time_per_request_ms": (
                        (end_time - start_time) / concurrent_requests
                    )
                    * 1000,
                }
                round_results.append(round_result)

        # Aggregate results
        if round_results:
            avg_rps = mean([r["requests_per_second"] for r in round_results])
            avg_time_per_request = mean(
                [r["avg_time_per_request_ms"] for r in round_results]
            )
            total_successful = sum([r["successful"] for r in round_results])
            total_failed = sum([r["failed"] for r in round_results])

            return {
                "test": "Concurrent Processing",
                "rounds": rounds,
                "concurrent_requests": concurrent_requests,
                "avg_requests_per_second": avg_rps,
                "avg_time_per_request_ms": avg_time_per_request,
                "total_successful": total_successful,
                "total_failed": total_failed,
                "success_rate": total_successful / (total_successful + total_failed)
                if (total_successful + total_failed) > 0
                else 0,
                "round_details": round_results,
            }
        else:
            return {"test": "Concurrent Processing", "error": "No rounds completed"}

    async def measure_ensemble_processing(self) -> Dict[str, Any]:
        """Measure performance of full ensemble processing."""
        console.print("[yellow]Measuring ensemble processing performance...[/yellow]")

        # Simulate ensemble processing
        main_prompt = "Analyze the impact of renewable energy adoption"
        sub_prompts = [
            "Examine the economic implications of renewable energy adoption",
            "Analyze the environmental benefits of renewable energy adoption",
            "Evaluate the social impact of renewable energy adoption",
            "Assess the technological challenges of renewable energy adoption",
        ]

        start_time = time.time()

        # Step 1: Generate sub-prompts (simulated template processing)
        template_start = time.time()
        # In real implementation, this would use Jinja2 templating
        template_time = time.time() - template_start

        # Step 2: Process sub-prompts concurrently
        processing_start = time.time()

        async with httpx.AsyncClient() as client:
            tasks = []
            for i, prompt in enumerate(sub_prompts):
                payload = {
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                }

                task = client.post(
                    f"{self.azure_openai_url}/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                    json=payload,
                    headers={"api-key": "test-key", "Content-Type": "application/json"},
                    timeout=30.0,
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

        processing_time = time.time() - processing_start

        # Step 3: Synthesize results (simulated)
        synthesis_start = time.time()

        # Simulate synthesis processing
        synthesis_payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": "Synthesize these analyses: [Analysis 1], [Analysis 2], [Analysis 3], [Analysis 4]",
                }
            ],
            "max_tokens": 200,
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.azure_openai_url}/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01",
                json=synthesis_payload,
                headers={"api-key": "test-key", "Content-Type": "application/json"},
                timeout=30.0,
            )

        synthesis_time = time.time() - synthesis_start
        total_time = time.time() - start_time

        successful_responses = [r for r in responses if not isinstance(r, Exception)]

        return {
            "test": "Ensemble Processing",
            "main_prompt": main_prompt,
            "num_sub_prompts": len(sub_prompts),
            "total_time_ms": total_time * 1000,
            "template_time_ms": template_time * 1000,
            "processing_time_ms": processing_time * 1000,
            "synthesis_time_ms": synthesis_time * 1000,
            "successful_sub_prompts": len(successful_responses),
            "failed_sub_prompts": len(sub_prompts) - len(successful_responses),
            "prompts_per_second": len(sub_prompts) / total_time,
            "breakdown": {
                "template_percent": (template_time / total_time) * 100,
                "processing_percent": (processing_time / total_time) * 100,
                "synthesis_percent": (synthesis_time / total_time) * 100,
            },
        }

    def measure_memory_usage(self) -> Dict[str, Any]:
        """Measure current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "test": "Memory Usage",
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "total_mb": psutil.virtual_memory().total / 1024 / 1024,
        }

    async def measure_storage_operations(self) -> Dict[str, Any]:
        """Measure Azure Blob Storage operation performance."""
        console.print("[yellow]Measuring storage operation performance...[/yellow]")

        # Simulate storing conversation data
        conversation_data = {
            "conversation_id": "perf-test-123",
            "messages": [{"role": "user", "content": "Test"} for _ in range(20)],
            "ensemble_data": {
                "main_prompt": "Test prompt",
                "sub_prompts": [f"Sub prompt {i}" for i in range(4)],
                "responses": [f"Response {i}" for i in range(4)],
            },
        }

        blob_data = json.dumps(conversation_data).encode()
        data_size_mb = len(blob_data) / 1024 / 1024

        upload_times = []
        download_times = []

        async with httpx.AsyncClient() as client:
            # Test upload performance
            for i in range(3):
                start_time = time.time()
                try:
                    await client.put(
                        f"{self.azure_blob_url}/testcontainer/perf-test-{i}.json",
                        content=blob_data,
                        headers={
                            "x-ms-version": "2020-10-02",
                            "x-ms-blob-type": "BlockBlob",
                            "Content-Type": "application/json",
                        },
                        timeout=10.0,
                    )
                    upload_time = time.time() - start_time
                    upload_times.append(upload_time)
                except Exception as e:
                    console.print(f"[red]Upload {i + 1} failed: {e}[/red]")

            # Test download performance
            for i in range(3):
                start_time = time.time()
                try:
                    await client.get(
                        f"{self.azure_blob_url}/testcontainer/perf-test-{i}.json",
                        headers={"x-ms-version": "2020-10-02"},
                        timeout=10.0,
                    )
                    download_time = time.time() - start_time
                    download_times.append(download_time)
                except Exception as e:
                    console.print(f"[red]Download {i + 1} failed: {e}[/red]")

        result = {
            "test": "Storage Operations",
            "data_size_mb": data_size_mb,
            "upload_operations": len(upload_times),
            "download_operations": len(download_times),
        }

        if upload_times:
            result["upload_avg_ms"] = mean(upload_times) * 1000
            result["upload_throughput_mbps"] = data_size_mb / mean(upload_times)

        if download_times:
            result["download_avg_ms"] = mean(download_times) * 1000
            result["download_throughput_mbps"] = data_size_mb / mean(download_times)

        return result

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark."""
        console.print(
            Panel(
                "[bold blue]Ingenious Performance Benchmark Suite[/bold blue]\n\n"
                "Measuring performance across all key areas:\n"
                "• Prompt processing latency\n"
                "• Concurrent request handling\n"
                "• Ensemble processing efficiency\n"
                "• Memory usage patterns\n"
                "• Storage operation performance",
                title="⚡ Performance Benchmark",
                border_style="blue",
            )
        )

        benchmark_results = {
            "timestamp": time.time(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "python_version": sys.version,
            },
            "tests": {},
        }

        # Test 1: Prompt Processing Latency
        console.print("\n[cyan]Test 1: Prompt Processing Latency[/cyan]")
        latency_result = await self.measure_prompt_processing_latency(10)
        benchmark_results["tests"]["latency"] = latency_result

        # Test 2: Concurrent Processing
        console.print("\n[cyan]Test 2: Concurrent Processing[/cyan]")
        concurrent_result = await self.measure_concurrent_processing(5, 3)
        benchmark_results["tests"]["concurrent"] = concurrent_result

        # Test 3: Ensemble Processing
        console.print("\n[cyan]Test 3: Ensemble Processing[/cyan]")
        ensemble_result = await self.measure_ensemble_processing()
        benchmark_results["tests"]["ensemble"] = ensemble_result

        # Test 4: Memory Usage
        console.print("\n[cyan]Test 4: Memory Usage[/cyan]")
        memory_result = self.measure_memory_usage()
        benchmark_results["tests"]["memory"] = memory_result

        # Test 5: Storage Operations
        console.print("\n[cyan]Test 5: Storage Operations[/cyan]")
        storage_result = await self.measure_storage_operations()
        benchmark_results["tests"]["storage"] = storage_result

        return benchmark_results

    def display_benchmark_results(self, results: Dict[str, Any]):
        """Display benchmark results in formatted tables."""

        # Performance Summary Table
        summary_table = Table(title="Performance Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Unit", style="yellow")
        summary_table.add_column("Rating", style="blue")

        # Latency metrics
        if (
            "latency" in results["tests"]
            and "avg_latency_ms" in results["tests"]["latency"]
        ):
            avg_latency = results["tests"]["latency"]["avg_latency_ms"]
            latency_rating = (
                "Excellent"
                if avg_latency < 100
                else "Good"
                if avg_latency < 500
                else "Needs Improvement"
            )
            summary_table.add_row(
                "Avg Prompt Latency", f"{avg_latency:.1f}", "ms", latency_rating
            )

        # Concurrent processing metrics
        if (
            "concurrent" in results["tests"]
            and "avg_requests_per_second" in results["tests"]["concurrent"]
        ):
            rps = results["tests"]["concurrent"]["avg_requests_per_second"]
            rps_rating = (
                "Excellent" if rps > 10 else "Good" if rps > 5 else "Needs Improvement"
            )
            summary_table.add_row(
                "Requests per Second", f"{rps:.1f}", "req/s", rps_rating
            )

        # Ensemble processing metrics
        if (
            "ensemble" in results["tests"]
            and "total_time_ms" in results["tests"]["ensemble"]
        ):
            ensemble_time = results["tests"]["ensemble"]["total_time_ms"]
            ensemble_rating = (
                "Excellent"
                if ensemble_time < 2000
                else "Good"
                if ensemble_time < 5000
                else "Needs Improvement"
            )
            summary_table.add_row(
                "Ensemble Processing", f"{ensemble_time:.0f}", "ms", ensemble_rating
            )

        # Memory usage metrics
        if "memory" in results["tests"]:
            memory_mb = results["tests"]["memory"]["rss_mb"]
            memory_rating = (
                "Excellent"
                if memory_mb < 100
                else "Good"
                if memory_mb < 200
                else "High"
            )
            summary_table.add_row(
                "Memory Usage", f"{memory_mb:.1f}", "MB", memory_rating
            )

        console.print(summary_table)

        # Detailed Results
        console.print("\n[bold]Detailed Results:[/bold]")

        for test_name, test_result in results["tests"].items():
            if isinstance(test_result, dict) and "test" in test_result:
                console.print(f"\n[cyan]{test_result['test']}:[/cyan]")

                # Display key metrics for each test
                if test_name == "latency":
                    console.print(
                        f"  Successful requests: {test_result.get('successful_requests', 'N/A')}"
                    )
                    console.print(
                        f"  Average latency: {test_result.get('avg_latency_ms', 0):.1f} ms"
                    )
                    console.print(
                        f"  Median latency: {test_result.get('median_latency_ms', 0):.1f} ms"
                    )
                    console.print(
                        f"  Standard deviation: {test_result.get('std_latency_ms', 0):.1f} ms"
                    )

                elif test_name == "concurrent":
                    console.print(
                        f"  Avg requests/second: {test_result.get('avg_requests_per_second', 0):.1f}"
                    )
                    console.print(
                        f"  Success rate: {test_result.get('success_rate', 0) * 100:.1f}%"
                    )
                    console.print(
                        f"  Avg time per request: {test_result.get('avg_time_per_request_ms', 0):.1f} ms"
                    )

                elif test_name == "ensemble":
                    console.print(
                        f"  Total processing time: {test_result.get('total_time_ms', 0):.0f} ms"
                    )
                    console.print(
                        f"  Sub-prompts processed: {test_result.get('successful_sub_prompts', 0)}"
                    )
                    console.print(
                        f"  Processing efficiency: {test_result.get('prompts_per_second', 0):.1f} prompts/sec"
                    )

                elif test_name == "storage":
                    if "upload_avg_ms" in test_result:
                        console.print(
                            f"  Upload speed: {test_result.get('upload_avg_ms', 0):.1f} ms"
                        )
                    if "download_avg_ms" in test_result:
                        console.print(
                            f"  Download speed: {test_result.get('download_avg_ms', 0):.1f} ms"
                        )


async def main():
    """Main benchmarking function."""
    benchmark = PerformanceBenchmark()

    try:
        results = await benchmark.run_comprehensive_benchmark()
        benchmark.display_benchmark_results(results)

        # Save detailed results
        with open("performance_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)

        console.print(
            "\n[green]✓ Benchmark complete! Detailed results saved to performance_benchmark_results.json[/green]"
        )

        # Performance recommendations
        console.print(
            Panel(
                "[bold]Performance Recommendations:[/bold]\n\n"
                "• For production: Monitor latency trends and set up alerts\n"
                "• Consider connection pooling for high-volume scenarios\n"
                "• Implement caching for frequently used prompts\n"
                "• Use async processing for all Azure service calls\n"
                "• Monitor memory usage with multiple concurrent ensembles",
                title="💡 Recommendations",
                border_style="yellow",
            )
        )

    except Exception as e:
        console.print(f"\n[red]✗ Benchmark failed: {e}[/red]")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        console.print("[bold]Ingenious Performance Benchmark[/bold]")
        console.print("\nMeasures performance across all key areas:")
        console.print("• Prompt processing latency and throughput")
        console.print("• Concurrent request handling capabilities")
        console.print("• Full ensemble processing efficiency")
        console.print("• Memory usage patterns")
        console.print("• Azure storage operation performance")
        console.print(
            "\nEnsure mock services are running: ../mock-azure-services.sh start"
        )
    else:
        asyncio.run(main())
