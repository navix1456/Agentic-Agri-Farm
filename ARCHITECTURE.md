# Agentic Farm Planner - Complete System Architecture

> **Phase-1 Implementation** | LLM-driven agentic architecture with safety-first design

## 🏗️ System Overview

The Agentic Farm Planner is a **multi-agent system** that autonomously routes user requests to specialized agents for seasonal farming guidance. The system prioritizes **transparency, safety, and explainability** through comprehensive guardrails and visible reasoning logs.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    📱 USER INTERFACE (Streamlit)                  │
│         Natural language input + Crop/State/Season selectors     │
│                     Demo target: ≤5 minutes                      │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                   🛡️  GUARDRAILS LAYER (Mandatory)               │
│  ┌──────────────────────┐      ┌──────────────────────┐         │
│  │  PII Redaction       │      │  Safety Enforcement  │         │
│  │  • Email masking     │      │  • Medical blocks    │         │
│  │  • Phone masking     │      │  • Chemical dosage   │         │
│  │  • Transparent logs  │      │  • Illegal content   │         │
│  └──────────────────────┘      └──────────────────────┘         │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│          🧠 SUPERVISOR AGENT (phi-3-mini via Ollama)              │
│  • LLM-based semantic intent inference (NOT keyword matching)    │
│  • Routes to specialist based on user intent                     │
│  • Returns: {intent, agent, reasoning}                           │
│  • Fallback: Semantic similarity if LLM unavailable              │
└────────────────────┬─────────────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
  ┌─────────┐  ┌─────────┐  ┌──────────┐
  │ PLANNER │  │  RISK   │  │  PEST /  │
  │  AGENT  │  │  AGENT  │  │  RNAi    │
  │         │  │         │  │ AGENT    │
  └────┬────┘  └────┬────┘  └────┬─────┘
       │            │            │
       └────────┬───┴────┬───────┘
                │        │
                ▼        ▼
        ┌────────────────────────┐
        │  DATA / TOOLS LAYER    │
        │  • Crop Calendar       │
        │  • Weather Assessment  │
        │  • Readiness Checklists│
        │  • Loaders & Formatters│
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  SESSION MEMORY STORE  │
        │  • Context persistence │
        │  • Conversation state  │
        │  • Decision history    │
        └────────────────────────┘
```

---

## 📋 Component Architecture

### 1️⃣ Guardrails Layer (Pre-Processing)

**Purpose:** Ensure safety, privacy, and ethical compliance before any agent processes input

**Components:**

#### PII Masking (`guardrails/pii.py`)
```
Input:  "My email is farmer@example.com"
Output: "My email is f***r@example.com" + flag=True
```
- **Email pattern:** `user@domain.com` → `u***@domain.com`
- **Phone pattern:** `9876543210` → `********10`
- **Transparent:** Logs show when/what was masked

#### Safety Filter (`guardrails/safety.py`)
```
Blocked keywords:
  • Medical: "prescription", "doctor", "cure", "disease"
  • Chemical: "pesticide", "dosage", "herbicide", "insecticide"
  • Illegal: "smuggle", "steal", "narcotic", "contraband"

Response: Advisory message + request block + logged action
```

**Flow:**
```
User Input
    ↓
PII Check → Mask sensitive data
    ↓
Safety Check → Block if unsafe
    ↓
If blocked: Show disclaimer + stop
If safe: Continue to Supervisor
```

---

### 2️⃣ Supervisor Agent (Intent Routing)

**File:** `agents/supervisor_agent.py`

**Purpose:** Route user requests to appropriate specialist agent using LLM reasoning

**Input:**
- Masked user text
- Context: `{crop, state, season}`
- Previous interactions (session memory)

**Process:**
```python
1. Build prompt with user intent + context
2. Call phi-3-mini via Ollama
3. Parse JSON response: {intent, agent, reason}
4. Return route decision
```

**Output:**
```json
{
  "intent": "season_planning",
  "agent": "planner_agent",
  "reason": "Supervisor inferred seasonal-planning intent via semantic similarity"
}
```

**Fallback Mechanism:**
- If Ollama unavailable → Use semantic similarity matching
- If parsing fails → Default to planner_agent
- **Always transparent:** Logs indicate which mode was used

**Key Feature:** 
❌ NO keyword matching (if "risk" in text → risk_agent)
✅ TRUE LLM inference (understands meaning, context, nuance)

---

### 3️⃣ Specialist Agents (Task Execution)

#### 📅 Planner Agent (`agents/planner_agent.py`)

**Input:** Crop, State, Season, Risk Map

**Data Sources:**
- `data/crop_calendar.json` - Monthly tasks per crop/region
- `data/weather_mock.json` - Risk levels per month
- `data/readiness_defaults.json` - Input checklists

**Output Format: TASK→WHEN→WHY→HOW→RISK**
```
Month: June
Task: Land prep and puddling
When: Early June
Why: Prepare for transplanting with monsoon onset
How: Puddle fields, maintain bunds
Risk: Medium (Monitor monsoon onset before transplanting)
```

**Readiness Checklist:**
```
Seed availability: Yes
Fertilizer type: Urea, DAP, K
Irrigation dependency: Canal/monsoon; keep 2-3 cm ponding
Labor intensity: High (10-12 people/hectare)
Weather flags: 
  • Watch monsoon onset
  • Plan harvest before northeast monsoon
```

**Key Features:**
- Risk-aware task sequencing (considers weather data)
- Color-coded UI (🟢 Low, 🟡 Medium, 🔴 High)
- Non-monetary checklist (practical requirements only)

---

#### 🌦️ Risk Agent (`agents/risk_agent.py`)

**Input:** State, Month

**Data Sources:**
- `data/weather_mock.json` - Regional monthly risks

**Output: Monthly Risk Assessment**
```
🟢 May: Low | Heat stress likely; plan irrigation windows
🟡 June: Medium | Monitor monsoon onset before transplanting
🔴 October: High | Cyclonic rain risk; secure harvest scheduling
```

**Logic:**
```
risk_level = weather_data[state][month]["level"]
alert = weather_data[state][month]["alert"]
```

**Key Features:**
- Color-coded visual summary (immediate risk understanding)
- Actionable alerts per month
- Region-specific (Tamil Nadu ≠ Punjab ≠ Maharashtra)

---

#### 🐛 Pest/RNAi Agent (`agents/pest_agent.py`)

**Input:** Crop type

**Output:**
```markdown
### Cotton Pest Management

🔬 Monitoring & Approach
Monitor for bollworm and whitefly; use trap-based monitoring first.

🧬 Why RNAi Technology?
RNAi targets pest genes precisely, reducing non-target impacts and resistance pressure.

🛡️ Safety & Best Practices
Avoid blanket chemical sprays. Prioritize scouting, pheromone traps, 
and RNAi-based precision strategies when available.
```

**Key Features:**
- Educational (explains RNAi benefits over chemicals)
- Safety-first (emphasizes non-chemical alternatives)
- Blocked from providing chemical dosages (guardrails)

---

### 4️⃣ Memory System (`memory/session_store.py`)

**Purpose:** Maintain context across multi-turn conversations

**Stored:**
```python
{
    "crop": "Rice",
    "location": "Tamil Nadu",
    "season": "Kharif",
    "last_agent": "planner_agent",
    "action_history": [
        {"query": "Plan Kharif rice", "agent": "planner_agent", "timestamp": ...},
        {"query": "Weather risks?", "agent": "risk_agent", "timestamp": ...}
    ]
}
```

**Scope:** Session-only (ephemeral, not persisted to disk)

**Usage:** Supervisor can reference previous context for follow-up queries

---

### 5️⃣ Data & Tools Layer

#### Crop Calendar Loader (`tools/crop_calendar_loader.py`)
```python
def select_calendar_entry(data, crop="Rice", state="Tamil Nadu", season="Kharif")
→ Returns: [task1, task2, ..., taskN] from JSON
```

**Data Structure:**
```json
{
  "Rice": {
    "Tamil Nadu": {
      "Kharif": [
        {"month": "June", "task": "Land prep and puddling", ...},
        {"month": "July", "task": "Transplanting", ...}
      ]
    }
  }
}
```

#### Weather API (`tools/weather_api.py`)
```python
def build_risk_map(data, state) → {month: {level, alert}}
```

**Uses:** weather_mock.json for deterministic testing

---

## 🔄 Complete Data Flow

### Example: "Plan Kharif rice in Tamil Nadu"

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                   │
│    "Plan Kharif rice in Tamil Nadu"                             │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ 2. GUARDRAILS                                                   │
│    ✓ No PII detected → PII Masked: False                       │
│    ✓ Safe content → Safety check passed                        │
│    → Proceed to Supervisor                                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ 3. SUPERVISOR INFERENCE                                         │
│    • LLM infers: intent = "season_planning"                    │
│    • Routes to: planner_agent                                  │
│    • Reason: "Semantic analysis detected planning request"     │
│    • Updates memory with {crop, location, season}             │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ 4. PLANNER AGENT EXECUTION                                      │
│    • Loads: crop_calendar.json[Rice][Tamil Nadu][Kharif]      │
│    • Loads: weather_mock.json[Tamil Nadu] for risk data        │
│    • Enriches tasks with risk levels from weather              │
│    • Builds readiness checklist from defaults                  │
│    • Formats output as TASK→WHEN→WHY→HOW→RISK                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ 5. RESPONSE FORMATTING (UI)                                     │
│    • Displays metrics: Rice | Tamil Nadu | Kharif | 6 tasks   │
│    • Shows month badges with green gradient                    │
│    • Color-codes risks: 🟢/🟡/🔴                               │
│    • Renders readiness checklist in columns                    │
│    • Adds critical alerts in red boxes                         │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│ 6. LOGS & TRANSPARENCY                                          │
│    • Supervisor Detected log shows:                            │
│      - Intent recognized                                       │
│      - Agent selected                                          │
│      - Reasoning visible                                       │
│      - PII masking status                                      │
│    • User can verify: "This is how the system understood me"  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Safety & Guardrails Strategy

### Multi-Layer Defense

**Layer 1: Input Validation**
- PII detection & masking
- Safety keyword filtering
- Malformed request rejection

**Layer 2: Agent Constraints**
- Planner: Can ONLY recommend actions (no chemical dosages)
- Pest: Can ONLY explain strategies (no prescription format)
- Risk: Can ONLY assess hazards (no medical advice)

**Layer 3: Output Monitoring**
- Responses checked for blocked terms before display
- Advisory disclaimers prepended to sensitive topics
- Logs make filtering transparent to users

**Layer 4: Transparency**
- All decisions logged with reasoning
- Users see what was blocked and why
- Builds trust through explainability

---

## 📊 Technology Stack

| Layer | Component | Technology | Notes |
|-------|-----------|-----------|-------|
| **LLM** | Intent Routing | phi-3-mini (Ollama) | 3.8B params, local |
| **UI/UX** | User Interface | Streamlit | Real-time, interactive |
| **Backend** | Agent Logic | Python 3.11+ | Custom lightweight framework |
| **Data** | Storage | JSON files | Static, version-controlled |
| **Memory** | Context Store | Python dict | Session-scoped, ephemeral |
| **Guardrails** | Safety | Custom filters | Regex + keyword matching |

---

## 🚀 Deployment Architecture

### Local Deployment (Phase-1)

```
User's Machine
├── Ollama service (running)
│   └── phi3:mini model (pulled)
├── Python 3.11+ environment
│   └── requirements.txt installed
├── Streamlit app
│   └── UI on localhost:8501
└── Static data files
    └── crop_calendar.json, weather_mock.json, etc.
```

**Setup:**
```bash
# 1. Start Ollama
ollama serve

# 2. In another terminal
cd Agentic-Agri-Farm-Planner
pip install -r requirements.txt
streamlit run ui/app.py
```

**Access:** http://localhost:8501

### Cloud Deployment (Phase-2)

**Option 1: Docker + Ollama**
```dockerfile
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "ui/app.py"]
```

**Option 2: API-Based (Azure OpenAI / Hugging Face)**
- Replace Ollama with cloud LLM
- Add authentication layer
- Implement rate limiting
- Deploy on Azure App Service or AWS ECS

---

## 📈 Phase-1 vs Phase-2 Roadmap

| Aspect | Phase-1 (Current) | Phase-2 (Future) |
|--------|-------------------|------------------|
| **LLM** | phi-3-mini (3.8B) | GPT-4 / Larger models + ensemble |
| **Data** | Static JSON mocks | Live APIs (weather, market prices, soil data) |
| **Memory** | Session dict | Vector DB (Pinecone/Weaviate) + semantic retrieval |
| **Budget** | Manual checklist | Automated cost optimization with ML |
| **Languages** | English only | Multilingual (Hindi, Marathi, Tamil) |
| **Personalization** | Context-based | User profiles + learning history |
| **Mobile** | Web only | Native mobile app |
| **Real-time** | Demo mode | Live IoT sensor integration |

---

## 🎯 Design Principles

### 1. **Agentic Behavior**
- LLM-driven reasoning, not keyword matching
- Agents make autonomous decisions based on context
- Supervisor intelligently routes to specialists

### 2. **Safety-First**
- Guardrails are mandatory, not optional
- Multi-layer defense against harmful outputs
- Transparent logging of all safety decisions

### 3. **Explainability**
- Every decision is logged with reasoning
- Users see logs in real-time
- No "black box" behavior

### 4. **Scalability**
- Modular agent design (easy to add new agents)
- Stateless architecture (scales horizontally)
- Data-driven (JSON files easily replaced with DBs)

### 5. **User-Centric**
- Demo-friendly (≤5 minutes to show all features)
- Beautiful, intuitive UI
- Clear, actionable outputs

---

## 🧪 Testing Strategy

### Unit Tests
- **Guardrails:** PII masking accuracy, safety filter coverage
- **Agents:** Output format validation, data loading
- **Memory:** Session state persistence, context updates

### Integration Tests
- **E2E flows:** User input → Guardrails → Supervisor → Agent → Output
- **Fallbacks:** Ollama unavailable, malformed data, edge cases

### Demonstration
- **Quick demos:** 3 buttons (Planner, Risk, Pest) pre-populated with sample queries
- **Guardrail demo:** Blocked request with visible log
- **Full flow:** Natural language query showing entire pipeline

---

## 📝 Code Structure

```
agents/
  ├── supervisor_agent.py   # Intent routing (LLM-based)
  ├── planner_agent.py      # Task generation
  ├── risk_agent.py         # Weather risk assessment
  └── pest_agent.py         # Pest management guidance

guardrails/
  ├── pii.py               # Email/phone masking
  ├── safety.py            # Blocked topic filtering
  └── __init__.py

data/
  ├── crop_calendar.json   # Rice, Wheat, Cotton per region
  ├── weather_mock.json    # Monthly risk data
  └── readiness_defaults.json # Checklist templates

tools/
  ├── crop_calendar_loader.py  # JSON loading
  ├── weather_api.py           # Weather data access
  └── __init__.py

memory/
  └── session_store.py     # Context persistence

ui/
  └── app.py              # Streamlit interface

tests/
  ├── test_guardrails.py
  └── test_agents.py
```

---

## ✅ Compliance Checklist

- ✓ **Agentic Behavior:** LLM-driven routing (not keyword matching)
- ✓ **Tool Usage:** JSON loaders, data transformers
- ✓ **Memory:** Session-scoped context persistence
- ✓ **Guardrails:** PII masking + safety filters
- ✓ **Transparency:** Reasoning logs visible to users
- ✓ **Completeness:** 4 agents (Supervisor + 3 specialists)
- ✓ **Clarity:** Formatted outputs with clear explanations
- ✓ **Adaptability:** Context-aware routing based on memory

---

**Last Updated:** January 2, 2026  
**Status:** Phase-1 Complete, Production-Ready  
**Demo Duration:** ≤5 minutes  
**Next Steps:** Phase-2 roadmap (APIs, personalization, multilingual)

## Agent Responsibilities

### 🧠 Supervisor Agent
- **Purpose:** Orchestrate all interactions
- **Input:** User query + context
- **Process:** LLM-based intent inference (phi-3-mini via Ollama)
- **Output:** Route decision as structured JSON
- **Key feature:** No keyword matching; purely reasoning-driven

### 📅 Planner Agent
- **Purpose:** Generate seasonal farm plans
- **Input:** Crop, state, season
- **Data sources:** crop_calendar.json, weather_mock.json, readiness_defaults.json
- **Output:** Month-wise tasks in TASK→WHEN→WHY→HOW→RISK format + readiness checklist
- **Key feature:** Risk-aware task sequencing

### 🌦️ Risk Agent
- **Purpose:** Assess weather-related risks
- **Input:** State, month
- **Data sources:** weather_mock.json
- **Output:** Monthly risk levels (Low/Medium/High) with alerts
- **Key feature:** Color-coded visual summaries

### 🐛 Pest/RNAi Agent
- **Purpose:** Provide pest management guidance
- **Input:** Crop or pest type
- **Data sources:** Static knowledge base
- **Output:** Scouting advice, RNAi benefits, safety warnings
- **Key feature:** No chemical dosages (blocked by guardrails)

## Data Flow

1. **User Input** → Guardrails (PII mask + safety check)
2. **Clean Input** → Supervisor (intent inference)
3. **Route Decision** → Specialist Agent
4. **Agent Query** → Data/Tools Layer
5. **Response** → Memory Store (update context)
6. **Output** → User Interface (formatted display)
7. **Logs** → Transparency Panel (reasoning visible)

## Memory Management

Session store maintains:
- Current crop/location/season
- Last invoked agent
- Action history (for multi-turn conversations)

**Scope:** Session-level only (no persistence across restarts)
**Future:** Phase-2 will add vector DB for semantic memory

## Guardrails Implementation

### PII Masking
- **Email:** `farmer@example.com` → `f***r@example.com`
- **Phone:** `9876543210` → `********10`

### Safety Filters
Blocked topics:
- Medical advice
- Chemical dosage instructions
- Illegal/contraband content

Response: Advisory disclaimer + block action

## Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | phi-3-mini (Ollama) |
| UI | Streamlit |
| Language | Python 3.11+ |
| Data | Static JSON files |
| Agent Framework | Custom (lightweight) |
| Memory | In-memory dict |

## Phase-1 vs Phase-2

| Feature | Phase-1 (Now) | Phase-2 (Future) |
|---------|---------------|------------------|
| LLM | phi-3-mini | Larger models + ensembles |
| Data | Static mock | Live APIs (weather, market) |
| Memory | Session dict | Vector DB + embeddings |
| Budget | Checklist only | Full cost optimization |
| UX | English only | Multilingual support |
| Deployment | Local | Cloud-ready |
