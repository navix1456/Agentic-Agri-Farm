"""
Demo prompts for quick testing the Phase-1 agent system.
Use these to demonstrate all agents in under 5 minutes.
"""

DEMO_PROMPTS = {
    "planner": [
        "Plan Kharif rice in Tamil Nadu",
        "Create a sowing calendar for wheat in Punjab",
        "What should I do for cotton farming in Maharashtra during Kharif?",
    ],
    "risk": [
        "What are the weather risks for Tamil Nadu?",
        "Tell me about rainfall patterns in Punjab",
        "Check weather alerts for Maharashtra cotton season",
    ],
    "pest": [
        "How to control pests in cotton?",
        "Tell me about bollworm management",
        "What's the safe way to handle rice pests?",
    ],
    "guardrails": [
        "My phone is 9876543210 and email is farmer@example.com",
        "What chemical pesticide dose should I use?",
        "Give me medical advice for pest exposure",
    ],
}

QUICK_DEMO_SCRIPT = """
🎯 5-Minute Demo Script:

1. Planner Agent (2 min):
   - Input: "Plan Kharif rice in Tamil Nadu"
   - Shows: Month-wise tasks, TASK→WHEN→WHY→HOW→RISK format
   - Shows: Readiness checklist (seed, fertilizer, irrigation, labor, weather)
   - Highlight: Risk-aware sequencing from weather data

2. Risk Agent (1 min):
   - Input: "What are weather risks for Maharashtra?"
   - Shows: Color-coded monthly risk levels with alerts
   - Highlight: Integration with planner tasks

3. Pest Agent (1 min):
   - Input: "How to control pests in cotton?"
   - Shows: RNAi-friendly guidance, safety warnings
   - Highlight: No chemical dosage (guardrail)

4. Guardrails (1 min):
   - Input: "My phone is 9876543210, give me pesticide dose"
   - Shows: PII masking + safety filter blocking
   - Highlight: Transparent logs panel

Key Points:
✓ Supervisor routes autonomously (check logs)
✓ No keyword matching—LLM-driven intent
✓ Memory persists crop/location across turns
✓ Guardrails catch unsafe requests
✓ Phase-2 roadmap: budget, live APIs, multilingual
"""
