import { Point3D } from './types';

/**
 * Calculates the angle formed by three points (A, B, C) with B as the vertex.
 * Returns the angle in degrees (0 to 180).
 */
export function calculateAngle(a: Point3D, b: Point3D, c: Point3D): number {
  if (!a || !b || !c) return 0;
  
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs((radians * 180.0) / Math.PI);
  
  if (angle > 180.0) {
    angle = 360.0 - angle;
  }
  
  return angle;
}

/**
 * Checks if a set of landmarks are all visible above a given threshold.
 */
export function areLandmarksVisible(landmarks: Point3D[], threshold = 0.5): boolean {
  return landmarks.every(lm => lm && lm.visibility >= threshold);
}
