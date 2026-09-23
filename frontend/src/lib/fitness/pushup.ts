import { Point3D, ExerciseState, FitnessMetrics } from './types';
import { calculateAngle, areLandmarksVisible } from './geometry';

// MediaPipe Pose Landmark Indices
const LEFT_SHOULDER = 11;
const RIGHT_SHOULDER = 12;
const LEFT_ELBOW = 13;
const RIGHT_ELBOW = 14;
const LEFT_WRIST = 15;
const RIGHT_WRIST = 16;
const LEFT_HIP = 23;
const RIGHT_HIP = 24;

export class PushupDetector {
  private state: ExerciseState = 'READY';
  private validReps = 0;
  private invalidReps = 0;
  private feedback = "Get into pushup position";
  private confidence = 0;
  private warnings: Set<string> = new Set();
  
  // Thresholds
  private readonly ANGLE_UP = 150; // Arms straight
  private readonly ANGLE_DOWN = 90; // Arms bent

  detect(landmarks: Point3D[]): FitnessMetrics {
    if (!landmarks || landmarks.length === 0) {
      this.feedback = "No body detected";
      return this.getMetrics();
    }

    // Use the side that is more visible
    const leftVisible = areLandmarksVisible([landmarks[LEFT_SHOULDER], landmarks[LEFT_ELBOW], landmarks[LEFT_WRIST]], 0.5);
    const rightVisible = areLandmarksVisible([landmarks[RIGHT_SHOULDER], landmarks[RIGHT_ELBOW], landmarks[RIGHT_WRIST]], 0.5);
    
    if (!leftVisible && !rightVisible) {
      this.feedback = "Move into full view of the camera.";
      this.confidence = 0;
      return this.getMetrics();
    }
    
    this.confidence = 1;
    
    let shoulder, elbow, wrist, hip;
    if (leftVisible) {
      shoulder = landmarks[LEFT_SHOULDER];
      elbow = landmarks[LEFT_ELBOW];
      wrist = landmarks[LEFT_WRIST];
      hip = landmarks[LEFT_HIP];
    } else {
      shoulder = landmarks[RIGHT_SHOULDER];
      elbow = landmarks[RIGHT_ELBOW];
      wrist = landmarks[RIGHT_WRIST];
      hip = landmarks[RIGHT_HIP];
    }
    
    const elbowAngle = calculateAngle(shoulder, elbow, wrist);
    
    // Check body alignment (simple check: shoulder and hip should be somewhat aligned horizontally or in a plank line)
    // We won't strictly penalize yet, but we'll issue warnings
    if (hip && shoulder && Math.abs(hip.y - shoulder.y) > 0.3) {
      this.warnings.add("Keep your body straight");
    }

    // State Machine
    if (this.state === 'READY' || this.state === 'UP') {
      if (elbowAngle > this.ANGLE_UP) {
        this.state = 'UP';
        this.feedback = "Good form, now go down.";
      } else if (elbowAngle < this.ANGLE_DOWN) {
        this.state = 'DOWN';
        this.feedback = "Good depth, push up!";
      } else {
        this.feedback = "Lower your body further.";
      }
    } else if (this.state === 'DOWN') {
      if (elbowAngle > this.ANGLE_UP) {
        this.state = 'UP';
        this.validReps++;
        this.feedback = "Good rep!";
      } else if (elbowAngle > this.ANGLE_DOWN && elbowAngle < this.ANGLE_UP) {
        this.feedback = "Keep pushing up!";
      }
    }

    return this.getMetrics();
  }
  
  private getMetrics(): FitnessMetrics {
    return {
      totalReps: this.validReps + this.invalidReps,
      validReps: this.validReps,
      invalidReps: this.invalidReps,
      currentState: this.state,
      feedback: this.feedback,
      confidence: this.confidence,
      formWarnings: Array.from(this.warnings)
    };
  }
}
