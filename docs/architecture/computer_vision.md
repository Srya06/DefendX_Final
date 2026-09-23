# Computer Vision (CV) Architecture

## Goal
To perform live fitness assessments using the candidate's device camera without requiring the upload of pre-recorded videos.

## Pipeline
The CV architecture follows a client-side to server-side pipeline:

1. **Device Camera**: Web API (`getUserMedia`) captures a live video stream within the PWA.
2. **Pose Detection**: A browser-compatible engine (e.g., MediaPipe Solutions) processes the video frames locally in the browser to extract body landmarks (e.g., shoulders, elbows, hips).
3. **Telemetry Extraction**: The frontend calculates joint angles and relative positions.
4. **State Machine**: An exercise-specific state machine (e.g., for push-ups or pull-ups) tracks the transition between "down" and "up" states.
5. **Rep Counting & Form Analysis**: Valid reps are counted, and form anomalies are detected locally.
6. **Telemetry Transmission**: Aggregated metrics and fitness results are transmitted to the backend API (`/api/v1/cv` and `/api/v1/fitness`).
7. **Candidate Metrics Update**: The backend stores the session and updates the candidate's Defense Readiness Index (DRI).

## Rationale
Running pose detection locally in the browser drastically reduces backend bandwidth and compute costs while preserving candidate privacy, as raw video frames are not transmitted.
