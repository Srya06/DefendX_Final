'use client';

import React, { useState, useEffect } from 'react';
import { CameraPreview } from '@/components/fitness/CameraPreview';
import { PoseOverlay } from '@/components/fitness/PoseOverlay';
import { FitnessMetricsCard } from '@/components/fitness/FitnessMetrics';
import { FitnessResultCard } from '@/components/fitness/FitnessResult';
import { ExerciseType, FitnessMetrics, AssessmentResult } from '@/lib/fitness/types';
import { calculateFormScore } from '@/lib/fitness/scoring';
import { useRouter } from 'next/navigation';

export default function FitnessAssessmentPage() {
  const router = useRouter();
  const [exercise, setExercise] = useState<ExerciseType>('pushups');
  const [isActive, setIsActive] = useState(false);
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  
  const [metrics, setMetrics] = useState<FitnessMetrics | null>(null);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  
  const [sessionStartTime, setSessionStartTime] = useState<number>(0);
  
  // Confidences tracking
  const [confidences, setConfidences] = useState<number[]>([]);

  const handleStart = () => {
    setResult(null);
    setMetrics(null);
    setConfidences([]);
    setCameraError(null);
    setIsActive(true);
    setSessionStartTime(Date.now());
  };

  const handleStop = () => {
    setIsActive(false);
    
    if (metrics) {
      const duration = Math.round((Date.now() - sessionStartTime) / 1000);
      const avgConf = confidences.length ? confidences.reduce((a, b) => a + b, 0) / confidences.length : 0;
      
      const score = calculateFormScore(metrics.validReps, metrics.invalidReps, metrics.formWarnings.length, avgConf);
      
      setResult({
        id: crypto.randomUUID(), // Temp ID, backend handles actual ID
        exercise_type: exercise,
        started_at: new Date(sessionStartTime).toISOString(),
        completed_at: new Date().toISOString(),
        duration_seconds: duration,
        total_reps: metrics.totalReps,
        valid_reps: metrics.validReps,
        invalid_reps: metrics.invalidReps,
        average_confidence: Math.round(avgConf * 100) / 100,
        form_score: score,
        form_warnings: metrics.formWarnings.join(', ') || null
      });
    }
  };

  const handleMetricsUpdate = (newMetrics: FitnessMetrics) => {
    setMetrics(newMetrics);
    setConfidences(prev => {
      // Keep only last 100 confidences to avoid memory leaks
      const next = [...prev, newMetrics.confidence];
      if (next.length > 100) next.shift();
      return next;
    });
  };

  const handleSaveResult = async () => {
    if (!result) return;
    setIsSaving(true);
    
    try {
      // Get session
      const authCookie = document.cookie.split('; ').find(row => row.startsWith('defendx_session='));
      const token = authCookie ? authCookie.split('=')[1] : null;

      if (!token) {
        alert("Not authenticated. Please log in.");
        router.push('/login');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/fitness/assessments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Usually we rely on cookies, but backend tests might use token
        },
        body: JSON.stringify({
          ...result,
          id: crypto.randomUUID() // Ensure valid UUID
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to save result");
      }
      
      // Mark as saved
      setResult({ ...result, id: 'saved' });
    } catch (err) {
      console.error(err);
      alert("Error saving result.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Live Fitness Assessment</h1>
        <p className="mt-2 text-sm text-gray-500">
          Camera processing is performed locally in your browser. DEFEND-X does not upload continuous video.
        </p>
      </div>

      {cameraError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {cameraError}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4 mb-6 justify-center items-center">
        <select 
          disabled={isActive}
          value={exercise}
          onChange={(e) => setExercise(e.target.value as ExerciseType)}
          className="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 p-2.5 disabled:opacity-50"
        >
          <option value="pushups">Push-ups</option>
          <option value="squats">Squats</option>
        </select>

        {!isActive ? (
          <button 
            onClick={handleStart}
            className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition"
          >
            Start Assessment
          </button>
        ) : (
          <button 
            onClick={handleStop}
            className="px-6 py-2.5 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition"
          >
            Stop Assessment
          </button>
        )}
      </div>

      <div className="relative">
        <CameraPreview 
          isActive={isActive} 
          onVideoReady={setVideoElement} 
          onCameraError={setCameraError} 
        />
        
        <PoseOverlay 
          isActive={isActive}
          videoElement={videoElement}
          exerciseType={exercise}
          onMetricsUpdate={handleMetricsUpdate}
        />
      </div>

      <FitnessMetricsCard metrics={metrics} isActive={isActive} />

      {!isActive && result && (
        <FitnessResultCard 
          result={result} 
          onSave={handleSaveResult} 
          isSaving={isSaving} 
        />
      )}
    </div>
  );
}
