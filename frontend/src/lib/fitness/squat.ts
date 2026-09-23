import { Point3D, ExerciseState, FitnessMetrics } from './types';
import { calculateAngle, areLandmarksVisible } from './geometry';

const LEFT_HIP = 23;
const RIGHT_HIP = 24;
const LEFT_KNEE = 25;
const RIGHT_KNEE = 26;
const LEFT_ANKLE = 27;
const RIGHT_ANKLE = 28;

export class SquatDetector {
  private state: ExerciseState = 'READY';
  private validReps = 0;
  private invalidReps = 0;
  private feedback = "Get into squat position";
  private confidence = 0;
  private warnings: Set<string> = new Set();
  
  private readonly ANGLE_UP = 160; 
  private readonly ANGLE_DOWN = 90;

  detect(landmarks: Point3D[]): FitnessMetrics {
    if (!landmarks || landmarks.length === 0) {
      this.feedback = "No body detected";
      return this.getMetrics();
    }

    const leftVisible = areLandmarksVisible([landmarks[LEFT_HIP], landmarks[LEFT_KNEE], landmarks[LEFT_ANKLE]], 0.5);
    const rightVisible = areLandmarksVisible([landmarks[RIGHT_HIP], landmarks[RIGHT_KNEE], landmarks[RIGHT_ANKLE]], 0.5);
    
    if (!leftVisible && !rightVisible) {
      this.feedback = "Move back so your legs are visible.";
      this.confidence = 0;
      return this.getMetrics();
    }
    
    this.confidence = 1;
    
    let hip, knee, ankle;
    if (leftVisible) {
      hip = landmarks[LEFT_HIP];
      knee = landmarks[LEFT_KNEE];
      ankle = landmarks[LEFT_ANKLE];
    } else {
      hip = landmarks[RIGHT_HIP];
      knee = landmarks[RIGHT_KNEE];
      ankle = landmarks[RIGHT_ANKLE];
    }
    
    const kneeAngle = calculateAngle(hip, knee, ankle);

    // State Machine
    if (this.state === 'READY' || this.state === 'UP') {
      if (kneeAngle > this.ANGLE_UP) {
        this.state = 'UP';
        this.feedback = "Standing. Now squat down.";
      } else if (kneeAngle <= this.ANGLE_DOWN) {
        this.state = 'DOWN';
        this.feedback = "Good depth, stand up!";
      } else {
        this.feedback = "Go slightly deeper.";
      }
    } else if (this.state === 'DOWN') {
      if (kneeAngle > this.ANGLE_UP) {
        this.state = 'UP';
        this.validReps++;
        this.feedback = "Good squat!";
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
