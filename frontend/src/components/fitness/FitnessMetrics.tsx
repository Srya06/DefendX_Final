'use client';

import React from 'react';
import { FitnessMetrics } from '@/lib/fitness/types';

interface FitnessMetricsProps {
  metrics: FitnessMetrics | null;
  isActive: boolean;
}

export function FitnessMetricsCard({ metrics, isActive }: FitnessMetricsProps) {
  if (!isActive) return null;

  const validReps = metrics?.validReps || 0;
  const feedback = metrics?.feedback || "Waiting...";
  const state = metrics?.currentState || "READY";
  const confidence = metrics?.confidence || 0;
  const warnings = metrics?.formWarnings || [];

  return (
    <div className="w-full max-w-2xl mx-auto mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Rep Counter */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Valid Reps</h3>
        <div className="text-6xl font-black text-indigo-600">{validReps}</div>
      </div>

      {/* State & Feedback */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between md:col-span-2 text-center md:text-left">
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Live Feedback</h3>
          <p className="text-2xl font-bold text-gray-800">{feedback}</p>
        </div>
        
        <div className="mt-4 flex flex-col sm:flex-row justify-between items-center text-sm gap-2">
          <div className="flex items-center">
            <span className="font-medium text-gray-600 mr-2">State:</span>
            <span className={`px-2 py-1 rounded font-bold ${state === 'DOWN' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}`}>
              {state}
            </span>
          </div>
          
          <div className="flex items-center">
             <span className="font-medium text-gray-600 mr-2">Confidence:</span>
             <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
               <div 
                 className={`h-full ${confidence > 0.7 ? 'bg-green-500' : confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'}`}
                 style={{ width: `${Math.round(confidence * 100)}%` }}
               />
             </div>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl md:col-span-3">
          <h4 className="text-sm font-bold text-yellow-800 mb-2 flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Form Adjustments
          </h4>
          <ul className="list-disc pl-5 text-sm text-yellow-700 space-y-1">
            {warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
