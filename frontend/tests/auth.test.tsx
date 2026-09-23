import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import LoginPage from '../src/app/login/page';
import ChangePasswordPage from '../src/app/change-password/page';
import AccountPage from '../src/app/(dashboard)/account/page';
import { AuthProvider } from '../src/context/AuthContext';

// Mock useRouter and usePathname
const pushMock = vi.fn();
const mockRouter = { push: pushMock };
vi.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
  usePathname: () => '/account',
}));

describe('Frontend Authentication Flow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  // 1. Login form renders
  it('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByText('DEFEND-X LOGIN')).toBeDefined();
    expect(screen.getByLabelText(/User ID/i)).toBeDefined();
  });

  // 2. Empty credentials rejected client-side (implicit by required attributes on inputs)
  it('requires inputs', () => {
    render(<LoginPage />);
    const idInput = screen.getByLabelText(/User ID/i) as HTMLInputElement;
    const passInput = screen.getByLabelText(/Password/i) as HTMLInputElement;
    expect(idInput.required).toBe(true);
    expect(passInput.required).toBe(true);
  });

  // 3. Successful normal login redirects to candidate dashboard placeholder (/profile/account)
  it('redirects to account on normal login', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok', must_change_password: false }),
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/User ID/i), { target: { value: 'user1' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'pass' } });
    fireEvent.click(screen.getByRole('button', { name: /LOGIN/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith('/profile/account');
    });
  });

  // 4. Successful temporary-password login redirects to /change-password
  it('redirects to change-password if required', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok', must_change_password: true }),
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/User ID/i), { target: { value: 'user1' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'temp' } });
    fireEvent.click(screen.getByRole('button', { name: /LOGIN/i }));

    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith('/change-password');
    });
  });

  // 5. Invalid login displays an appropriate generic error
  it('shows error on invalid login', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid username or password' }),
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText(/User ID/i), { target: { value: 'user1' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: /LOGIN/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeDefined();
    });
  });

  // 6. Change-password form renders
  it('renders change password form', () => {
    render(<ChangePasswordPage />);
    expect(screen.getByText('MANDATORY PASSWORD CHANGE')).toBeDefined();
  });

  // 7. Successful password change redirects appropriately
  it('redirects after successful password change', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' }),
    });

    render(<ChangePasswordPage />);
    fireEvent.change(screen.getByLabelText(/Current Temporary Password/i), { target: { value: 'old' } });
    fireEvent.change(screen.getByLabelText(/New Password/i), { target: { value: 'newpass123' } });
    fireEvent.click(screen.getByRole('button', { name: /CHANGE PASSWORD/i }));

    await waitFor(() => {
      expect(screen.getByText(/Password updated successfully/i)).toBeDefined();
    });
  });

  // 8. Password mismatch is handled (backend throws 400)
  it('shows error if password change fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Incorrect current password' }),
    });

    render(<ChangePasswordPage />);
    fireEvent.change(screen.getByLabelText(/Current Temporary Password/i), { target: { value: 'wrong' } });
    fireEvent.change(screen.getByLabelText(/New Password/i), { target: { value: 'newpass123' } });
    fireEvent.click(screen.getByRole('button', { name: /CHANGE PASSWORD/i }));

    await waitFor(() => {
      expect(screen.getByText('Incorrect current password')).toBeDefined();
    });
  });

  // 9. Account settings page renders
  it('renders account settings page and fetches profile', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user_id: 'user1', role: 'CANDIDATE', must_change_password: false }),
    });

    render(
      <AuthProvider>
        <AccountPage />
      </AuthProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('user1')).toBeDefined();
      expect(screen.getByText('CANDIDATE')).toBeDefined();
    });
  });

  // 10. Username change request is sent correctly
  it('sends username change request', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user_id: 'user1', role: 'CANDIDATE', must_change_password: false }),
    });

    render(
      <AuthProvider>
        <AccountPage />
      </AuthProvider>
    );
    await waitFor(() => screen.getByText('user1'));

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ new_username: 'new_user1' }),
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user_id: 'new_user1', role: 'CANDIDATE', must_change_password: false }),
    });

    fireEvent.change(screen.getByLabelText(/New User ID/i), { target: { value: 'new_user1' } });
    fireEvent.click(screen.getByRole('button', { name: /Update ID/i }));

    await waitFor(() => {
      expect(screen.getByText(/User ID updated successfully/i)).toBeDefined();
      expect(screen.getByText('new_user1')).toBeDefined();
    });
  });

});
