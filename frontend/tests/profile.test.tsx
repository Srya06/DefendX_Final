import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ProfilePage from '../src/app/(dashboard)/profile/page';
import * as AuthContextModule from '../src/context/AuthContext';

// Mock useAuth
vi.mock('../src/context/AuthContext', () => ({
  useAuth: () => ({
    user: { user_id: 'user1', role: 'CANDIDATE' },
  }),
}));

describe('Profile Page', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  it('fetches and renders profile data', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ full_name: 'John Doe', target_force: 'Indian Navy' }),
    });

    render(<ProfilePage />);

    // Wait for fetch to complete and UI to update
    await waitFor(() => {
      expect((screen.getByLabelText(/Full Name/i) as HTMLInputElement).value).toBe('John Doe');
      expect((screen.getByLabelText(/Target Force/i) as HTMLSelectElement).value).toBe('Indian Navy');
    });
  });

  it('updates profile and shows success message', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ full_name: 'John', target_force: '' }),
    });

    render(<ProfilePage />);
    
    await waitFor(() => {
      expect((screen.getByLabelText(/Full Name/i) as HTMLInputElement).value).toBe('John');
    });

    // Mock successful update
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'John Smith' } });
    fireEvent.change(screen.getByLabelText(/Target Force/i), { target: { value: 'Indian Army' } });
    
    fireEvent.click(screen.getByRole('button', { name: /Save Profile/i }));

    await waitFor(() => {
      expect(screen.getByText(/Profile updated successfully/i)).toBeDefined();
    });
  });

  it('shows error message if profile update fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ full_name: 'John', target_force: '' }),
    });

    render(<ProfilePage />);
    
    await waitFor(() => {
      expect((screen.getByLabelText(/Full Name/i) as HTMLInputElement).value).toBe('John');
    });

    // Mock failed update
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Validation Error' }),
    });

    fireEvent.click(screen.getByRole('button', { name: /Save Profile/i }));

    await waitFor(() => {
      expect(screen.getByText(/Failed to update profile/i)).toBeDefined();
    });
  });
});
