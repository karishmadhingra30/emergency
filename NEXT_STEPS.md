# NEXT_STEPS: LangGraph Agent Architecture

This document describes the architectural direction for the emergency-response prototype.

The current codebase is a single-turn chatbot with RAG. Currently, it cannot do multi-step reasoning. Ex: a query like "I'm at this address, what do I do?" needs geocoding, then shelter lookup, then first-aid context, in that order. The shelter result also needs to inform the final answer.

LangGraph fits this use case because the interaction is not linear. Different queries need different tool sequences, and some need looping. Ex: if geocoding fails, the graph should ask the user to clarify instead of continuing. A directed graph with conditional edges expresses this more naturally than a chain.

[`agent_sketch.py`](./agent_sketch.py) is a minimal working skeleton of the design below.

---

## State

All nodes read from and write to a shared `AgentState`:

```python
class AgentState(TypedDict):
    user_message: str                         # the raw input
    location: Optional[dict]                  # {"lat": float, "lng": float, "address": str}
    intent: Optional[Literal[                 # set by the router
        "shelter_lookup",
        "first_aid",
        "general_prep",
        "needs_clarification",
    ]]
    tool_calls: list[dict]                    # log of tools invoked and their outputs
    response: Optional[str]                   # final synthesized answer
    error: Optional[str]                      # set if a node fails
```

Design choices:

- `tool_calls` is a list, because a single query might need multiple tools (Ex: geocode then shelter lookup). The synthesizer needs to see all of them to compose a coherent answer. also serves as an audit log.
- `intent` is optional because the router sets it mid-graph, not the user. Storing it in state lets downstream nodes read it without the router knowing about them.
- `error` is a field, not an exception, because LangGraph nodes should be pure state transforms. Raising exceptions mid-graph is not great. Writing `error` to state lets a downstream node give the user a graceful fallback.

---

## Graph structure (made with Claude)

```
                     ┌─────────┐
                     │  START  │
                     └────┬────┘
                          │
                          ▼
                     ┌─────────┐
                     │ router  │
                     │ (LLM)   │
                     └────┬────┘
                          │
         ┌────────────────┼────────────────┬──────────────────┐
         │                │                │                  │
         ▼                ▼                ▼                  ▼
    shelter_lookup   first_aid       general_prep       clarify_user
         │                │                │                  │
         ▼                │                │                  │
    geocode               │                │                  │
         │                │                │                  │
         └────────────────┴─────┬──────────┴──────────────────┘
                                ▼
                         ┌─────────────┐
                         │ synthesizer │
                         │   (LLM)     │
                         └──────┬──────┘
                                ▼
                             ┌─────┐
                             │ END │
                             └─────┘
```

### Nodes

- `router`: an LLM call that classifies the user's intent into one of four categories. Writes `intent` to state. Uses structured output (Pydantic) to force a valid category, so there is no free-form parsing.
- `geocode`: tool node. Takes an address from `user_message` or `location.address` and returns lat/lng. Only runs on the shelter lookup path, because first-aid and general prep usually do not need location.
- `shelter_lookup`: tool node wrapping the existing `ShelterManager` from `app.py`. Needs coordinates, so runs after `geocode`.
- `first_aid`: tool node wrapping the existing `pdf_processor.VectorDatabase` RAG retrieval.
- `general_prep`: tool node for preparedness content (currently the same vector DB, but logically separate, for example go-bag checklists).
- `clarify_user`: no-tool node. Sets `response` to a clarification question and routes to END.
- `synthesizer`: an LLM call that composes the final answer from `user_message`, `intent`, and all `tool_calls`. This is the only node that speaks to the user.

### Routing logic

The router writes `intent` to state. A single conditional edge function reads it and routes:

```python
def route_by_intent(state: AgentState) -> str:
    intent = state["intent"]
    if intent == "shelter_lookup":
        return "geocode"          # shelter needs location first
    elif intent == "first_aid":
        return "first_aid"
    elif intent == "general_prep":
        return "general_prep"
    else:
        return "clarify_user"
```

This keeps routing in one place instead of scattered across nodes. The router does not know where the graph goes next. That is the conditional edge's job. This separation makes it easy to add new intents later: add a branch to the router's classification, and a branch to this function.

---

## Tool abstraction

Every tool follows the same pattern:

```python
class ToolInput(BaseModel): ...
class ToolOutput(BaseModel): ...

def call_tool(state: AgentState) -> AgentState:
    # 1. Extract inputs from state
    # 2. Validate with ToolInput
    # 3. Call the underlying logic (existing ShelterManager, VectorDB, etc.)
    # 4. Wrap result in ToolOutput
    # 5. Append to state["tool_calls"] with {tool_name, input, output}
    # 6. Return updated state
```



### The geocoding tool

Geocoding is the new tool. Input: an address string, or the raw `user_message` if no explicit address. Output: `{lat, lng, formatted_address, confidence}`. It would use the Google Maps Geocoding API, which is already a dependency for shelter data.

If geocoding fails or returns low confidence, the tool writes `error` to state and the graph routes to `clarify_user` instead of continuing to shelter lookup.

---

## Out of scope for the first pass

- Streaming responses. The synthesizer would stream in production, but the sketch does not.
- Multi-turn conversation memory. State resets per request. evetually will need a checkpointer.
- Parallel tool calls. `shelter_lookup` and `first_aid` could run in parallel for some queries, but adding parallelism before the sequential version works will break the design.
- Real API integrations beyond what is already in the codebase.

---

## Tradeoffs

- vs. LangChain chains: chains are linear. This problem needs branching by intent and the possibility of looping for clarification. A graph expresses that directly.
- vs. raw Claude tool-use in a loop: that works for simpler agents, but ends up reimplementing state management, routing, and observability. LangGraph gives those primitives.
- vs. a custom state machine: same argument. LangGraph is a domain-specific library for this pattern, and its checkpointing and replay story is mature.

---

## Build order

Working backward from a demoable milestone:

1. `AgentState`, router node, and synthesizer node wired end-to-end with no tools. The router classifies, the synthesizer responds from the LLM only. This proves the graph plumbing works.
2. Wrap the existing `VectorDatabase` as the `first_aid` tool node. Smallest real tool, validates the wrapper pattern.
3. Add `geocode` and `shelter_lookup` nodes, wired sequentially. Most interesting path because it involves two tools in sequence with a data dependency.
4. Add `clarify_user` and the error path from geocoding. This is where the reactive agent behavior becomes visible.
5. Replace the current single-turn chatbot in `app.py` with the graph behind the same HTTP endpoint. No frontend changes needed.

 `agent_sketch.py` covers step 1 and stubs for step 2 and 3.
