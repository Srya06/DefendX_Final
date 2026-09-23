export type ExerciseType = 'pushups' | 'squats';

export type ExerciseState = 'READY' | 'DOWN' | 'UP';

export interface Point3D {
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export interface FitnessMetrics {
  totalReps: number;
  validReps: number;
  invalidReps: number;
  currentState: ExerciseState;
  feedback: string;
  confidence: number;
  formWarnings: string[];
}

export interface AssessmentResult {
  id: string;
  exercise_type: string;
  started_at: string;
  completed_at: string;
  duration_seconds: number;
  total_reps: number;
  valid_reps: number;
  invalid_reps: number;
  average_confidence: number;
  form_score: number;
  form_warnings: string | null;
}
