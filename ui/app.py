from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.planner_agent import build_readiness, format_tasks, generate_plan
from agents.pest_agent import explain_pest
from agents.risk_agent import full_risk_map, summarize_risks
from agents.supervisor_agent import SupervisorAgent
from guardrails.pii import redact_and_flag
from guardrails.safety import enforce_safety
from memory.session_store import SessionStore
from tools.crop_calendar_loader import load_calendar
from tools.weather_api import load_weather

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@st.cache_data(show_spinner=False)
def load_static_data() -> Dict[str, Any]:
    calendar = load_calendar(DATA_DIR / "crop_calendar.json")
    weather = load_weather(DATA_DIR / "weather_mock.json")
    with (DATA_DIR / "readiness_defaults.json").open("r", encoding="utf-8") as f:
        readiness = json.load(f)
    return {"calendar": calendar, "weather": weather, "readiness": readiness}


def main() -> None:
    st.set_page_config(page_title="Agentic Farm Demo", layout="wide", page_icon="🌾")
    
    # Custom color scheme
    st.markdown("""
        <style>
            .main {
                padding-top: 2rem;
            }
            h1, h2, h3 {
                color: #2d5016;
            }
            [data-testid="metric-container"] {
                background-color: #2d5016 !important;
                border-radius: 10px !important;
                padding: 1.2rem !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            [data-testid="metric-container"] > div:first-child {
                color: #ffffff !important;
                font-weight: 600;
            }
            [data-testid="metric-container"] > div:nth-child(2) {
                color: #c8e6c9 !important;
                font-size: 1.8rem !important;
                font-weight: bold !important;
            }
            .task-month {
                font-size: 1.8rem;
                font-weight: bold;
                color: #2d5016;
                background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
                padding: 0.8rem;
                border-radius: 6px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("# 🌾 Seasonal Farm Planner & Risk Alert")
    st.markdown("### Phase-1 Agentic AI Demo")
    st.caption("🤖 phi-3-mini via Ollama | Supervisor + Planner/Risk/Pest agents | 🛡️ Guardrails + 🧠 Memory")
    
    # Info expander
    with st.expander("ℹ️ About this demo"):
        st.markdown("""
        **What this demonstrates:**
        - ✅ Autonomous supervisor agent routing (LLM-driven, not keyword matching)
        - ✅ Task agents: Planner (calendar + readiness), Risk (weather alerts), Pest/RNAi (safety guidance)
        - ✅ Guardrails: PII masking (email/phone) + safety filters (medical/chemical/illegal topics)
        - ✅ Session memory: persists crop/location/season context across interactions
        - ✅ Transparent logs: see supervisor reasoning and guardrail actions
        
        **Phase-2 (deferred):** Budget optimization, live weather APIs, multilingual support, market pricing
        
        
        """)

    if "store" not in st.session_state:
        st.session_state["store"] = SessionStore()
    if "logs" not in st.session_state:
        st.session_state["logs"] = []

    data = load_static_data()
    calendar = data["calendar"]
    weather = data["weather"]
    readiness_defaults = data["readiness"]

    col_input, col_logs = st.columns([2, 1])

    with col_input:
        st.subheader("🎯 User Request")
        
        # Demo prompt buttons
        st.markdown("**Quick demos:**")
        demo_cols = st.columns(3)
        with demo_cols[0]:
            if st.button("📅 Planner", use_container_width=True):
                st.session_state["demo_input"] = "Plan Kharif rice in Tamil Nadu"
        with demo_cols[1]:
            if st.button("🌦️ Risk", use_container_width=True):
                st.session_state["demo_input"] = "What are weather risks for Maharashtra?"
        with demo_cols[2]:
            if st.button("🐛 Pest/RNAi", use_container_width=True):
                st.session_state["demo_input"] = "How to control pests in cotton safely?"
        
        user_input = st.text_area(
            "Describe your farming need:",
            value=st.session_state.get("demo_input", ""),
            height=100,
            placeholder="e.g., Plan Kharif rice in Tamil Nadu, What are weather risks?, How to handle pests?"
        )
        
        col_crop, col_state, col_season = st.columns(3)
        with col_crop:
            crop = st.selectbox("🌱 Crop", ["Rice", "Wheat", "Cotton"], index=0)
        with col_state:
            state = st.selectbox("📍 Location", ["Tamil Nadu", "Punjab", "Maharashtra"], index=0)
        with col_season:
            season = st.selectbox("📆 Season", ["Kharif", "Rabi"], index=0)

        supervisor = SupervisorAgent(model="phi3:mini", endpoint="http://localhost:11434/api/chat", mock=False)

        if st.button("🚀 Run Agent", type="primary", use_container_width=True):
            if not user_input.strip():
                st.warning("⚠️ Please enter a request first.")
                return
                
            masked_text, pii_flag = redact_and_flag(user_input)
            allowed, safety_msg = enforce_safety(user_input)
            
            if pii_flag:
                st.info("🔒 PII detected and masked in your input.")
            
            if not allowed:
                st.error(f"🛡️ Safety Filter Blocked: {safety_msg}")
                st.session_state["logs"].append({"event": "safety_block", "message": safety_msg})
                return

            context = {"crop": crop, "state": state, "season": season}
            route = supervisor.route(masked_text, context)

            st.session_state["store"].update(crop=crop, location=state, season=season, last_agent=route.get("agent"))
            st.session_state["logs"].append({"event": "supervisor", "route": route, "pii_masked": pii_flag})

            risk_map = full_risk_map(state, weather)

            if route.get("agent") == "planner_agent":
                plan = generate_plan(calendar, crop, state, season, risk_map)
                checklist = readiness_defaults.get(crop, {}).get(state, {})
                readiness = build_readiness(checklist)
                
                st.success("✅ Planner Agent Output")
                
                # Header with context
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🌱 Crop", plan['crop'])
                with col2:
                    st.metric("📍 Location", plan['state'])
                with col3:
                    st.metric("📆 Season", plan['season'])
                with col4:
                    st.metric("📋 Tasks", len(plan.get("tasks", [])))
                
                st.divider()
                
                if plan.get("tasks"):
                    st.markdown("### 📅 Month-wise Task Plan")
                    st.caption("Format: **TASK → WHEN → WHY → HOW → RISK**")
                    
                    for idx, task in enumerate(plan["tasks"], 1):
                        # Month badge at the top
                        month = task.get('month') or task.get('when', 'N/A')
                        if not month or month == '':
                            month = 'TBD'
                        
                        st.markdown(f"<div class='task-month'>📅 **{month}**</div>", unsafe_allow_html=True)
                        
                        with st.container(border=True):
                            # Main task title
                            st.markdown(f"#### ✅ {task.get('task', '')}")
                            
                            # Info in columns for better layout
                            info_col1, info_col2 = st.columns([1, 1])
                            
                            with info_col1:
                                st.markdown(f"**⏰ When:** {task.get('when', '')}")
                                st.markdown(f"**💡 Why:** {task.get('why', '')}")
                            
                            with info_col2:
                                st.markdown(f"**🔧 How:** {task.get('how', '')}")
                            
                            # Risk assessment
                            st.divider()
                            risk_level = task.get('risk', 'Medium')
                            
                            if 'High' in risk_level or 'Delayed' in risk_level or 'stress' in risk_level.lower() or 'storm' in risk_level.lower():
                                st.warning(f"⚠️ **Risk Level:** 🔴 **{risk_level}**")
                            elif 'Medium' in risk_level or 'rain' in risk_level.lower() or 'humidity' in risk_level.lower():
                                st.info(f"ℹ️ **Risk Level:** 🟡 **{risk_level}**")
                            else:
                                st.success(f"✓ **Risk Level:** 🟢 **{risk_level}**")
                            
                            # Critical alerts
                            if task.get("risk_alert"):
                                st.error(f"🚨 **Critical Alert:** {task['risk_alert']}")
                        
                        st.write("")  # Spacing between tasks
                else:
                    st.warning(plan.get("note", "No tasks available."))

                st.divider()
                
                # Readiness checklist in columns
                st.markdown("### 📦 Input Readiness Checklist")
                st.caption("Non-monetary requirements for this season")
                
                checklist_cols = st.columns(2)
                for idx, (key, value) in enumerate(readiness.items()):
                    with checklist_cols[idx % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{key}**")
                            if isinstance(value, list):
                                for item in value:
                                    st.markdown(f"  • {item}")
                            else:
                                st.markdown(f"`{value}`")

            elif route.get("agent") == "risk_agent":
                st.warning("⚠️ Risk Agent Output")
                st.markdown(f"### 🌦️ Weather Risk Assessment: {state}")
                st.caption("Monthly risk levels and alerts")
                
                risk_map = full_risk_map(state, weather)
                risk_lines = summarize_risks(risk_map)
                
                # Display in columns for better layout
                risk_cols = st.columns(2)
                for idx, line in enumerate(risk_lines):
                    with risk_cols[idx % 2]:
                        if "🔴" in line:
                            st.error(line)
                        elif "🟡" in line:
                            st.warning(line)
                        else:
                            st.success(line)

            elif route.get("agent") == "pest_agent":
                st.info("🐛 Pest / RNAi Agent Output")
                pest = explain_pest(crop)
                
                st.markdown(f"### {pest['topic'].title()} Pest Management")
                
                with st.container(border=True):
                    st.markdown("**🔬 Monitoring & Approach**")
                    st.markdown(pest['explanation'])
                
                st.divider()
                
                with st.container(border=True):
                    st.markdown("**🧬 Why RNAi Technology?**")
                    st.markdown(pest['why_rnai'])
                
                st.divider()
                
                with st.container(border=True):
                    st.markdown("**🛡️ Safety & Best Practices**")
                    st.markdown(pest['safety'])

            else:
                st.write("❌ No agent selected.")

    with col_logs:
        st.subheader("🔍 Agent Reasoning / Logs")
        st.caption("Transparency: See supervisor routing & guardrail actions")
        
        if not st.session_state["logs"]:
            st.info("No logs yet. Run an agent to see reasoning.")
        
        for log in reversed(st.session_state["logs"][-5:]):  # Show last 5
            if log.get("event") == "supervisor":
                route = log.get("route", {})
                st.code(
                    f"🧠 Supervisor Detected:\n"
                    f"Intent: {route.get('intent')}\n"
                    f"Agent: {route.get('agent')}\n"
                    f"Reason: {route.get('reason')}\n"
                    f"PII Masked: {log.get('pii_masked')}\n"
                    f"Note: Repeated intents may reuse cached routing from session memory."
                )
            elif log.get("event") == "safety_block":
                st.code(f"🛡️ Blocked: {log.get('message')}")

        st.caption("")
        
        # Add clear logs button
        if st.button("🗑️ Clear Logs"):
            st.session_state["logs"] = []
            st.rerun()


if __name__ == "__main__":
    main()
