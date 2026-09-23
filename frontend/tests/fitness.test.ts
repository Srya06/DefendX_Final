import { describe, it, expect } from 'vitest';
import { calculateAngle, areLandmarksVisible } from '../src/lib/fitness/geometry';

describe('Fitness Geometry', () => {
  it('calculates 90-degree angle correctly', () => {
    // Shoulder
    const a = { x: 0, y: 1, z: 0, visibility: 1 };
    // Elbow (vertex)
    const b = { x: 0, y: 0, z: 0, visibility: 1 };
    // Wrist
    const c = { x: 1, y: 0, z: 0, visibility: 1 };

    const angle = calculateAngle(a, b, c);
    expect(Math.round(angle)).toBe(90);
  });

  it('calculates 180-degree angle correctly', () => {
    // Shoulder
    const a = { x: -1, y: 0, z: 0, visibility: 1 };
    // Elbow (vertex)
    const b = { x: 0, y: 0, z: 0, visibility: 1 };
    // Wrist
    const c = { x: 1, y: 0, z: 0, visibility: 1 };

    const angle = calculateAngle(a, b, c);
    expect(Math.round(angle)).toBe(180);
  });

  it('handles missing landmarks', () => {
    const a = { x: 0, y: 1, z: 0, visibility: 1 };
    const b = { x: 0, y: 0, z: 0, visibility: 1 };
    
    // @ts-ignore
    const angle = calculateAngle(a, b, null);
    expect(angle).toBe(0);
  });

  it('checks visibility properly', () => {
    const landmarks = [
      { x: 0, y: 0, z: 0, visibility: 0.8 },
      { x: 0, y: 0, z: 0, visibility: 0.6 }
    ];
    
    expect(areLandmarksVisible(landmarks, 0.5)).toBe(true);
    expect(areLandmarksVisible(landmarks, 0.7)).toBe(false);
  });
});
