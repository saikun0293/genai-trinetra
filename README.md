# Trinetra 🔍

**An AI-driven agentic framework for automated quality assurance in transaction workflows**

Built for the 2025 GenAI Hackathon using Google's Agent Development Kit (ADK) and Vertex AI. 

## Problem Statement

The traditional 4-eye check (maker-checker) process suffers from: 
- **Rubber Stamp Effect**: Duplication without real scrutiny, creating false comfort
- **Latency Bottlenecks**: 2-6 hour delays in workflows
- **Collusive Blind Spots**: Vulnerability to human collusion
- **Operational Delays**: Increased risk exposure and inconsistent control effectiveness

## Solution

Trinetra implements an AI-powered agentic system that: 

✅ **Automates parallel synthetic reviews** to validate transactions or workflows  
✅ **Detects anomalies** and escalates them to human reviewers with context  
✅ **Maintains vigilance** by running agent vs. human performance reviews  
✅ **Provides AI decision support** and reasoning before human reviewers act  
✅ **Enables pre-investigative triage** for early anomaly detection  
✅ **Adapts through learning loops** based on rejected or reviewed cases

## Architecture

```
├── app/                    # Main agent logic
│   ├── agent. py           # Primary orchestration agent
│   └── sub_agents/        # Specialized review agents
├── frontend/              # User interface
├── deployment/            # Terraform infrastructure (GCP)
├── tests/                 # Test suites
└── context/               # ADK samples and documentation
```

## Technology Stack

- **Agent Framework**: Google Agent Development Kit (ADK)
- **AI Platform**: Google Vertex AI
- **Infrastructure**: Google Cloud Platform
- **Languages**: Python, TypeScript
- **IaC**: Terraform

## Quick Start

To use ADK command you need to activate virtual environment

```
cd ~/genai-hackathon
uv sync
source .venv/bin/activate
adk web
```

### Running the app

- Frontend: `cd frontend && npm run dev`
- Backend: `cd app && uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --reload`

See [app/API_SERVER_README.md](app/API_SERVER_README.md) for details on using custom endpoints alongside the agent.


## Features

🔍 **Synthetic Reviews**: Parallel AI agents validate transactions independently  
🚨 **Anomaly Detection**:  Pattern recognition and risk scoring  
🤝 **Human-in-the-Loop**: Escalation with full context and reasoning

*Developed for the 2025 GenAI Hackathon Challenge - Trinetra*
