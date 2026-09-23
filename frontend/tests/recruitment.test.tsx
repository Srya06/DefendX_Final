import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import RecruitmentPage from '../src/app/(dashboard)/recruitment/page';
import * as AuthContextModule from '../src/context/AuthContext';

// Mock useAuth
vi.mock('../src/context/AuthContext', () => ({
  useAuth: () => ({
    user: { user_id: 'user1', role: 'CANDIDATE' },
  }),
}));

const mockForces = [
  { id: '1', name: 'Indian Army' },
  { id: '2', name: 'Indian Navy' },
  { id: '3', name: 'Police' }
];

const mockNotifications = [
  { id: 'n1', category_id: 'c1', title: 'Navy SSR 2026', status: 'ACTIVE' }
];

const mockDetails = {
  id: 'n1',
  title: 'Navy SSR 2026',
  physical_standards: [
    {
      id: 'ps1',
      text_content: 'Height 157cm',
      document_id: 'doc-navy-123',
      page_number: 14,
      source_url: 'https://joinindiannavy.gov.in/official.pdf'
    }
  ],
  eligibility_requirements: [],
  medical_standards: []
};

describe('Recruitment Intelligence Page', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  it('renders page and force selector', async () => {
    // 1. fetch forces
    // 2. fetch profile
    // 3. fetch notifications (after force defaults to Indian Army)
    (global.fetch as any)
      .mockResolvedValueOnce({ ok: true, json: async () => mockForces }) // forces
      .mockResolvedValueOnce({ ok: true, json: async () => ({ target_force: 'Indian Navy' }) }) // profile
      .mockResolvedValueOnce({ ok: true, json: async () => mockNotifications }); // notifications for Indian Navy

    render(<RecruitmentPage />);

    expect(screen.getByText('Loading...')).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText('Recruitment Intelligence')).toBeDefined();
    });

    // Check force selector has loaded
    const select = screen.getByRole('combobox');
    expect(select).toBeDefined();
    expect((select as HTMLSelectElement).value).toBe('Indian Navy'); // Defaulted from profile
  });

  it('renders notifications list and empty state for details', async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({ ok: true, json: async () => mockForces })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ target_force: 'Indian Navy' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => mockNotifications });

    render(<RecruitmentPage />);

    await waitFor(() => {
      expect(screen.getByText('Navy SSR 2026')).toBeDefined();
      expect(screen.getByText('Select a notification to view intelligence')).toBeDefined();
    });
  });

  it('renders notification details and provenance when selected', async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({ ok: true, json: async () => mockForces })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ target_force: 'Indian Navy' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => mockNotifications })
      .mockResolvedValueOnce({ ok: true, json: async () => mockDetails }); // Details fetch

    render(<RecruitmentPage />);

    await waitFor(() => {
      expect(screen.getByText('Navy SSR 2026')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Navy SSR 2026'));

    await waitFor(() => {
      expect(screen.getByText('Height 157cm')).toBeDefined();
      // Provenance UI checks
      expect(screen.getByText('Official Source')).toBeDefined();
      expect(screen.getByText('Document ID: doc-navy-123')).toBeDefined();
      expect(screen.getByText('Page: 14')).toBeDefined();
      expect(screen.getByText('[View Source]')).toBeDefined();
    });
  });
});
