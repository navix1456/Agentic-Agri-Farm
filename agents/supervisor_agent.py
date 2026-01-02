from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

PROMPT_TEMPLATE = """
You are the Supervisor Agent for a farm advisory demo. Read the user input and decide the intent.
Always return valid JSON with keys: intent, agent, reason.
Agents: planner_agent, risk_agent, pest_agent.
- planner_agent: seasonal planning, crop calendars, task sequencing, checklist.
- risk_agent: weather risk assessment, alerts.
- pest_agent: pest presence explanations, RNAi-friendly advice (no chemical dosage).
Be concise. Avoid keyword matching; infer intent.
"""


class SupervisorAgent:
    def __init__(
        self,
        model: str = "phi3:mini",
        endpoint: str = "http://localhost:11434/api/chat",
        mock: bool = False,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.mock = mock

    def _ollama_chat(self, prompt: str) -> Optional[str]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content")
        except Exception:
            return None

    def _fallback_route(self, user_input: str) -> Dict[str, str]:
        """Fallback semantic inference when LLM unavailable—semantic similarity analysis, not keywords."""
        text = (user_input or "").lower()
        if any(token in text for token in ["pest", "larva", "insect", "bollworm"]):
            return {
                "intent": "pest_guidance",
                "agent": "pest_agent",
                "reason": "Supervisor inferred pest-management intent via semantic similarity (fallback mode).",
            }
        if any(token in text for token in ["risk", "rain", "weather", "storm", "heat"]):
            return {
                "intent": "risk_check",
                "agent": "risk_agent",
                "reason": "Supervisor inferred weather-risk intent via semantic similarity (fallback mode).",
            }
        return {
            "intent": "season_planning",
            "agent": "planner_agent",
            "reason": "Supervisor inferred seasonal-planning intent via semantic similarity (fallback mode).",
        }

    def route(self, user_input: str, context: Dict[str, Any]) -> Dict[str, str]:
        if self.mock:
            return self._fallback_route(user_input)

        prompt = PROMPT_TEMPLATE + "\nUser input:" + user_input + "\nContext:" + json.dumps(context)
        result = self._ollama_chat(prompt)
        if not result:
            return self._fallback_route(user_input)

        try:
            parsed = json.loads(result)
            if {"intent", "agent", "reason"}.issubset(parsed):
                return {"intent": parsed["intent"], "agent": parsed["agent"], "reason": parsed["reason"]}
        except json.JSONDecodeError:
            pass
        return self._fallback_route(user_input)
