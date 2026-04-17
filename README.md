# Emergency Response Prototype

A working prototype of an emergency-response web app combining a chatbot (first-aid guidance and shelter lookup) with an interactive map. Built as an exploration of what a low-connectivity, multilingual disaster-response tool could look like.

This is an **early-stage prototype**, iterated on with AI assistance. It runs end-to-end, but the code reflects rapid exploration rather than a finished architecture. The architectural direction I'm taking it - a LangGraph-based agent with multiple tools and conditional routing - is described in [NEXT_STEPS.md](./NEXT_STEPS.md), with an initial sketch in [`agent_sketch.py`](./agent_sketch.py).

## Current State

- **Chatbot with first-aid RAG**: local Gemma model (via Ollama) answers emergency first-aid questions, grounded in a vector database built from curated first-aid PDFs in [`Docs/`](./Docs) (Red Cross, WHO, Indian Army, SAS Survival, snakebite protocols)
- **Shelter lookup**: finds nearest shelters from an Excel dataset, returns distance-sorted results
- **Interactive map**: Leaflet-based map that displays shelter locations and chatbot results together
- **India-specific context**: emergency numbers (108, 100, 1078), mountain and flood safety guidance, snakebite-specific content

## Running it locally

Requires Python 3.9+, [Ollama](https://ollama.com) with the `gemma2:2b` model pulled, and (for shelter data generation) a Google Maps API key.

```bash
pip install -r requirements.txt
ollama pull gemma2:2b
ollama serve          # in a separate terminal
python app.py         # starts Flask server on :8080
```

Then open `http://localhost:8080`.

## Limitations

- Not a production system - error handling, observability, and resilience are minimal
- Not a finished agent - the current chatbot is a single-turn RAG loop, not a multi-step agent with tools
- Not multilingual yet - Hindi-first support is in the roadmap, not the code
- Not offline - Ollama runs locally but the map requires tiles

## Next Steps

See [NEXT_STEPS.md](./NEXT_STEPS.md) for the architectural direction: a LangGraph agent that routes by disaster type, calls tools for evacuation zones / AQI / shelter capacity / seismic data, and synthesizes multi-source answers. [`agent_sketch.py`](./agent_sketch.py) is a minimal working skeleton of that direction.

## Context

Built as a project for climate adaptation applications of LLM agents - specifically, how a low-connectivity emergency tool could serve users in disaster scenarios where the chatbot needs to do more than chat (look things up, combine sources, reason about what to do next).

## Repo contents

- `app.py` - Flask backend serving the chatbot + map
- `chatbot.py`, `gemma_chat.py` - chatbot logic and Ollama/Gemma integration
- `shelter_locator.py` - Google Maps shelter data fetcher
- `offline_map_plotter.py` - generates interactive Leaflet maps from Excel data
- `pdf_processor.py` - builds the first-aid vector database from PDFs in `Docs/`
- `first_aid_knowledge.py` - curated first-aid knowledge base
- `map_with_chat.html`, `index.html`, etc. - frontend
- `Docs/` - source first-aid PDFs (Red Cross, WHO, etc.)
- `vectordb/` - generated RAG vector database
- `shelters_downloaded.xlsx` - sample shelter dataset
- `agent_sketch.py` - exploratory LangGraph agent skeleton (see NEXT_STEPS.md)

## Development note

This prototype was built iteratively with AI coding assistance (Claude) - many short, exploratory commits no polished PRs. The cleanup reflected in recent commits and the `main` branch represents consolidating that exploration into something coherent to share.
