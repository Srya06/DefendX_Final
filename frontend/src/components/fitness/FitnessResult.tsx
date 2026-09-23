'use client';

import React from 'react';
import { AssessmentResult } from '@/lib/fitness/types';

interface FitnessResultProps {
  result: AssessmentResult | null;
  onSave: () => void;
  isSaving: boolean;
}

export function FitnessResultCard({ result, onSave, isSaving }: FitnessResultProps) {
  if (!result) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="bg-indigo-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Assessment Complete</h2>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Exercise</div>
            <div className="font-bold text-gray-900 capitalize">{result.exercise_type}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Valid Reps</div>
            <div className="text-2xl font-black text-indigo-600">{result.valid_reps}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Duration</div>
            <div className="font-bold text-gray-900">{result.duration_seconds}s</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-500 mb-1">Form Score</div>
            <div className={`text-2xl font-black ${result.form_score >= 80 ? 'text-green-600' : result.form_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
              {result.form_score}
            </div>
          </div>
        </div>

        {result.form_warnings && (
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Areas for Improvement</h4>
            <p className="text-gray-600 text-sm bg-gray-50 p-3 rounded">{result.form_warnings}</p>
          </div>
        )}

        <div className="flex justify-end border-t border-gray-100 pt-4 mt-4">
          <button
            onClick={onSave}
            disabled={isSaving || result.id === 'saved'}
            className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? "Saving..." : result.id === 'saved' ? "Saved Successfully" : "Save Results to Profile"}
          </button>
        </div>
      </div>
    </div>
  );
}
