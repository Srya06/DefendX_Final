# AI Agent Architecture

## Overview
DEFEND-X employs a multi-agent system powered by **LangGraph** to process recruitment intelligence, guide academic preparation, and act as a personal mentor.

## Agent Roster
The conceptual agent roster includes:
- **CommanderAgent**: The central orchestrator routing requests.
- **RecruitmentAgent**: Analyzes target force requirements.
- **AcademicAgent**: Plans study schedules and mock tests.
- **FitnessAgent**: Reviews fitness session metrics.
- **MentorAgent**: Provides personalized guidance.
- **TranslationAgent**: Handles multilingual interaction.
- **SynthesisAgent**: Aggregates insights into the Defense Readiness Index (DRI).

## State Management
Agents communicate by reading from and writing to a shared, typed `AgentState` object within LangGraph.

## Provider Abstraction
The system is built on an LLM Provider Abstraction layer. 
- **Development**: Uses local models (e.g., Qwen2.5 via Ollama) to reduce costs and improve iteration speed. The backend must NOT assume Ollama will run in Vercel.
- **Production**: Uses a production LLM service (e.g., OpenAI, Anthropic, or hosted open-source models). The provider can be swapped via environment variables without altering the core agent logic.
