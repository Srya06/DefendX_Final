import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import DashboardPage from '../src/app/(dashboard)/dashboard/page';

describe('Dashboard empty states', () => {
  it('renders honest empty states for unimplemented modules', () => {
    render(<DashboardPage />);
    
    expect(screen.getByText('Recruitment Intelligence')).toBeDefined();
    expect(screen.getByText(/Recruitment intelligence will be connected in Phase 4/i)).toBeDefined();
    
    expect(screen.getByText('Academic Preparation')).toBeDefined();
    expect(screen.getByText(/Academic preparation will be connected in a later phase/i)).toBeDefined();
    
    expect(screen.getByText('Fitness Assessment')).toBeDefined();
    expect(screen.getByText(/Live camera fitness assessment will be connected in Phase 8/i)).toBeDefined();
    
    expect(screen.getByText('Readiness')).toBeDefined();
    expect(screen.getByText(/Defense Readiness Index will be calculated/i)).toBeDefined();
    
    expect(screen.getByText('AI Mentor')).toBeDefined();
    expect(screen.getByText(/Multi-agent intelligence will be connected in Phase 6/i)).toBeDefined();
  });
});
