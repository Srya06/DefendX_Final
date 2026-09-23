'use client';

import React, { useRef, useEffect, useState } from 'react';
import { FilesetResolver, PoseLandmarker, DrawingUtils } from '@mediapipe/tasks-vision';
import { PushupDetector } from '@/lib/fitness/pushup';
import { SquatDetector } from '@/lib/fitness/squat';
import { ExerciseType, FitnessMetrics } from '@/lib/fitness/types';

interface PoseOverlayProps {
  videoElement: HTMLVideoElement | null;
  exerciseType: ExerciseType;
  isActive: boolean;
  onMetricsUpdate: (metrics: FitnessMetrics) => void;
}

export function PoseOverlay({ videoElement, exerciseType, isActive, onMetricsUpdate }: PoseOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isModelLoading, setIsModelLoading] = useState(true);
  const [modelError, setModelError] = useState<string | null>(null);
  
  const landmarkerRef = useRef<PoseLandmarker | null>(null);
  const reqFrameRef = useRef<number>(0);
  const lastVideoTimeRef = useRef<number>(-1);
  
  const pushupDetector = useRef(new PushupDetector());
  const squatDetector = useRef(new SquatDetector());

  useEffect(() => {
    // Reset state machines on exercise change
    pushupDetector.current = new PushupDetector();
    squatDetector.current = new SquatDetector();
  }, [exerciseType]);

  useEffect(() => {
    let active = true;

    async function initModel() {
      try {
        setIsModelLoading(true);
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        
        const landmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: "/models/pose_landmarker_lite.task",
            delegate: "GPU"
          },
          runningMode: "VIDEO",
          numPoses: 1
        });
        
        if (active) {
          landmarkerRef.current = landmarker;
          setIsModelLoading(false);
        }
      } catch (err: any) {
        if (active) {
          console.error("Failed to load PoseLandmarker:", err);
          setModelError("Failed to load AI model. Please try refreshing.");
          setIsModelLoading(false);
        }
      }
    }
    
    initModel();
    
    return () => {
      active = false;
      if (landmarkerRef.current) {
        landmarkerRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!isActive || !videoElement || !landmarkerRef.current || !canvasRef.current || isModelLoading) {
      if (reqFrameRef.current) {
        cancelAnimationFrame(reqFrameRef.current);
      }
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const drawingUtils = new DrawingUtils(ctx);

    const predict = async () => {
      if (videoElement.readyState >= 2 && videoElement.currentTime !== lastVideoTimeRef.current) {
        lastVideoTimeRef.current = videoElement.currentTime;
        
        // Sync canvas size to video aspect ratio
        if (canvas.width !== videoElement.videoWidth || canvas.height !== videoElement.videoHeight) {
          canvas.width = videoElement.videoWidth;
          canvas.height = videoElement.videoHeight;
        }

        const startTimeMs = performance.now();
        const results = landmarkerRef.current!.detectForVideo(videoElement, startTimeMs);

        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (results.landmarks && results.landmarks.length > 0) {
          const landmarks = results.landmarks[0];
          
          // Draw skeleton
          drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS, {
            color: '#00FF00', lineWidth: 4
          });
          drawingUtils.drawLandmarks(landmarks, {
            color: '#FF0000', lineWidth: 2, radius: 4
          });

          // Run exercise logic
          let metrics: FitnessMetrics;
          if (exerciseType === 'pushups') {
            metrics = pushupDetector.current.detect(landmarks);
          } else {
            metrics = squatDetector.current.detect(landmarks);
          }
          onMetricsUpdate(metrics);
        } else {
          // No body detected
          const emptyMetrics: FitnessMetrics = {
            totalReps: exerciseType === 'pushups' ? pushupDetector.current['validReps'] + pushupDetector.current['invalidReps'] : squatDetector.current['validReps'] + squatDetector.current['invalidReps'],
            validReps: exerciseType === 'pushups' ? pushupDetector.current['validReps'] : squatDetector.current['validReps'],
            invalidReps: exerciseType === 'pushups' ? pushupDetector.current['invalidReps'] : squatDetector.current['invalidReps'],
            currentState: 'READY',
            feedback: "No body detected",
            confidence: 0,
            formWarnings: []
          };
          onMetricsUpdate(emptyMetrics);
        }
        
        ctx.restore();
      }
      reqFrameRef.current = requestAnimationFrame(predict);
    };

    predict();

    return () => {
      if (reqFrameRef.current) {
        cancelAnimationFrame(reqFrameRef.current);
      }
    };
  }, [isActive, videoElement, isModelLoading, exerciseType, onMetricsUpdate]);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full object-cover pointer-events-none transform scale-x-[-1]"
      />
      {isModelLoading && isActive && (
        <div className="absolute top-4 right-4 bg-gray-900/80 px-3 py-1 rounded text-sm text-white">
          Loading AI Model...
        </div>
      )}
      {modelError && isActive && (
        <div className="absolute top-4 right-4 bg-red-900/80 px-3 py-1 rounded text-sm text-white">
          {modelError}
        </div>
      )}
    </>
  );
}
