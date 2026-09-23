'use client';

import React, { useRef, useEffect, useState } from 'react';

interface CameraPreviewProps {
  onVideoReady: (videoElement: HTMLVideoElement) => void;
  onCameraError: (error: string) => void;
  isActive: boolean;
}

export function CameraPreview({ onVideoReady, onCameraError, isActive }: CameraPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [permissionState, setPermissionState] = useState<'prompt' | 'granted' | 'denied'>('prompt');

  useEffect(() => {
    let stream: MediaStream | null = null;

    async function setupCamera() {
      if (!isActive) return;
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        onCameraError("Browser unsupported. Camera API not available.");
        return;
      }

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'user', // Prefer front camera
            width: { ideal: 640 },
            height: { ideal: 480 }
          }
        });
        
        setPermissionState('granted');
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play();
            onVideoReady(videoRef.current!);
          };
        }
      } catch (err: any) {
        setPermissionState('denied');
        if (err.name === 'NotAllowedError') {
          onCameraError("Camera permission denied. Please allow camera access in your browser settings.");
        } else if (err.name === 'NotFoundError') {
          onCameraError("No camera found on this device.");
        } else {
          onCameraError(`Camera error: ${err.message || err.name}`);
        }
      }
    }

    if (isActive) {
      setupCamera();
    }

    return () => {
      // Cleanup stream on unmount or when inactive
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, [isActive, onVideoReady, onCameraError]);

  return (
    <div className="relative w-full max-w-2xl mx-auto aspect-video bg-gray-900 rounded-lg overflow-hidden flex items-center justify-center">
      {isActive ? (
        <>
          <video
            ref={videoRef}
            className="absolute top-0 left-0 w-full h-full object-cover transform scale-x-[-1]"
            playsInline
            muted
          />
          {permissionState === 'prompt' && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
              <p className="text-white">Requesting camera access...</p>
            </div>
          )}
          {permissionState === 'denied' && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/90 z-10 p-6 text-center">
              <svg className="w-12 h-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-white font-medium">Camera Access Required</p>
              <p className="text-gray-400 text-sm mt-2">Please enable camera permissions in your browser settings and refresh the page.</p>
            </div>
          )}
        </>
      ) : (
        <div className="text-gray-500 flex flex-col items-center">
          <svg className="w-16 h-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <p>Camera is currently off</p>
        </div>
      )}
    </div>
  );
}
