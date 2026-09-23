# PWA Architecture

## Overview
DEFEND-X is designed as a Progressive Web Application (PWA). The single Next.js application will serve all supported platforms:
- Desktop / Laptop browsers
- Android phones and tablets
- iPhones and iPads

## Core Requirements

### Manifest and Service Worker
- A standard Web App Manifest (`manifest.json`) will define the app name, icons, and display mode (standalone).
- A Service Worker will provide caching strategies (e.g., Cache First for static assets, Network First for API calls) and enable an offline-friendly app shell.

### Responsive UI
- The UI uses Tailwind CSS and a mobile-first approach.
- The interface will emulate a serious intelligence/command-center application, maintaining usability across small screens (phones) and large screens (desktops).

### Hardware Access
- **Camera API**: The application will request `getUserMedia()` for live fitness assessments.
- **HTTPS Requirement**: Camera access requires a secure context (HTTPS) in production and staging environments.

### Deployment Boundary
- The Next.js frontend will be deployed on Vercel.
- It will communicate exclusively with the external Python backend API.
