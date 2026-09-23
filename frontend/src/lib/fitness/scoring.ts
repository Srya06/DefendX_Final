/**
 * Calculates a deterministic form score out of 100.
 */
export function calculateFormScore(validReps: number, invalidReps: number, warningsCount: number, averageConfidence: number): number {
  if (validReps + invalidReps === 0) return 0;
  
  const totalReps = validReps + invalidReps;
  const repRatio = validReps / totalReps; // 0.0 to 1.0
  
  // Start with rep ratio contributing 70 points
  let score = repRatio * 70;
  
  // Add confidence score contributing 30 points
  score += averageConfidence * 30;
  
  // Deduct points for warnings
  score -= (warningsCount * 5);
  
  return Math.max(0, Math.min(100, Math.round(score)));
}
