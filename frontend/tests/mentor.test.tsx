import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MentorPage from '../src/app/mentor/page';
import { expect, test, vi, beforeEach } from 'vitest';


const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

test('submits query and displays loading state then results', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      request_id: 'test-req',
      response: 'This is the synthesized AI mentor response.',
      selected_agents: ['recruitment', 'synthesis'],
      evidence: [
        { text: 'Navy requires 157cm height.', source_url: 'http://test.com', page_start: 1 }
      ],
      execution_trace: [
        { agent: 'commander', status: 'completed' },
        { agent: 'recruitment', status: 'completed', tools_used: ['hybrid_retrieval'] },
        { agent: 'synthesis', status: 'completed' }
      ],
      warnings: []
    })
  });

  render(<MentorPage />);
  
  const input = screen.getByPlaceholderText(/Ask about Navy/i);
  fireEvent.change(input, { target: { value: 'Navy height?' } });
  
  const submitBtn = screen.getByText('Ask Mentor');
  fireEvent.click(submitBtn);
  
  expect(screen.getByText('Thinking...')).toBeDefined();
  
  await waitFor(() => {
    expect(screen.getByText('This is the synthesized AI mentor response.')).toBeDefined();
  });
  
  expect(screen.getByText('"Navy requires 157cm height."')).toBeDefined();
  expect(screen.getByText('commander')).toBeDefined();
  expect(screen.getByText('recruitment')).toBeDefined();
  expect(screen.getByText('synthesis')).toBeDefined();
});

test('displays error when API fails', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: false,
    json: async () => ({ detail: 'AGENT_EXECUTION_FAILED: OLLAMA_UNAVAILABLE' })
  });

  render(<MentorPage />);
  
  fireEvent.change(screen.getByPlaceholderText(/Ask about Navy/i), { target: { value: 'test' } });
  fireEvent.click(screen.getByText('Ask Mentor'));
  
  await waitFor(() => {
    expect(screen.getByText('AGENT_EXECUTION_FAILED: OLLAMA_UNAVAILABLE')).toBeDefined();
  });
});
