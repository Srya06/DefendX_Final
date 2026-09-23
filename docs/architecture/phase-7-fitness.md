# Phase 7: Live Computer Vision Fitness Assessment

## Architecture Overview

DEFEND-X implements a completely client-side browser-based computer vision assessment system. To ensure absolute privacy and reduce backend costs, NO raw video is uploaded or stored.

### Pipeline Workflow

1. **Camera**: The frontend uses `navigator.mediaDevices.getUserMedia()` to capture live video from the candidate's active device (mobile or desktop).
2. **Pose**: `@mediapipe/tasks-vision` processes the video frames locally using `requestAnimationFrame` drawing onto a hidden/overlay `<canvas>`.
3. **Landmarks**: The `PoseLandmarker` extracts 33 3D body landmarks.
4. **Angles**: Custom geometry utilities (`src/lib/fitness/geometry.ts`) calculate required angles (e.g., shoulder-elbow-wrist, hip-knee-ankle).
5. **State Machine**: Deterministic state machines track `READY -> DOWN -> UP` states. They require proper threshold transitions to prevent false positives and noise.
6. **Rep Counting**: Reps only increment on a valid `DOWN -> UP` transition within required angle parameters.
7. **Form Analysis**: Warnings are generated (e.g. "Go deeper") based on landmark coordinates. A live confidence score ensures the candidate is in view.
8. **Fitness Result**: An assessment is summarized, producing a deterministic 0-100 form score.
9. **Backend Persistence**: ONLY the derived textual and numerical metrics are sent to `POST /api/v1/fitness/assessments`. The backend validates the metrics and stores them securely against the candidate's authenticated UUID.

### Clear Distinctions

- **Client-Side CV**: All camera and pose logic runs in the browser.
- **Backend Persistence**: The backend acts strictly as a secure storage engine for the derived results. It enforces data isolation between candidates.
- **Future DRI Integration**: (Phase 8) Will use these derived fitness scores as part of the Defense Readiness Index calculation.
