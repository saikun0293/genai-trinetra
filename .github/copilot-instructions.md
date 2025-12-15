# Project Context for GitHub Copilot

## Project Overview

This is a GenAI Hackathon project using Google ADK for agent development. Try to use only Agent Development Kit (ADK), Vertex AI and other Google Cloud services.

## Key Folders

- `context/`: For context purposes only contains ADK samples, docs etc.
- `app/`: Main application code
- `frontend/`: Frontend interface
- `app/sub_agents/`: Sub-agent implementations
- `deployment/`: Terraform infrastructure
- `tests/`: Test suites

## Coding Standards

- Use Python type hints
- Follow Google Python style guide
- Add logging at each major step
- Use environment variables for configuration

## Architecture

- Main agent: `app/agent.py`
- Sub-agents communicate through session state

Do not create any summary markdown files unless explicitly instructed.
