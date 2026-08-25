"""
Cost Tracker service for calculating LLM token usage and USD costs across research agents.
"""

from typing import Any, Dict


class CostTracker:
    # Standard per-1k token costs (USD)
    PRICING = {
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.00060},
        "text-embedding-3-small": {"prompt": 0.00002, "completion": 0.0},
        "default": {"prompt": 0.0005, "completion": 0.0015},
    }

    @classmethod
    def calculate_cost(
        cls,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
    ) -> float:
        rates = cls.PRICING.get(model, cls.PRICING["default"])
        cost = (prompt_tokens / 1000.0 * rates["prompt"]) + (
            completion_tokens / 1000.0 * rates["completion"]
        )
        return round(cost, 6)

    @classmethod
    def estimate_agent_breakdown(
        cls,
        num_docs: int,
        num_claims: int,
        report_length: int,
    ) -> tuple[int, float, Dict[str, Any]]:
        """
        Estimates or aggregates token and cost distributions across agents.
        """
        # Planner: ~1.5k prompt, ~800 completion
        planner_p, planner_c = 1500, 800
        # Search Agent: ~800 prompt, ~400 completion per query
        search_p, search_c = 800 * 3, 400 * 3
        # Fact Extractor: ~1200 prompt, ~500 completion per source
        fact_p, fact_c = max(1, num_docs) * 1200, max(1, num_claims) * 200
        # Synthesizer: ~3500 prompt, ~2000 completion
        synth_p, synth_c = 3500, max(1500, report_length // 4)

        planner_cost = cls.calculate_cost(planner_p, planner_c)
        search_cost = cls.calculate_cost(search_p, search_c)
        fact_cost = cls.calculate_cost(fact_p, fact_c)
        synth_cost = cls.calculate_cost(synth_p, synth_c)

        total_tokens = (
            planner_p
            + planner_c
            + search_p
            + search_c
            + fact_p
            + fact_c
            + synth_p
            + synth_c
        )
        total_cost = round(
            planner_cost + search_cost + fact_cost + synth_cost, 4
        )

        breakdown = {
            "planner": {
                "tokens": planner_p + planner_c,
                "cost_usd": planner_cost,
                "latency_ms": 1240,
            },
            "search_agent": {
                "tokens": search_p + search_c,
                "cost_usd": search_cost,
                "latency_ms": 2850,
            },
            "fact_extractor": {
                "tokens": fact_p + fact_c,
                "cost_usd": fact_cost,
                "latency_ms": 1920,
            },
            "synthesizer": {
                "tokens": synth_p + synth_c,
                "cost_usd": synth_cost,
                "latency_ms": 3410,
            },
        }

        return total_tokens, total_cost, breakdown
