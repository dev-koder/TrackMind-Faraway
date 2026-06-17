# TrackMind 🚄
### Autonomous Railway Cascade Intelligence System

> *Multi-agent AI that detects cascading delays, quantifies passenger impact, and autonomously generates operational responses — demonstrated on a digital twin of the Delhi-Howrah corridor.*

Built for **FAR AWAY 2026** — India's Biggest International Hackathon  
Theme: **Railways × Agentic & Autonomous Systems**

---

## The Problem

Indian Railways runs 13,000 trains daily across 68,000 km of track serving 23 million passengers.

When one train is delayed, it cascades. Trains share tracks. Stations get congested. Passengers miss connections. Today, railway operations staff detect and respond to these cascades manually — slow, inconsistent, and reactive.

**Nobody has autonomous intelligence for this.**

---

## What TrackMind Does

One delay event triggers a council of 5 autonomous agents, each with a dedicated role:

| Agent | Role |
|---|---|
| 🔍 Monitor | Detects delay and classifies severity |
| 🌿 Cascade | Maps downstream train and station impacts |
| 👥 Impact | Quantifies passenger disruption in real numbers |
| ⚡ Response | Generates 2 options with competing trade-offs |
| 📡 Comms | Drafts announcements in English, Hindi, and SMS |

A **6th arbitration engine** runs a weighted vote across agents — with competing objectives surfaced honestly — and produces a final recommendation with confidence score.

**Every decision is fully explainable. Nothing is a black box.**

---

## Demo

```
Delay injected: Train 12301 Rajdhani Express, +47 minutes at Kanpur Central

[Monitor]   → Delay detected: HIGH severity
[Cascade]   → 3 trains affected: 12302, 13005, 12381
[Impact]    → 2,847 passengers affected | 203 missed connections
[Response]  → Option A: Hold at ALD (saves 203 connections, +18 min cost)
              Option B: Proceed and reroute (saves 89 connections, +6 min cost)
[Comms]     → Announcements drafted in English + Hindi + SMS
[Arbitrate] → Option A recommended (87% confidence, 2:1 weighted vote)

Total time: 19 seconds
```

---

## Technical Architecture

```
React + D3.js + Tailwind
        ↕ WebSocket
FastAPI + Async Python
        ↕
5 Claude Agents (claude-sonnet-4-6)
        +
Arbitration Engine
        +
Delhi-Howrah Digital Twin (corridor.json)
```

The digital twin is built from publicly available Indian Railways schedule data for the Delhi-Howrah corridor — 6 major stations, 6 trains, real schedules, realistic delay injection.

---

## Why This Is Genuinely Agentic

Most "multi-agent" systems are pipelines. TrackMind has competing objectives:

- The **Response Agent** models two goals simultaneously: minimize delay (efficiency) vs minimize passenger disruption (service quality). These conflict. Both options are surfaced.
- The **Arbitration Engine** runs a weighted vote. Impact Agent (weight 3) and Response Agent (weight 3) can disagree — when they do, the system flags for human review instead of auto-resolving.

This is goal-directed reasoning with explicit trade-offs. Not a workflow.

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key

### Backend
```bash
cd trackmind/backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt   # Windows
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
.\venv\Scripts\uvicorn main:app --port 8000
```

### Frontend
```bash
cd trackmind/frontend
npm install
npm run dev
```

Open `http://localhost:5173`

> **Note:** The system works without an API key — all agents have fallback responses so the demo always runs.

---

## Data Sources

- Train schedules: Indian Railways official timetable (public)
- Station coordinates: Public geographic data
- Occupancy assumptions: Indian Railways published punctuality and ridership statistics
- Delay scenarios: Modeled on real-world Indian Railways delay patterns

This is a digital twin — a simplified, verified simulation — not a connection to live railway systems.

---

## Built With

- [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- [D3.js](https://d3js.org/) — network graph
- [Tailwind CSS](https://tailwindcss.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Anthropic Claude](https://anthropic.com/) — agent intelligence
- [Recharts](https://recharts.org/) — data visualization

---

## Team Bleach
### Dev Kushwaha

<!-- Add team names -->

---

*FAR AWAY 2026 — The goal is not to write every line of code yourself. The goal is to build something meaningful.*
