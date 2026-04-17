"""
agent_sketch.py

Minimal LangGraph skeleton for the emergency-response agent.
See NEXT_STEPS.md for the full architectural direction.

This covers step 1 from the build order: router + synthesizer wired
end-to-end, with tool nodes stubbed. Real tool wrappers are TODO.

Run:
    pip install langgraph anthropic python-dotenv
    # Set ANTHROPIC_API_KEY in .env
    python agent_sketch.py
"""

from __future__ import annotations

import os
from typing import Literal, Optional, TypedDict

from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

load_dotenv()
client = Anthropic()  # reads ANTHROPIC_API_KEY from environment


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    user_message: str
    location: Optional[dict]
    intent: Optional[Literal[
        "shelter_lookup",
        "first_aid",
        "general_prep",
        "needs_clarification",
    ]]
    tool_calls: list[dict]
    response: Optional[str]
    error: Optional[str]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

ROUTER_PROMPT = """You are a router for an emergency response assistant.
Classify the user's message into exactly one of these categories:

- shelter_lookup: user is asking to find a shelter, safe location, or where to go
- first_aid: user is asking about medical treatment, injuries, or first aid
- general_prep: user is asking about disaster preparation, go-bags, or general readiness
- needs_clarification: the message is unclear, off-topic, or missing critical info

Respond with ONLY the category name, nothing else. No punctuation, no explanation.
"""


def router_node(state: AgentState) -> AgentState:
    """Classify the user's intent using Claude."""
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=20,
        system=ROUTER_PROMPT,
        messages=[{"role": "user", "content": state["user_message"]}],
    )
    raw_intent = message.content[0].text.strip().lower()

    # Validate against allowed values, fall back to clarification
    valid = {"shelter_lookup", "first_aid", "general_prep", "needs_clarification"}
    intent = raw_intent if raw_intent in valid else "needs_clarification"

    return {**state, "intent": intent}


# ---------------------------------------------------------------------------
# Tool nodes (stubbed, see NEXT_STEPS.md for real implementations)
# ---------------------------------------------------------------------------

def geocode_node(state: AgentState) -> AgentState:
    """Stub: would call Google Maps Geocoding API. Returns fake coords."""
    fake_result = {
        "lat": 37.8715,
        "lng": -122.2730,
        "formatted_address": "Berkeley, CA, USA",
        "confidence": "high",
    }
    tool_call = {"tool": "geocode", "input": state["user_message"], "output": fake_result}
    return {
        **state,
        "location": fake_result,
        "tool_calls": state["tool_calls"] + [tool_call],
    }


def shelter_lookup_node(state: AgentState) -> AgentState:
    """Stub: would wrap existing ShelterManager from app.py."""
    fake_shelters = [
        {"name": "MLK Middle School", "distance_km": 1.2, "type": "school"},
        {"name": "Berkeley Fire Station 3", "distance_km": 2.0, "type": "fire_station"},
    ]
    tool_call = {"tool": "shelter_lookup", "input": state["location"], "output": fake_shelters}
    return {**state, "tool_calls": state["tool_calls"] + [tool_call]}


def first_aid_node(state: AgentState) -> AgentState:
    """Stub: would wrap existing pdf_processor.VectorDatabase."""
    fake_excerpt = (
        "For severe bleeding: apply firm direct pressure with a clean cloth. "
        "Do not remove the cloth if it soaks through; add another layer on top."
    )
    tool_call = {"tool": "first_aid", "input": state["user_message"], "output": fake_excerpt}
    return {**state, "tool_calls": state["tool_calls"] + [tool_call]}


def general_prep_node(state: AgentState) -> AgentState:
    """Stub: would retrieve preparedness content."""
    fake_excerpt = "Basic go-bag: water, non-perishable food, flashlight, first-aid kit, cash, copies of ID."
    tool_call = {"tool": "general_prep", "input": state["user_message"], "output": fake_excerpt}
    return {**state, "tool_calls": state["tool_calls"] + [tool_call]}


def clarify_user_node(state: AgentState) -> AgentState:
    """Short-circuit: ask the user for more info, skip synthesis."""
    return {
        **state,
        "response": "I need more context to help. Can you tell me your location or what kind of emergency you're facing?",
    }


# ---------------------------------------------------------------------------
# Synthesizer
# ---------------------------------------------------------------------------

SYNTHESIZER_PROMPT = """You are an emergency response assistant. The user asked a question,
and the system ran tools to gather relevant information. Your job is to compose a clear,
calm, and actionable response using the tool outputs.

Keep the response brief and direct. If the information is incomplete, say so honestly
rather than guessing.
"""


def synthesizer_node(state: AgentState) -> AgentState:
    """Compose the final response from user_message + tool_calls."""
    context_lines = [f"User asked: {state['user_message']}", f"Intent: {state['intent']}", ""]
    for tc in state["tool_calls"]:
        context_lines.append(f"Tool `{tc['tool']}` returned: {tc['output']}")

    context = "\n".join(context_lines)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SYNTHESIZER_PROMPT,
        messages=[{"role": "user", "content": context}],
    )
    response_text = message.content[0].text

    return {**state, "response": response_text}


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def route_by_intent(state: AgentState) -> str:
    """Conditional edge: decide which node runs after the router."""
    intent = state["intent"]
    if intent == "shelter_lookup":
        return "geocode"            # shelter lookup needs location first
    elif intent == "first_aid":
        return "first_aid"
    elif intent == "general_prep":
        return "general_prep"
    else:
        return "clarify_user"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph():
    """Wire nodes and edges into a compiled LangGraph."""
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("router", router_node)
    graph.add_node("geocode", geocode_node)
    graph.add_node("shelter_lookup", shelter_lookup_node)
    graph.add_node("first_aid", first_aid_node)
    graph.add_node("general_prep", general_prep_node)
    graph.add_node("clarify_user", clarify_user_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Entry: START -> router
    graph.add_edge(START, "router")

    # Conditional routing from the router based on intent
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "geocode": "geocode",
            "first_aid": "first_aid",
            "general_prep": "general_prep",
            "clarify_user": "clarify_user",
        },
    )

    # Shelter lookup path: geocode -> shelter_lookup -> synthesizer
    graph.add_edge("geocode", "shelter_lookup")
    graph.add_edge("shelter_lookup", "synthesizer")

    # First-aid and general-prep paths go straight to synthesizer
    graph.add_edge("first_aid", "synthesizer")
    graph.add_edge("general_prep", "synthesizer")

    # Clarification short-circuits to END (no synthesis needed)
    graph.add_edge("clarify_user", END)

    # Synthesizer always terminates
    graph.add_edge("synthesizer", END)

    return graph.compile()


def run_query(user_message: str) -> dict:
    """Convenience wrapper: invoke the graph with an initial state."""
    graph = build_graph()
    initial_state: AgentState = {
        "user_message": user_message,
        "location": None,
        "intent": None,
        "tool_calls": [],
        "response": None,
        "error": None,
    }
    return graph.invoke(initial_state)


if __name__ == "__main__":
    queries = [
        "I'm bleeding badly, what do I do?",
        "Where's the nearest shelter?",
        "What should I pack in a go-bag?",
    ]

    for q in queries:
        print(f"\n{'='*60}\nQ: {q}\n{'='*60}")
        result = run_query(q)
        print(f"Intent classified: {result['intent']}")
        print(f"Tools called: {[tc['tool'] for tc in result['tool_calls']]}")
        print(f"\nResponse:\n{result['response']}")
