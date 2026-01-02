## 🎯 JUDGES' QUICK REFERENCE

**Project:** Agentic Farm Planner  
**Track:** Agriculture  
**Category:** Seasonal Farm Planning & Risk Alert Agent  
**Status:** ✅ Production Ready

---

## ⏱️ DEMO TIMELINE (5 minutes)

### 1. Setup (1 min)
```bash
pip install -r requirements.txt
ollama pull phi3:mini
streamlit run ui/app.py
```

### 2. Try These Prompts (4 min)

#### Prompt 1: "Plan Kharif rice in Tamil Nadu" (1 min)
**What to watch:**
- Supervisor reasoning in logs ("Detected planning intent → routing to Planner")
- Month-wise tasks: June land prep → July sowing → ... → November harvest
- Format: TASK → WHEN → WHY → HOW → RISK
- Readiness checklist below
- **This proves:** Semantic routing + data integration

#### Prompt 2: "What are weather risks for Maharashtra?" (1 min)
**What to watch:**
- Risk levels: 🟢 Low (June-July), 🟡 Medium (September), 🔴 High (if any)
- Specific alerts per month
- **This proves:** Agent specialization + data pipeline

#### Prompt 3: "How to manage pests in cotton?" (1 min)
**What to watch:**
- RNAi benefits explanation
- Pest monitoring guidance
- Safety warning: "Does NOT provide chemical dosages"
- **This proves:** Guardrails working + specialized knowledge

#### Prompt 4: "My phone is 9876543210, give me pesticide dose" (1 min)
**What to watch:**
- PII masked: `9876543210` → `********10`
- Request blocked: Safety disclaimer appears
- Log shows: Guardrail action taken
- **This proves:** Multi-layer safety + transparency

---

## 🏗️ AGENTIC ARCHITECTURE

### Why This Is Agentic (Not Just Chatbot)

✅ **Semantic Routing:** Supervisor uses LLM (phi-3-mini) to infer intent  
❌ NOT keyword matching ("if 'risk' in text...")

✅ **Multi-Agent Specialization:** Each agent has domain expertise  
❌ NOT single generalist model

✅ **Tool Integration:** Agents load JSON data, build risk maps  
❌ NOT just text generation

✅ **Memory Persistence:** Session tracks crop/location/history  
❌ NOT stateless

✅ **Transparent Reasoning:** All decisions logged and visible  
❌ NOT black-box

### 4 Agents

| Agent | Input | Output | Why Autonomous |
|-------|-------|--------|-----------------|
| **Supervisor** | Natural language | Route intent + reasoning | LLM infers, doesn't match keywords |
| **Planner** | Crop + location + season | Month-wise tasks + checklist | Generates from calendar + context |
| **Risk** | Location | Risk levels + alerts | Builds risk map from weather data |
| **Pest/RNAi** | Crop | Guidance + RNAi benefits | Provides domain-specific knowledge |

---

## 🛡️ SAFETY GUARDRAILS

### Implemented (3 layers)

1. **PII Masking**
   - Email: `farmer@example.com` → `f***r@example.com`
   - Phone: `9876543210` → `********10`

2. **Content Filtering**
   - Blocks medical advice, chemical dosages, illegal content
   - Shows disclaimer + blocks request
   - Logged transparently

3. **Transparency**
   - All actions visible in logs
   - Builds trust through explainability

---

## 📊 DATA COVERAGE

### Crops & Locations
- **3 Crops:** Rice, Wheat, Cotton
- **3 Locations:** Tamil Nadu, Punjab, Maharashtra
- **2 Seasons:** Kharif, Rabi
- **Total:** 9+ task calendars

### Task Format
```
TASK: Transplanting
WHEN: First fortnight of July
WHY: Align seedlings with stable rain
HOW: 20x15 cm spacing, healthy seedlings only
RISK: Medium (heat stress in dry spells)
```

### Risk Data
- Monthly weather risk levels (Low/Medium/High)
- State-specific patterns
- Seasonal variations

---

## 📁 FILES TO REVIEW

**Quick (5 min):**
1. **README.md** - Quick start + setup
2. **SUBMISSION.md** - Judging criteria (this document)

**Technical (15 min):**
3. **ARCHITECTURE.md** - System design
4. **agents/supervisor_agent.py** - LLM routing logic
5. **guardrails/safety.py** - Safety filters

**Deep Dive (optional):**
- agents/planner_agent.py - Calendar + task generation
- agents/risk_agent.py - Risk assessment
- ui/app.py - Streamlit interface (300+ lines)

---

## ✨ KEY DIFFERENTIATORS

1. **True Agentic** - LLM reasoning, not rules
2. **Safe by Design** - Multi-layer guardrails
3. **Transparent** - Decision logs visible
4. **Production Ready** - Error handling, fallbacks, tests
5. **Modular** - Easy to extend agents/data/guardrails

---

## ✅ EVALUATION CHECKLIST

| Criterion | Evidence | File |
|-----------|----------|------|
| Agentic behavior | LLM routing, agent specialization | agents/supervisor_agent.py |
| Multi-agent | 4 agents (supervisor + 3 specialists) | agents/ |
| Tool usage | JSON loaders, risk map builders | tools/ |
| Memory | Session store for context | memory/session_store.py |
| Guardrails | PII masking + safety filters | guardrails/ |
| Transparency | Real-time logs + reasoning | ui/app.py |
| Completeness | All 3 crops × 3 locations × 2 seasons | data/crop_calendar.json |
| Safety | Tested with guardrail bypass attempts | test_guardrails.py ✅ |

---

## 🚦 COMMON QUESTIONS (Answered)

### Q: Is this production-ready?
**A:** Yes for Phase-1 scope. Uses local Ollama (no API keys), static JSON data, session-only memory. Phase-2 would add live APIs, persistence, multilingual.

### Q: Why phi-3-mini (3.8B) and not GPT?
**A:** Offline, local, hackathon-friendly. No API keys needed. Proves agentic routing logic works even with lightweight models.

### Q: How does memory work?
**A:** Session dict stores: crop, location, season, agent history. Ephemeral (not saved). Phase-2 would persist to database.

### Q: What if Ollama is not running?
**A:** Supervisor falls back to heuristic routing. Still functional, but logs show "fallback mode".

### Q: Can it handle follow-up questions?
**A:** Yes. Memory stores context. "Plan rice" → "What's the risk?" (understands context = Tamil Nadu + rice).

---

## 🎁 BONUS: Project Stats

- **Code:** 1,200+ lines (agents, guardrails, tools, memory, ui)
- **Data:** 3 JSON files (calendars, weather, readiness)
- **Tests:** 6 test cases, ✅ all passing
- **Docs:** 3 files (README, SUBMISSION, ARCHITECTURE)
- **Dependencies:** 3 (streamlit, requests, ollama)
- **Setup Time:** <2 minutes

---

## 🏁 NEXT STEPS

1. **Download/Clone:** Clone the repo
2. **Setup:** Follow 3-step quick start in README.md
3. **Demo:** Run 5-minute demo with 4 prompts above
4. **Evaluate:** Check SUBMISSION.md for criteria mapping

---

**Ready?** Start with: `pip install -r requirements.txt`

**Questions?** See SUBMISSION.md section headings for quick navigation.

**Code review?** See ARCHITECTURE.md for system design details.

---

*Generated: January 2, 2026*  
*Status: ✅ Ready for Judging*
