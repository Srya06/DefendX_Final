# DEFEND-X

Defense Recruitment & Readiness Intelligence Platform

## Architecture

This project is structured as a scalable, service-oriented ecosystem.

### Frontend
Built with Next.js, TypeScript, and Tailwind CSS. It functions as a Progressive Web App (PWA) allowing access across Desktop, Android, and iOS devices. The frontend handles the candidate journey and includes browser-compatible pose detection capabilities for live fitness assessments.

### Backend
Powered by Python and FastAPI. The backend uses a RESTful API architecture and interfaces with:
- PostgreSQL: For transactional data (users, profiles, roles).
- Neo4j: For the defense knowledge graph.

### AI Architecture
Built using LangGraph for multi-agent orchestration. The system uses an LLM provider abstraction, enabling local development with models like Qwen2.5 (via Ollama) while allowing a smooth transition to production LLM services without rewriting agent logic.

### Computer Vision (CV) Architecture
The frontend captures live video via the device camera, runs browser-compatible pose detection, and sends aggregated metrics to the backend. This enables real-time fitness evaluation without relying on pre-recorded video uploads.

## Environment Setup
Copy `.env.example` to `.env` and fill in the required variables for your local development environment.
