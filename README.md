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

## Phase 7: Live Computer Vision Fitness Assessment

DEFEND-X includes a browser-based computer vision fitness tracker for push-ups and squats.

* **Camera Permissions**: The browser will request camera access upon clicking "Start Assessment". If denied, the user must manually re-enable it in browser settings.
* **Supported Workflow**: Go to Dashboard -> Fitness Assessment -> Select Exercise -> Start Camera -> Perform Exercise -> Stop -> Save Result.
* **Browser Requirements**: A modern browser (Chrome, Safari, Firefox, Edge) with WebRTC (getUserMedia) and WebAssembly support.
* **Local Development**: Run "npm run dev". Ensure the .task model is in "public/models/".
* **Privacy Behavior**: Video is processed 100% locally in the browser. DEFEND-X does not record, upload, or store raw video frames. Only mathematical metrics (rep counts, angles, scores) are saved.
* **Fitness API Endpoints**:
  * POST /api/v1/fitness/assessments: Save assessment.
  * GET /api/v1/fitness/assessments: Fetch own history.
* **Testing Instructions**:
  * "pytest tests/test_fitness.py" for backend API authorization.
  * "vitest run" for frontend geometry calculations.
* **Limitations**: 
  * Not an official military-standard assessment.
  * Heavily dependent on good lighting and camera placement.
  * Reps will not count if full body (for squats) or upper body (for pushups) isn't clearly visible to the AI model.
